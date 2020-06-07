#!/usr/bin/python3
#!/usr/bin/env python3

import os
import re
import sys
import getopt
import readline
import string

## 绘图
import networkx as nx
import matplotlib.pyplot as plt

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
    return fun_list

def get_name( _str ):
    fun_list = []
    str_list = re.findall ( r"\w+\s*\(" , _str )
    for str in str_list :
        str = str[:-1]
        fun_list.append(str)
    return fun_list

####################################
## 由 函数名，返回函数对象
def get_func_obj_by_name( graph,func_name ):
    for f in graph.all_func_list :
        if func_name == f.name :
            return f
    return None

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
                    names = keyword_call ( line_0 )
                    if ( def_func != None ):
                        for name in names:
                            re_marked = 0
                            for name_marked in def_func.call_func_name_list :
                                if ( name_marked ==  name  ):
                                    re_marked += 1
                            if ( re_marked == 0 ):
                                # print ( "   Call :",name)
                                def_func.calling += 1
                                def_func.call_func_name_list.append( name )
                else :
                    # 函数定义，声明，调用
                    if line.__contains__(";"):
                        # 有；，函数声明和调用
                        if rgl_call_fun_patten.match ( line_0 ):
                            names = get_name( line_0 )
                            if ( def_func != None ):
                                for name in names:
                                    re_marked = 0
                                    for name_marked in def_func.call_func_name_list :
                                        if ( name_marked ==  name  ):
                                            re_marked += 1
                                    
                                    if ( re_marked == 0 ):
                                        # print ( "   Call :",name)
                                        def_func.calling += 1
                                        def_func.call_func_name_list.append( name )
                        else :
                            pass
                            # print ( "Declare : ",line_0 )
                    else:
                        if rgl_define_fun_patten.match ( line_0 ):
                            names = get_name( line_0 )
                            for nm in names:
                                # print ( "Define : ",nm)
                                def_func = Function( nm )
                                def_func.start_line = current_line
                                def_func.parent_src_file = src_file_name
                                src_file.func_list.append ( def_func )
                                graph.all_func_list.append ( def_func )
                        else :
                            str_list = re.findall(r"\(.*\)", line_0)
                            # print ( "其他",str_list )
    return 0

## 遍历所有文件，记录 c 文件
def get_filelist(dir):
    Filelist = []
    for home, dirs, files in os.walk( dir ):
        for filename in files:
            if filename.endswith(".c") :
                Filelist.append(os.path.join(home, filename))
    return Filelist

## 梳理被调用关系
#  对每一个定义函数，排查其调用函数列表，如果定义函数名=被调用函数名，则标记
# 定义函数的被调用记录，包括：被调用计数和调用该定义函数的函数名
def checkout_called( graph ):
    for fx in graph.all_func_list : # 定义函数
        for fy in graph.all_func_list : # 遍历包括定义函数在内的所有定义函数
            for fz in fy.call_func_name_list: # 逐一检查定义函数的调用列表，排查是否与定义函数同名
                if ( fz == fx.name ):
                    fx.called += 1
                    fx.called_func_name_list.append( fy.name )


def max_called_calling( graph ):
    call_max_name = ""
    call_max_num = 0

    called_max_name = ""
    called_max_num = 0
    for fx in graph.all_func_list :
        if fx.calling > call_max_num :
            call_max_num = fx.calling
            call_max_name =  fx.name
        if fx.called > called_max_num:
            called_max_num = fx.called
            called_max_name = fx.name

    print("MAX_CALL : ",call_max_name,call_max_num)
    print("MAX_CALLED : ",called_max_name,called_max_num)

def print_func_list( graph ):
    for f in graph.all_func_list :
        if f.called == 0 :    
            print ( " \n<<< %s >>>"%( f.name) )
        else:
            print ( " \n< %s >"%( f.name) )

        print ( "called:%i"%( f.called) )
        if f.called_func_name_list.__len__() > 0 :
            print (  f.called_func_name_list  )

        print ( "calling:%i"%( f.calling ) )
        if f.call_func_name_list.__len__() > 0 :
            print (  f.call_func_name_list  )

####################################
## 由 函数名，返回函数对象
def get_func_obj_by_name( graph,func_name ):
    func_obj = None
    for f in graph.all_func_list :
        if func_name == f.name :
            return f
    return None

################################
## 展开函数关系图，递归调用
def extend_relationship (graph, canvas, f, id ):
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
            func_obj = get_func_obj_by_name( graph, call_func_name )
            child_offset += 1
            if func_obj != None:
                extend_relationship ( graph , canvas , func_obj , child_id ) 
        return        
    else :
        return None


######################################
# 绘制指定函数的调用关系图
def draw_root_func_relationship( graph , root_func ):
    canvas = nx.DiGraph()
    extend_relationship ( graph , canvas , root_func , 1 )

    pos = nx.spring_layout(canvas)
    nx.draw_networkx_edges(canvas,pos,alpha=0.4)

    nx.draw_networkx_nodes(canvas,pos,node_size=80,alpha=0.4)

    # nx.draw(canvas, pos,node_size =400 )
    node_labels = nx.get_node_attributes(canvas, 'desc')
    nx.draw_networkx_labels(canvas, pos, labels=node_labels)
    plt.show()

def print_usage():
    print ( 'code-graph v0.0.1' )
    print ( 'Usage: code-graph.py -i <inputfile> -o <outputfile> ' )
    exit()

def parse_opt( argv ):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hi:",["ifile="])
    except getopt.GetoptError:
        print ( 'code-graph -i <inputfile>' )
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ( 'code-graph.py -i <inputfile> -o <outputfile> ' )
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
            return inputfile

def main ( argv ):
    input_file = parse_opt( argv )
    
    if ( input_file == None ):
        print_usage()

    if not os.access( input_file, os.F_OK):
        print_usage()

    file_list = get_filelist( sys.path[0]+"/src" )    
    graph = Code_graph()

    new_define_something( graph ,input_file )
    checkout_called( graph )
    print_func_list( graph )

    ## 第一次遍历，扫描所有文件，将定义函数添加到列表 all_func_list
    # for f in file_list:
    #     new_define_something( graph ,f )
    # checkout_called( graph )
    # print_func_list( graph )

    for f in graph.all_func_list :
        if f.called == 0:
            print ("CALLED_0 : ", f.name )
            root_func = f
            break
    
    draw_root_func_relationship( graph , root_func )

    return 

#########
if __name__ == "__main__":
    main ( sys.argv[1:]  )
