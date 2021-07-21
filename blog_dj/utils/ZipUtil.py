# -*- coding: utf-8 -*-
"""
@Time  : 
@Author :       
@Desc : Zip压缩工具类,封装了ZipStream的方法
"""
import datetime
import os

import zipstream
from django.http import StreamingHttpResponse, HttpResponse


class ZipUtils:
    def __init__(self):
        self.zip_file = zipstream.ZipFile(mode='w', compression=zipstream.ZIP_DEFLATED)

    def zip(self, file, name):
        if os.path.isfile(file):
            self.zip_file.write(file, arcname=os.path.basename(file))
        else:
            self.zip_folder(file, name)

    def zip_folder(self, folder, name):
        for file in os.listdir(folder):
            full_path = os.path.join(folder, file)
            if os.path.isfile(full_path):
                self.zip_file.write(full_path, arcname=os.path.join(name, os.path.basename(full_path)))
            else:
                self.zip_folder(full_path, os.path.join(name, os.path.basename(full_path)))

    def close(self):
        if self.zip_file:
            self.zip_file.close()

    def export_zip(self, dir_name, zip_name):
        for file in os.listdir(dir_name):
            full_path = os.path.join(dir_name, file)
            self.zip(full_path, file)
        zip_name = "{}_{}.zip".format(zip_name, datetime.datetime.now().strftime("%Y%m%d"))
        response = HttpResponse(self.zip_file)
        response['Content-type'] = "application/zip"
        response['Content-Disposition'] = 'attachment;filename="{}"'.format(zip_name)
        return response
