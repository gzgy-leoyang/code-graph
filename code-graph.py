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

###########################
def get_func_name(ll ):
    str_list = re.findall(r"(.+?)\(", ll)  # 提取"("之前的字符
    list  = str_list[0].split(' ')
    if list.__len__() == 1 :
        name = list[0].strip()
    else:
        name = list[list.__len__()-1].strip()
    return name

def get_nest_str( line ):
    str_list = re.findall(r"(\()(.+?)(\))", line)  # 提取"("之前的字符
    # list  = str_list[0].split(' ')
    for i in str_list:
        print (i)

#############################
def get_void_func_name(ll ):
    str_list = re.findall(r"(.+?)\(", ll)  # 提取"("之前的字符
    return  str_list[0].strip()

def get_inner_func_name(ll ):
    str_list = re.findall(r"(.+?)\(", ll)  # 提取"("之前的字符
    return  str_list[1].strip()

def call_func_regist( graph, def_func,func_name ):
    # 以被调用者函数名，在总函数列表中查找到这个被调用函数对象
    func = get_func_obj_by_name( graph, func_name )
    if func == None :
        # 没有定义过，但被调用，属于库函数
        # new 一个函数对象，并加入总函数对象列表，
        # 该函数的被调用计数加1，但该对象的调用函数名为空
        # 调用计数也会保持为0
        f = Function( func_name )
        f.called += 1
        graph.all_func_list.append ( f )
    else:
        # 属于已定义函数，将该函数的被调用计数加1
        func.called += 1
    # 遍历当前定义函数的调用函数列表，检查是否已经登记调用，排除一个定义函数中多次调用同一函数的情况
    marked  = 0
    for fx_name in def_func.call_func_name_list :
        if fx_name == func_name :
            marked += 1
            
    if marked == 0 :
        # 没有被登记过
        # 调用者的调用计数加1,被调用者函数名加入调用者的列表
        def_func.calling += 1
        def_func.call_func_name_list.append( func_name )

####
def check_call_func(  line ):    
    rgl_genernal_call_func_str = r'''
    (
    (\s*\w+\s*)? # 变量类型
    (\s*\w+\s*\=\s*)? #变量名=
    (?!(if|while|switch|for))\w+\s*(\() # 排除 keyword,函数名(
    ( \&? \-? \"?\s*\w+\[?\s*\]?\W*\s*\"? ,?)*\S*\s*(\))\s*; # 参数列表,...)
    )
    '''
    call_func_patten = re.compile ( rgl_genernal_call_func_str,re.X )

    rgl_keyword_nest_call_func_str = r'''
    (
        (\s*(if|while|switch|for)\s* (\()) # keyword ( 
        ((\s*\w*\s*=) | (\s*\w*\s*==)) # 变量名=
        (\s*\w+\s*)(\()  #函数名(
        ((\s*\w+\s*,?\s)* (\))) # 参数列表)
        (\s*)(\))
    )
    '''
    call_keyword_nest_patten = re.compile ( rgl_keyword_nest_call_func_str,re.X )
    if call_keyword_nest_patten.match ( line):
        print ( "Nest Call 22: ",line )
        # str_list = re.findall(r"\((.+?)\(", line)
        # # str_list = re.findall(r"(\() ( (\s*\w*\s*=) | (\s*\w*\s*==\s*) )? (\s*\w+\s*) (\() (\s*\w+\s*,?)* (\)) (\s*) (\))", line)
        # return  get_func_name_nest_in_keyword( str_list )
    elif call_func_patten.match ( line ):
        # print ( "Genernal Call : ",line )
        str_list = re.findall(r"(\=?\s*.+?)\(", line )
        print ( "str_list[] ",str_list)

        return str_list[0].strip()
    return None

