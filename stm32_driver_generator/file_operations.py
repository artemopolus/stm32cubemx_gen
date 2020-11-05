import sys
import os
import re
from shutil import copyfile

def copySrcToDst(src, dst):
    copyfile(src, dst)

def getStringFromFile(path, filename, label, fileext = '.c'):
    list_files = findFileInFolder(path, filename, fileext=fileext)
    out = []
    with open(list_files[0],'r') as src:
        code_lines = src.read().splitlines()
        for line in code_lines:
            if line.find(label) != -1:
                out.append(line)
    return out 


def findFileInFolder(path, file, fileext = ''):
    target_path = []
    cur_files = os.listdir(path)
    for elem in cur_files:
        elem_path = path + '\\' + elem
        if os.path.isdir(elem_path):
            return_path = findFileInFolder(elem_path, file, fileext = fileext)
            if return_path:
                target_path.append( return_path )
        else:
            _filename, _fileext = os.path.splitext(elem)
            if file == _filename:
                if fileext:
                    if _fileext == fileext:
                        target_path.append(elem_path)
                else:
                    target_path.append(elem_path)
    output = multiToFlat(target_path)
    return output

def multiToFlat(data, new_data = None):
    if new_data == None:
        new_data = []
    for elem in data:
        if type(elem) == list:
            multiToFlat(elem,new_data=new_data)
        else:
            new_data.append(elem)
    return new_data