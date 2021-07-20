# --*-- coding:utf-8 --*--
"""
flask utils
"""
import os
from urllib.parse import quote

from flask import Response

from app.utils.errors import ParamError, ServerError
from config.base_config import Config


class File:
    """文件操作的类:上传，下载等"""
    def __init__(self, limit=1024 * 1024 * 20, chunk_size=512):
        self.limit = limit
        self.chunk_size = chunk_size

    def validate_exist(self, file, upload_dir):
        """检验目标目录下是否有重名文件存在"""
        files = os.listdir(upload_dir)
        if file.filename in files:
            raise ParamError(msg='目录下已存在同名文件!')

    def validate_size(self, file):
        """校验文件大小"""
        if self.limit is None:
            return

        self.content = file.read()
        size = len(self.content)
        if size > self.limit:
            val = int(self.limit / (1024 * 1024))
            raise ParamError(msg=f'文件大小超出限制，仅限{val}MB以下!')

    def check_upload_file(self, file, upload_dir):
        """上传文件校验"""
        if not file:
            raise ParamError(msg='请先选择文件再上传!')

        self.validate_exist(file, upload_dir)
        self.validate_size(file) # 默认限制 20 MB


    def upload(self, upload_dir, file):
        """文件上传"""
        self.check_upload_file(file, upload_dir)
        # filename = secure_filename(file.filename)
        file_path = os.path.join(upload_dir, file.filename)
        try:
            # file.save(file_path)  # 上面read读取后，file已经为空
            with open(file_path, 'wb') as f:
                f.write(self.content)
        except Exception as e:
            # logger.error(e)
            raise ParamError(msg='文件写入失败!')

    def download(self, file_dir, filename):
        """文件下载： 根据文件路径"""
        file_path = os.path.join(file_dir, filename)
        response = Response(self.file_iterator(file_path), content_type="application/octet-stream")
        response.headers['filename'] = quote(filename.encode('utf-8'))
        response.headers['Access-Control-Expose-Headers'] = 'filename'
        return response

    def file_iterator(self, file_path):
        """文件迭代读取"""
        with open(file_path, 'rb') as f:
            while 1:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    break
                yield chunk

    def delete(self, file_path):
        """删除文件"""
        try:
            os.remove(file_path)
        except Exception as e:
            # logger.error(e)
            raise ParamError(msg='删除失败!')

    def create_dir(self, dir_name):
        """创建目录
        dir_name:相对目录名
        """
        abs_path = os.path.join(Config.UPLOAD_DIR, dir_name)
        if not os.path.exists(abs_path):
            os.makedirs(abs_path)
        return abs_path

file_obj = File()
