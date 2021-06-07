# -*- coding: utf-8 -*-
"""
深度递归遍历指定目录下所有文件及其子目录所有文件
"""
import os


def getAllFilesOfWalk(dir):
    """使用listdir循环遍历"""
    if not os.path.isdir(dir):
        print(dir)
        return
    dirlist = os.walk(dir)
    for root, dirs, files in dirlist:
        print(root, dirs, files)
        for file in files:
            print(os.path.join(root, file))


if __name__ == '__main__':
    dir = ''
    getAllFilesOfWalk(dir)