##############################
## 扫描文件内的调用函数，将被调用函数登记到调用者名下
def scan_call_func(  graph,src_file_name ):

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
    # 函数头
    def_func_patten_name = re.compile(rgl_def_func_name,re.X)

    rgl_def_func_end = r'''
    (})(\s*) # 函数结束"}"
    '''
    # 函数尾
    def_func_patten_end = re.compile(rgl_def_func_end,re.X)
    
    file_path  = src_file_name
    scan_func_step = 0
    with open( file_path ) as fd:
        def_func =  None 
        for line in fd:
            if scan_func_step == 0 :
                if def_func_patten_name.match( line ):
                    scan_func_step = 1
                    n = get_func_name( line )
                    print ( "Function:",n )
                    # 定位函数头：调用者
                    def_func = get_func_obj_by_name( graph, n )
            elif scan_func_step==1:
                n = check_call_func(  line )
                if n != None:
                    print ( "   CALL :",n )
                elif def_func_patten_end.match( line ):
                    scan_func_step = 0
                    def_func = None 

                # if call_keyword_nest_patten.match ( line ):
                #     print ( line )
                #     get_nest_str( line )
                # elif call_func_patten.match( line ):
                #     # 函数内定位：被调用者
                #     n = get_func_name( line )
                #     if def_func != None :
                #         call_func_regist( graph, def_func, n )
                
    return 

