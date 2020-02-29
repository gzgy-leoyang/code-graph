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
    name=""
    call_func_list = []
    def __init__(self,func_name):
        self.name = func_name

##############
## 
##############
class Src_file:
    src_file_name = ""
    func_list = []
    def __init__(self,file_name):
        self.src_file_name = file_name
    
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
    # 匹配函数定义
    rgl_def_func_name = r'''
    (((\s*)(static)(\s*)) | (\s*))  
    ((void)|(char)|(short)|(int)|(float)|(long)|(double)) # 识别函数返回值类型
    (\s*(\*)?\s*)                                                                             # 识别返回值是否为指针类型以及中间是否包含空格
    (\w+)                                                                                          # 识别函数名
    ((\s*)(\()(\n)?)                                                                         # 函数开始小括号
    ((\s*)?(const)?(\s*)?                                                             # 参数前是否有const
    ((void)|(char)|(short)|(int)|(float)|(long)|(double)) # 参数类型
    (\s*)(\*)?(\s*)?(restrict)?(\s*)?(\w+)(\s*)?(\,)?(\n)?(.*)?)*# 最后的*表示有多个参数
    ((\s*)(\))(\n)?)                                                                         # 函数结束小括号
    '''
    rgl_def_func_start = r'''
    (({)(\n)?)# 函数开始"{"
    '''
    rgl_def_func_end = r'''
    (})(\s*) # 函数结束"}"
    '''
    ## 匹配函数调用（多行）
    rgl_call_func = r'''
    ((\s*) (\w+)(\s*)(=))  # "空白字符(>=0)-单词字符(>1)-空格字符(>=0)-= " (0次或1次)
    ((\s*)((?!if|while|switch)\w+)(\s*)(\())# "空白字符(>=0)-单词字符(>1)-空格字符(>=0)-( " (0次或1次)识别函数名
    '''
    ## 匹配函数调用（无返回）
    rgl_call_void_func = r'''
    ((\s*)((?!if|while|switch)\w+)(\s*)(\())# "空白字符(>=0)-单词字符(>1)-空格字符(>=0)-( " (0次或1次)识别函数名
    '''
    file_path  = sys.path[0] +'/'+ src_file_name
    scan_func_step = 0
    def_func_obj = None
    with open( file_path ) as fd:
        def_func_patten_name = re.compile(rgl_def_func_name,re.X)
        def_func_patten_start = re.compile(rgl_def_func_start,re.X)
        call_func_patten = re.compile(rgl_call_func,re.X)
        call_void_func_patten = re.compile(rgl_call_void_func,re.X)
        def_func_patten_end = re.compile(rgl_def_func_end,re.X)

        src_file = Src_file( src_file_name )
        for line in fd:
            if scan_func_step == 0 :
                if def_func_patten_name.match( line ):
                    scan_func_step = 1
                    n = get_func_name( line )
                    def_func_obj = Function( n )
                    src_file.func_list.append( def_func_obj )
                    print( "DEF: ",n,def_func_obj )
            elif scan_func_step==1:
                if def_func_patten_start.match( line ):
                    scan_func_step = 2
                    print( ">>")
            elif scan_func_step==2:
                if call_func_patten.match( line ):
                    n = get_func_name( line )
                    if def_func_obj != None:
                        f = Function( n )
                        def_func_obj.call_func_list.append( f )
                        print("+",def_func_obj,n,f)
                elif call_void_func_patten.match( line ):
                    n =  get_void_func_name( line )
                    if def_func_obj != None:
                        f = Function( n )
                        def_func_obj.call_func_list.append( f )
                        print("+",def_func_obj,n,f)
                elif def_func_patten_end.match( line ):
                    scan_func_step = 0
                    def_func_obj = None
                    print( "<<")
    return src_file

#################
def main():
    src_file_obj = parse_file( "can_service.c" )    
    for f in src_file_obj.def_func_list:
        print("*",f,f.name)
        for ff in f.call_func_list :
            print("**",ff.name)
    return 

#########
if __name__ == "__main__":
    main()