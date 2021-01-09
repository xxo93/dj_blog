# coding:utf-8
"""
@Desc: 分割大文件
@Author: wangzhongmin
@Date: 2020.12.31
"""

filename = r'uwsgi.log'  # 要拆分的文件路径(默认为同级目录)
outputF = r'uwsgi.log'  # 拆分之后的文件名（前部）
outi = 1  # 拆分之后的文件名下标
with open(filename, 'r', encoding='UTF-8') as f:
    read_data = f.read(100 * 1024)  # 100KB 每次读取100KB大小内容
    while (read_data != ''):
        with open('log_data/' + outputF + str(outi) + '.txt', 'w', encoding='UTF-8') as f_o:
            for j in range(0, 1024):  # 100KB * 1024 =100mb      拆分后每个文件大小100MB
                outbytes = f_o.write(read_data)
                read_data = f.read(100000)  # 100KB
                if (read_data == ""):
                    break
        outi = outi + 1
    print('over')
