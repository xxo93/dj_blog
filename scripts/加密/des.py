# -*- encoding: utf-8 -*-
"""
@author: wangzhongmin
@time: 2021/9/13 9:38
@desc: DES加密 类
pip install pyDes
"""
import base64
import json
import uuid
from pyDes import *


class DesEngine:
    """ DES加密类 """
    EXTERNAL_KEY = 'KAYISOFT'
    EXTERNAL_IV = 'KAYISOFT'
    """
    str(encrypt_dict).encode()  # bytes
    json.dumps(encrypt_dict)    # json
    json.dumps(encrypt_dict).encode()   # bytes
    """

    @staticmethod
    def external_encrypt(encrypt_str: str, key: str = EXTERNAL_KEY, iv: str = EXTERNAL_IV):
        """ 对 字符对象 加密成 加密字符串 (外部解析)"""

        # 转bytes
        encrypt_bytes = bytes(encrypt_str, encoding="utf-8")
        key_bytes = bytes(key, encoding="utf-8")
        iv_bytes = bytes(iv, encoding="utf-8")

        # 加密
        k = des(key_bytes, CBC, iv_bytes, pad=None, padmode=PAD_PKCS5)
        encrypt_bytes = k.encrypt(encrypt_bytes)

        # base64编码 返回 str类型
        encrypt_str = base64.b64encode(encrypt_bytes).decode()  # 转base64编码返回
        return encrypt_str

    @staticmethod
    def external_decrypt(license: str, key=EXTERNAL_KEY, iv=EXTERNAL_IV):
        """ 将 加密字符串 解密成 字符对象 (外部解析)"""
        license_bytes = base64.b64decode(license)
        k = des(key, CBC, iv, pad=None, padmode=PAD_PKCS5)
        decrypt_bytes = k.decrypt(license_bytes)
        try:
            decrypt_obj = decrypt_bytes.decode()
        except Exception as ex:
            decrypt_obj = None
        return decrypt_obj


if __name__ == "__main__":
    st = '你好世界xxx'
    encrypt_str = DesEngine.external_encrypt(st)
    print('加密后字符:', encrypt_str)

    decrypt_str = DesEngine.external_decrypt(encrypt_str)
    print('解密后字符:', decrypt_str)