########################
## 扫描文件内定义函数
# def scan_def_func(  src_file_name ):
def scan_def_func( graph, src_file_name ):

    # 匹配函数头，类型1，花括号与函数名不同行
    rgl_def_func_head = r'''
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

    # 匹配函数尾
    rgl_def_func_end = r'''(})(\s*)'''

    file_path  = src_file_name
    scan_func_step = 0
    current_line = 0
    new_func = None
    with open( file_path ) as fd:
        # 函数头
        def_func_head_patten = re.compile(rgl_def_func_head,re.X)
        # 函数尾
        def_func_end_patten = re.compile(rgl_def_func_end,re.X)

        src_file = Src_file( src_file_name )
        graph.src_file_list.append( src_file )
        for line in fd:
            current_line += 1
            if scan_func_step == 0 :
                if def_func_head_patten.match( line ):
                    scan_func_step = 1
                    n = get_func_name( line )
                    def_func = Function( n )
                    def_func.start_line = current_line
                    def_func.parent_src_file = src_file_name
                    src_file.func_list.append( def_func )
                    graph.all_func_list.append(def_func)
            elif scan_func_step == 1:
                if def_func_end_patten.match( line ):
                    scan_func_step = 0
                    def_func.end_line = current_line
                    def_func = None
    return src_file.func_list.__len__()


##################
## 遍历所有文件，记录 c 文件
def get_filelist(dir):
    Filelist = []
    for home, dirs, files in os.walk( dir ):
        for filename in files:
            if filename.endswith(".c") :
                Filelist.append(os.path.join(home, filename))
    return Filelist

####################################
## 由 函数名，返回函数对象
def get_func_obj_by_name( graph,func_name ):
    func_obj = None
    for f in graph.all_func_list :
        if func_name == f.name :
            return f
    return None

#################
## 打印函数调用树
layer_counter = 0
def print_func_relationship ( f ):
    global layer_counter 
    if f.call_func_list.__len__() != 0 :
        layer_counter += 1
        for call_f in f.call_func_list:
            print ("    "*layer_counter,end="")
            print ("|-",call_f.name )
            func_obj = get_func_obj_by_name( call_f.name )
            if func_obj != None:
                print_func_relationship ( func_obj )  
        layer_counter -= 1
        return        
    else :
        return None

def print_func_list( graph ):
    for f in graph.all_func_list :
        if f.called == 0 :    
            print ( " \n<<< %s >>>"%( f.name) )
        else:
            print ( " \n< %s >"%( f.name) )

        print ( "called:%i"%( f.called) )
        print ( "calling:%i"%( f.calling ) )
        if f.call_func_name_list.__len__() > 0 :
            print (  f.call_func_name_list  )


################################
## 展开函数关系图，递归调用
def extend_relationship ( canvas, f, id ):
    parent_id = id
    child_id = 0
    chide_base = id *10
    child_offset = 0
    
    ## TODO 根据函数的地位，为每个 node 计算设定 pos
    ## 最后，绘制时也要获取 pos 元组，分别导入 edge 和 node 绘制

    ## TODO 根据函数地位不同，设置每个node 的颜色不同，最后单独绘制 node
    canvas.add_node( parent_id , desc= f.name )

    if f.calling != 0 :
        child_offset = 0
        for call_func_name in f.call_func_name_list:
            child_id = chide_base + child_offset
            # 添加一个子节点
            canvas.add_node( child_id , desc= call_func_name )
            print ( "C: %i,%s"% ( child_id , call_func_name) ) 
            # 添加“父子”连接
            canvas.add_edge( parent_id , child_id) 
            # 根据函数名，获取函数对象，准备向下遍历
            func_obj = get_func_obj_by_name( call_func_name )
            child_offset += 1
            if func_obj != None:
                extend_relationship (canvas , func_obj , child_id ) 
        return        
    else :
        return None

#######################################
## 绘制指定函数的调用关系图
# def draw_root_func_relationship( root_func ):
#     canvas = nx.DiGraph()
#     extend_relationship ( canvas , root_func , 1 )

#     pos = nx.spring_layout(canvas)
#     nx.draw_networkx_edges(canvas,pos,alpha=0.4)

#     nx.draw_networkx_nodes(canvas,pos,node_size=80,alpha=0.4)

#     # nx.draw(canvas, pos,node_size =400 )
#     node_labels = nx.get_node_attributes(canvas, 'desc')
#     nx.draw_networkx_labels(canvas, pos, labels=node_labels)
#     plt.show()

def not_empty(s):
    return s and s.strip()

def get_func_name_nest_in_keyword( str_list ):
    ss = str_list[0].split()
    # l = ss.__len__

    return
    # mid_str = []
    # #去除空格内容
    # for s in str_list[0]:
    #     if s != '' and s != " ":
    #         mid_str.append(s)
    # # 截掉头尾的内容
    # mid_str2 = mid_str[1:-1]

    # print (mid_str2 )

    # if mid_str2.count("==") > 0 :
    #     return mid_str2[ mid_str2.index("==")+1]

    # if  mid_str2.count("=") > 0 :
    #     return mid_str2[ mid_str2.index("=")+1]
    
    # return mid_str2[ 0 ]

def scan_keyword_nest_call_func(  graph,src_file_name ):
    
    file_path  = "/home/dd/py-demo/code-graph/src/a.c"
    scan_func_step = 0
    with open( file_path ) as fd:
        def_func =  None 
        for line in fd:
            name = check_call_func(  line )
            if name != None:
                print ( "NAME:",name)    
    return 




def main():
    # print ("main:")
    file_list = get_filelist( sys.path[0]+"/src" )    
    graph = Code_graph()
    # scan_keyword_nest_call_func(  graph,"dd" )
    ## 第一次遍历，扫描所有文件，将定义函数添加到列表 all_func_list

    # scan_def_func( graph, "/home/dd/py-demo/code-graph/src/can_service.c")
    for f in file_list:
        scan_def_func( graph, f )
    
    ## 第二次遍历，扫描所有文件，将定义函数内的“被调用函数”登记到
    ## “调用函数”(定义函数) 的 call_func_name_list 中
    ## 如果是库函数，将会在此过程被添加到 all_func_list 
    ## 此过程，还将完成：记录函数的“被调用计数called”和“调用计数calling”
    scan_call_func( graph, "/home/dd/py-demo/code-graph/src/can_service.c")

    # for f in file_list:
    #     print ("SCAN call_func from : ", f )
    #     scan_call_func( graph, f )

    # print_func_list( graph )

    ## 绘制所有的“顶层函数”的调用关系
    # root_func_list = []
    # for f in all_func_list :
    #     if f.called == 0:
    #         root_func_list.append(f)

    # draw_root_func_relationship(  root_func_list[0] )
    # print ( " \nROOT Func : %s "%( f.name) )
    return 

#########
if __name__ == "__main__":
    main()