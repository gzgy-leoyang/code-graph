#!/usr/bin/python3
#!/usr/bin/env python3

import os
import re
import sys
import getopt
import readline

def parse_file( file_name ):
    file_path  = sys.path[0] +'/'+file_name
    with open( file_path ) as fd:
        for line in fd:
            print(line)
    return 0

############################
# @berif 打印 help 信息
def usage( ):
    print(' Usage: Code-graph <cmd> [opt]')
    print(' cmd:')
    print('     commit  ：...')
    print(' Code-graph v0.1  2020/2/27 ( leoyang20102013@163.com )')

#################
def main():
    if sys.argv.__len__() <= 1:
        usage()
        exit()
    return 

#########
if __name__ == "__main__":
    main()