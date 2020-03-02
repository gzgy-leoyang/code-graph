#!/usr/bin/python3
#!/usr/bin/env python3

import os
import re
import sys
import getopt
import readline

import string

##############
##
##############
class Function:
    def __init__(self,func_name):
        self.name = func_name
        self.call_func_list=[]
        self.start_line = 0
        self.end_line = 0
        self.parent_src_file = ""

##############
## 
##############
class Src_file:
    def __init__(self,file_name):
        self.src_file_name = file_name
        self.func_list = []

top_func = None
src_file_list=[]
all_def_func_list = []

###########################
def get_func_name(ll ):
    str_list = re.findall(r"(.+?)\(", ll)  # 提取"("之前的字符
    list  = str_list[0].split(' ')
    if list.__len__() == 1 :
        name = list[0].strip()
    else:
        name = list[list.__len__()-1].strip()
    return name

#############################
def get_void_func_name(ll ):
    str_list = re.findall(r"(.+?)\(", ll)  # 提取"("之前的字符
    return  str_list[0].strip()

#############################
def parse_file(  src_file_name ):
    global top_func
    global all_def_func_list
    # 函数头，类型1，花括号与函数名不同行
    rgl_def_func_name = r'''
    (((\s*)(static)(\s*)) | (\s*))  
    ((void)|(char)|(short)|(int)|(float)|(long)|(double)) # 识别函数返回值类型
    (\s*(\*)?\s*)                                                                             # 识别返回值是否为指针类型以及中间是否包含空格
    (\w+)                                                                                          # 识别函数名
    ((\s*)(\()(\n)?)                                                                         # 函数开始小括号
    ((\s*)?(const)?(\s*)?                                                             # 参数前是否有const
    ((void)|(char)|(short)|(int)|(float)|(long)|(double)) # 参数类型
    (\s*)(\*)?(\s*)?(restrict)?(\s*)?(\w+)(\s*)?(\,)?(\n)?(.*)?)*# 最后的*表示有多个参数
    (((\s*)(\))(\s*)){1})                                                                         # 函数结束小括号
    '''

    rgl_def_func_end = r'''
    (})(\s*) # 函数结束"}"
    '''
    ## 匹配函数调用（多行）
    rgl_call_func = r'''
    ((\s*) (\w+)(\s*)(=))  # "空白字符(>=0)-单词字符(>1)-空格字符(>=0)-= " (0次或1次)
    ((\s*)((?!if|while|switch|for)\w+)(\s*)(\())# "空白字符(>=0)-单词字符(>1)-空格字符(>=0)-( " (0次或1次)识别函数名
    '''
    ## 匹配函数调用（无返回）
    rgl_call_void_func = r'''
    ((\s*)((?!if|while|switch|for)\w+)(\s*)(\())# "空白字符(>=0)-单词字符(>1)-空格字符(>=0)-( " (0次或1次)识别函数名
    '''
    # file_path  = sys.path[0] +'/'+ src_file_name
    file_path  = src_file_name

    scan_func_step = 0
    current_line = 0
    def_func = None
    with open( file_path ) as fd:
        # 函数头
        def_func_patten_name = re.compile(rgl_def_func_name,re.X)
        # 调用函数
        ## 类型1，有返回参数
        call_func_patten = re.compile(rgl_call_func,re.X)
        ## 类型2，无参数返回
        call_void_func_patten = re.compile(rgl_call_void_func,re.X) 
        # 函数尾
        def_func_patten_end = re.compile(rgl_def_func_end,re.X)

        # print ( "\n< %s >" %src_file_name )
        src_file = Src_file( src_file_name )
        src_file_list.append(src_file)
        for line in fd:
            current_line += 1
            if scan_func_step == 0 :
                if def_func_patten_name.match( line ):
                    scan_func_step = 1
                    n = get_func_name( line )
                    
                    def_func = Function( n )
                    def_func.start_line = current_line
                    def_func.parent_src_file = src_file_name
                    all_def_func_list.append( def_func )
                    if n == "main":
                        top_func = def_func
                    src_file.func_list.append( def_func )
            elif scan_func_step==1:
                if call_func_patten.match( line ):
                    n = get_func_name( line )
                    re_call_counter  = 0
                    for fx in def_func.call_func_list :
                        if fx.name == n :
                            re_call_counter += 1

                    if re_call_counter == 0 :
                        f = Function( n )
                        def_func.call_func_list.append( f )
                elif call_void_func_patten.match( line ):
                    n =  get_void_func_name( line )
                    re_call_counter  = 0
                    for fx in def_func.call_func_list :
                        if fx.name == n :
                            re_call_counter += 1
                    if re_call_counter == 0 :
                        f = Function( n )
                        def_func.call_func_list.append( f )
                elif def_func_patten_end.match( line ):
                    scan_func_step = 0
                    def_func.end_line = current_line
                    def_func = None
        
    # for f in src_file.func_list:
    #     print("** %s (%s : %i-%i )"%( f.name, f.parent_src_file, f.start_line, f.end_line ) )
    #     for ff in f.call_func_list :
    #         print("     |---",ff.name)
    return src_file


def get_filelist(dir):
    Filelist = []
    for home, dirs, files in os.walk( dir ):
        for filename in files:
            if filename.endswith(".c") :
                Filelist.append(os.path.join(home, filename))
    return Filelist

####################################
def get_func_obj_by_name( func_name ):
    func_obj = None
    for f in all_def_func_list :
        if func_name == f.name :
            return f
    return None

    
#################
layer_counter = 0
def function_tree ( f ):
    global layer_counter 
    if f.call_func_list.__len__() != 0 :
        layer_counter += 1
        for call_f in f.call_func_list:
            print ("    "*layer_counter,end="")
            print ("|-",call_f.name )
            func_obj = get_func_obj_by_name( call_f.name )
            if func_obj != None:
                function_tree ( func_obj )  
        layer_counter -= 1
        return        
    else :
        return None

def main():
    global top_func
    file_list = get_filelist( sys.path[0]+"/src" )
    for f in file_list:
        src_file_obj = parse_file( f ) 
    
    print ( "[ROOT]",top_func.name)
    function_tree ( top_func )  
    return 

    # src_file_obj = parse_file( sys.path[0]+"/can_service.c" )
#########
if __name__ == "__main__":
    main()