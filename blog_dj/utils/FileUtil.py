# -*- coding: utf-8 -*-
"""
@Author: wwx800191
@Date: 2021/3/26
@Desc: 文件
"""
import re
import os
import sys
import time
import stat
import socket
import shutil
from ftplib import FTP
from uuid import uuid4
from datetime import datetime

from django.http import HttpResponse
from django.utils.encoding import escape_uri_path

from PyVbord.utils.errors import ParamsException
from PyVbord.utils.errors_code import RECORD_NOT_EXISTS


def upload_to_localhost(files, paths, target_dir, root_directory=None):
    """
    将目录上传到项目服务器的指定目录
    :param files: 文件的列表
    :param paths: 文件路径的列表
    :param target_dir: 上传指定的目录
    :param root_directory 上传指定目录的下一级目录（用于存放当前文件的目录）
    :return:
    """
    # 创建根目录
    if not root_directory:
        uuid = str(uuid4())
        root_directory = os.path.join(target_dir, datetime.now().strftime('%Y%m%d') + "-" + uuid)
    else:
        root_directory = os.path.join(target_dir, root_directory)
    if paths:
        # 处理目录
        for index, each_file in enumerate(files):
            file_dir, file_name = os.path.split(paths[index])
            file_dir = os.path.join(root_directory, file_dir)
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
            file_path = os.path.join(file_dir, file_name)
            with open(file_path, 'wb+') as f:
                for chunk in each_file.chunks():
                    f.write(chunk)
    else:
        if not os.path.exists(root_directory):
            os.makedirs(root_directory)
        for each_file in files:
            # 单个处理文件
            file_path = os.path.join(root_directory, each_file.name)
            with open(file_path, 'wb+') as f:
                for chunk in each_file.chunks():
                    f.write(chunk)
    return root_directory


