#!/usr/bin/python3
#!/usr/bin/env python3

import os
import re
import sys
import getopt
import readline

import string

## 绘图
# import networkx as nx
# import matplotlib.pyplot as plt

##############
##
##############
class Function:
    def __init__(self,func_name):
        self.name = func_name
        self.called_func_name_list=[]
        self.call_func_name_list=[]
        self.start_line = 0
        self.end_line = 0
        self.parent_src_file = ""
        self.called = 0
        self.calling = 0 

##############
## 
##############
class Src_file:
    def __init__(self,file_name):
        self.src_file_name = file_name
        self.func_list = []

class Code_graph:
    def __init__(self):
        self.src_file_list = []
        self.all_func_list = []
#############
## 文件列表
src_file_list=[]

#############
## 所有函数列表，包括：定义函数，库函数
all_func_list = []

# 分级分类
# 首先，检查不包含空格的语句中是否包含 xxx(xxxx)
# 如果是，则进一步判断是函数定义还是调用 
## 带;号，声明或是调用
## 不带;号，定义，需要区分 if/while/switch
def keyword_call ( _str ):
    fun_list = []
    str_list = re.findall ( r"\(.*\)" , _str)
    str = str_list[0]
    str = str[2:-1] # 去掉 if/while/switch ( ... )，抽取其中的内容
    rgl_brackets_patten = re.compile( r'''.*\w+\s*\(.*\)''' ,re.X )
    if rgl_brackets_patten.match ( str ):
        # 其中内容确实有函数特征，抽取符合函数部分
        str_list = re.findall ( r"\w+\s*\(", str )
        for str in str_list: ## 如果嵌套调用，就处理多个符合 xxx( 的字符串
            str = str[:-1]
            fun_list.append( str )
        # print ( "调用:",fun_list )
    return fun_list

def get_name( _str ):
    fun_list = []
    str_list = re.findall ( r"\w+\s*\(" , _str )
    for str in str_list :
        str = str[:-1]
        fun_list.append(str)
    # print ( fun_list )
    return fun_list

def new_define_something( graph , src_file_name ):
    level_1_patten = re.compile( r'''.*\w+\(.*\)''' ,re.X) # xxx() ,无空格
    rgl_define_fun_patten = re.compile( r'''.*\s+\w+\s*\(.*\)''' ,re.X) # 函数定义，xxx func() ,无；and 有空格
    rgl_call_fun_patten = re.compile( r'''(.*\w+\s*=\s*)?(\(.*\))?\s*\w+\s*\(.*\)''' ,re.X) # 函数调用, xxx = func () ; or func() ; 包含空格
    rgl_comment_patten = re.compile( r'''^//.*''' ,re.X)
    rgl_mocao_patten = re.compile( r'''^\#.*''' ,re.X)

    current_line = 0
    def_func = None
    src_file = Src_file( src_file_name )
    graph.src_file_list.append( src_file )
    
    print ( "\n< File > ", src_file_name )
    with open( src_file_name ) as fd:
        for line in fd:
            current_line += 1
            line_0 = line
            line = line.strip() 
            line = line.replace(" ","")
            if rgl_comment_patten.match ( line ):
                continue
            if rgl_mocao_patten.match ( line ):
                continue
            # '''.*\w+\(.*\)''' ,去掉空格的语句，符合 xxx() 模式，
            # 进一步判断是函数定义，声明，调用或是if/while/swtich/for
            if level_1_patten.match ( line ):  
                if ( any ( keyword in line_0 for keyword in ["if", "switch", "while","for"] ) ):
                    # 关键词语句，进一步提取后再通过正则判断
                    keyword_call ( line_0 )
                else :
                    # 函数定义，声明，调用
                    if line.__contains__(";"):
                        # 有；，函数声明和调用
                        if rgl_call_fun_patten.match ( line_0 ):
                            n = get_name( line_0 )
                            print ( "   Call :",n )
                            if ( def_func != None ):
                                def_func.calling += 1
                                def_func.call_func_name_list.append( n )
                        else :
                            print ( "Declare : ",line_0 )
                    else:
                        if rgl_define_fun_patten.match ( line_0 ):
                            n = get_name( line_0 )
                            print ( "Define : ",n )
                            def_func = Function( n )
                            def_func.start_line = current_line
                            def_func.parent_src_file = src_file_name
                            src_file.func_list.append( def_func )
                            graph.all_func_list.append(def_func)
                        else :
                            str_list = re.findall(r"\(.*\)", line_0)
                            print ( "其他",str_list )
    return 0

## 遍历所有文件，记录 c 文件
def get_filelist(dir):
    Filelist = []
    for home, dirs, files in os.walk( dir ):
        for filename in files:
            if filename.endswith(".c") :
                Filelist.append(os.path.join(home, filename))
    return Filelist


def main():
    file_list = get_filelist( sys.path[0]+"/src" )    
    graph = Code_graph()

    ## 第一次遍历，扫描所有文件，将定义函数添加到列表 all_func_list
    for f in file_list:
        new_define_something( graph ,f )
    return 

#########
if __name__ == "__main__":
    main()