def readonly_handler(func, path, execinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def del_localhost_dir(target_dir):
    shutil.rmtree(target_dir, onerror=readonly_handler)


def merge_file(file_name, root_directory):
    def get_file_id(origin_name):
        return int(origin_name.replace(file_name, ""))

    up_file_names = [each_file_name for each_file_name in os.listdir(root_directory) if file_name in each_file_name]
    # 将文件排序
    up_file_names.sort(key=get_file_id)
    merge_file_path = os.path.join(root_directory, file_name)
    with open(merge_file_path, "ab+") as f:
        for up_file_name in up_file_names:
            root_up_file_name = os.path.join(root_directory, up_file_name)
            g = open(root_up_file_name, "rb")
            f.write(g.read())
            g.close()
            os.remove(root_up_file_name)


class FileUtil(object):
    def __init__(self, base_dir='/usr/upload'):
        self.base_dir = base_dir

    def validate_path(self, file_name):
        if '..' in file_name:
            raise ParamsException({"code": RECORD_NOT_EXISTS, "error_msg": "无效的文件名或文件路径"})

    def get_file_dir(self, file_dir):
        file_path = self.base_dir
        if file_dir:
            self.validate_path(file_dir)
            file_path = os.path.join(self.base_dir, file_dir)
            if not os.path.exists(file_path):
                os.makedirs(file_path)
        return file_path

    def download(self, file_path):
        file_path = self.get_file_dir(file_path)
        file_name = os.path.basename(file_path)
        with open(file_path, 'rb') as f:
            # file_name = f"{time.strftime('%Y%m%d%H%M%S', time.localtime())}{suffix}"
            response = HttpResponse(f)
            response['Content-Type'] = 'application/octet-stream'
            response['Access-Control-Expose-Headers'] = "Content-Disposition"
            response["Content-Disposition"] = "attachment; filename*={}".format(escape_uri_path(file_name))
            # response["Content-Disposition"] = f"attachment; filename={file_name}"
        return response

    def delete(self, file_dir):
        if file_dir:
            self.validate_path(file_dir)
            file_path = os.path.join(self.base_dir, file_dir)
            if os.path.exists(file_path):
                os.remove(file_path)
                return file_path

    def upload(self, file, file_dir=None):
        file_path = self.get_file_dir(file_dir)
        file_name = file.name
        suffix = file_name[file_name.rfind('.'):]
        origin_file_name = file_name[:file_name.rfind('.')]
        file_name = f"{origin_file_name}_{time.strftime('%Y%m%d%H%M%S', time.localtime())}{suffix}"
        file_path = os.path.join(file_path, file_name)
        with open(file_path, 'wb+') as f:
            for chunk in file.chunks():
                f.write(chunk)
        if file_dir:
            file_name = os.path.join(file_dir, file_name)
        return file_name

    def get_file_size(self, file_path):
        file_path = self.get_file_dir(file_path);
        return os.path.getsize(file_path)


class FtpFileUtils:
    """ ftp自动下载、自动上传脚本，可以递归目录操作 """

    def __init__(self, host, port=21):
        """
        @desc: 初始化 FTP 客户端
        :param host: ip地址
        :param port: 端口号
        """
        self.host = host
        self.port = port
        self.ftp = FTP()
        # 重新设置下编码方式
        self.ftp.encoding = 'gbk'
        self.log_file = open("PyVbord/logs/ftp_log.txt", "a")
        self.file_list = []
        self.lines = []

    def __clear_lines(self):
        self.lines = []

    def __save_line(self, line):
        self.lines.append(line)

    def login(self, username, password):
        """
        @desc: 初始化 FTP 客户端
        :param username: 用户名
        :param password: 密码
        """
        try:
            timeout = 60
            socket.setdefaulttimeout(timeout)
            # 0主动模式 1 #被动模式
            self.ftp.set_pasv(True)
            # 打开调试级别2，显示详细信息
            # self.ftp.set_debuglevel(2)

            self.debug_print('开始尝试连接到 %s' % self.host)
            self.ftp.connect(self.host, self.port)
            self.debug_print('成功连接到 %s' % self.host)

            self.debug_print('开始尝试登录到 %s' % self.host)
            self.ftp.login(username, password)
            self.debug_print('成功登录到 %s' % self.host)

            self.debug_print(self.ftp.welcome)
        except Exception as err:
            self.deal_error("FTP 连接或登录失败 ，错误描述为：%s" % err)

    # def is_same_size(self, local_file, remote_file):
    #     """判断远程文件和本地文件大小是否一致
    #
    #        参数:
    #          local_file: 本地文件
    #
    #          remote_file: 远程文件
    #     """
    #     try:
    #         remote_file_size = self.ftp.size(remote_file)
    #     except Exception as err:
    #         # self.debug_print("is_same_size() 错误描述为：%s" % err)
    #         remote_file_size = -1
    #
    #     try:
    #         local_file_size = os.path.getsize(local_file)
    #     except Exception as err:
    #         # self.debug_print("is_same_size() 错误描述为：%s" % err)
    #         local_file_size = -1
    #
    #     self.debug_print('local_file_size:%d  , remote_file_size:%d' % (local_file_size, remote_file_size))
    #     if remote_file_size == local_file_size:
    #         return 1
    #     else:
    #         return 0

    def download_file(self, source_file_path, target_file_path):
        """
        @desc: 从ftp下载文件
        :param source_file_path: 源文件（路径字符串或者文件对象）
        :param target_file_path: 目标文件路径
        :return:
        """
        try:
            buf_size = 1024
            # 如果target_file_path是字符串路径
            if isinstance(source_file_path, str):
                file_handler = open(source_file_path, 'wb')
            # 否则target_file_path是文件流
            else:
                file_handler = source_file_path
            self.ftp.retrbinary('RETR %s' % target_file_path, file_handler.write, buf_size)
            file_handler.close()
        except Exception as err:
            self.debug_print('下载文件出错，出现异常：%s ' % err)
            return

    def download_file_tree(self, target_file_path, remote_file_path):
        """
        @desc: 从远程目录下载多个文件到本地目录
        :param target_file_path: 本地路径
        :param remote_file_path: 远程路径
        """
        try:
            self.ftp.cwd(remote_file_path)
        except Exception as err:
            self.debug_print('远程目录%s不存在，继续...' % remote_file_path + " ,具体错误描述为：%s" % err)
            return

        if not os.path.isdir(target_file_path):
            self.debug_print('本地目录%s不存在，先创建本地目录' % target_file_path)
            os.makedirs(target_file_path)

        self.debug_print('切换至目录: %s' % self.ftp.pwd())

        self.file_list = []
        # 方法回调
        self.ftp.dir(self.get_file_list)

        remote_names = self.file_list
        self.debug_print('远程目录 列表: %s' % remote_names)
        for item in remote_names:
            file_type = item[0]
            file_name = item[1]
            local = os.path.join(target_file_path, file_name)
            if file_type == 'd':
                print("download_file_tree()---> 下载目录： %s" % file_name)
                self.download_file_tree(local, file_name)
            elif file_type == '-':
                print("download_file()---> 下载文件： %s" % file_name)
                self.download_file(local, file_name)
            self.ftp.cwd("..")
            self.debug_print('返回上层目录 %s' % self.ftp.pwd())
        return True

    def upload_file(self, source_file, target_file):
        """
        @desc: 从本地上传文件到ftp
        :param source_file: 源文件(字符串路径或者文件流对象)
        :param target_file: 远程文件
        """

        buf_size = 1024
        # 如果target_file为路径字符串
        if isinstance(source_file, str):
            file_handler = open(source_file, 'rb')
        # 否则target_file_path是文件流
        else:
            file_handler = source_file

        self.ftp.storbinary('STOR %s' % target_file, file_handler, buf_size)
        file_handler.close()
        self.debug_print('上传: %s' % target_file + "成功!")

    def del_file(self, path):
        self.ftp.delete(path)
        self.write_log("删除%s成功" % path)

    def upload_file_tree(self, local_path, remote_path):
        """
        @desc: 从本地上传目录下多个文件到ftp
        :param local_path: 本地路径
        :param remote_path: 远程路径
        """
        if not os.path.isdir(local_path):
            self.debug_print('本地目录 %s 不存在' % local_path)
            return

        self.ftp.cwd(remote_path)
        self.debug_print('切换至远程目录: %s' % self.ftp.pwd())

        local_name_list = os.listdir(local_path)
        for local_name in local_name_list:
            src = os.path.join(local_path, local_name)
            if os.path.isdir(src):
                try:
                    self.ftp.mkd(local_name)
                except Exception as err:
                    self.debug_print("目录已存在 %s ,具体错误描述为：%s" % (local_name, err))
                self.debug_print("upload_file_tree()---> 上传目录： %s" % local_name)
                self.upload_file_tree(src, local_name)
            else:
                self.debug_print("upload_file_tree()---> 上传文件： %s" % local_name)
                self.upload_file(src, local_name)
        self.ftp.cwd("..")

    def upload_file_obj_dir(self, source_file_list, source_path_list, remote_path="/"):
        """
        上传文件夹流到远端服务器
        :param source_file_list: 源文件流组成的对象列表
        :param source_path_list: 与源文件流一一对应的文件路径列表
        :param remote_path: 上传到远端服务器的路径
        :return:
        """
        self.ftp.cwd(remote_path)
        self.debug_print('切换至远程目录: %s' % self.ftp.pwd())
        # 创建唯一标识目录
        new_dir = "{}{}".format(datetime.now().strftime("%Y%m%d%H%M%S"), uuid4())
        try:
            self.ftp.cwd(new_dir)  # 切换到需要创建的子目录, 不存在则异常
        except Exception as e:
            self.ftp.mkd(new_dir)  # 不存在创建当前子目录
            self.ftp.cwd(new_dir)
        # 获取当前工作路径
        base_dir = self.ftp.pwd()

        source_path_list = source_path_list or ["/"]
        for index, each_obj in enumerate(source_file_list):
            # 复制当前路径
            base_dir_cp = base_dir
            path_components = re.split(r"/|\\", source_path_list[index])[:-1]
            for path_component in path_components:
                base_dir_cp = os.path.join(base_dir_cp, path_component)
                try:
                    self.ftp.cwd(base_dir_cp)  # 切换到需要创建的子目录, 不存在则异常
                except Exception as e:
                    self.ftp.mkd(base_dir_cp)  # 不存在创建当前子目录
            self.ftp.cwd(base_dir_cp)

            self.upload_file(source_file_list[index], source_file_list[index].name)
        # 切回根路径
        self.ftp.cwd(os.path.join("/", remote_path))
        return os.path.join(remote_path, new_dir)

    def del_dir(self, path):
        """
        @desc: 删除一个目录及其中全部的文件, 由于FTP只能删除空目录，要递归删除
        :param path:
        :return:
        """
        self.__clear_lines()
        self.ftp.cwd(path)
        self.ftp.retrlines("LIST", callback=self.__save_line)
        self.ftp.cwd('/')
        for line in self.lines:
            if "Microsoft" in self.ftp.getwelcome():
                # 代表是windows服务器
                name_match = re.search(r"<DIR> +(.*)", line, re.M | re.I)
                if name_match:
                    # 代表是目录
                    name_match = name_match.groups()[0]
                else:
                    # 代表是文件
                    name_match = re.search(r" +\d+ +(.*)", line, re.M | re.I).groups()[0]
                name = os.path.join(path, name_match)
            else:
                # linux服务器
                name = os.path.join(path, re.search(r"\d+:\d+ +(.*)", line, re.M | re.I).groups()[0])

            if line[0] == "d" or '<DIR>' in line:
                self.del_dir(name)
            else:
                self.ftp.delete(name)
        self.ftp.rmd(path)

    def close(self):
        """ 退出ftp
        """
        self.debug_print("close()---> FTP退出")
        self.ftp.quit()
        self.log_file.close()

    def debug_print(self, s):
        """ 打印日志
        """
        self.write_log(s)

    def deal_error(self, e):
        """ 处理错误异常
        :param e：异常
        """
        log_str = '发生错误: %s' % e
        self.write_log(log_str)
        sys.exit()

    def write_log(self, log_str):
        """ 记录日志
        :param log_str：日志
        """
        time_now = time.localtime()
        date_now = time.strftime('%Y-%m-%d', time_now)
        format_log_str = "%s ---> %s \n " % (date_now, log_str)
        print(format_log_str)
        self.log_file.write(format_log_str)

    def get_file_list(self, line):
        """ 获取文件列表
        :param line：
        """
        file_arr = self.get_file_name(line)
        # 去除  . 和  ..
        if file_arr[1] not in ['.', '..']:
            self.file_list.append(file_arr)

    def get_file_name(self, line):
        """ 获取文件名
         :param line：
        """
        pos = line.rfind(':')
        while (line[pos] != ' '):
            pos += 1
        while (line[pos] == ' '):
            pos += 1
        file_arr = [line[0], line[pos:]]
        return file_arr


def get_file_hanlder(host, port, username, password):
    ftp_handler = FtpFileUtils(host=host, port=port)
    ftp_handler.login(username=username, password=password)
    return ftp_handler
