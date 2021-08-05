# -*- coding: utf-8 -*-
""" 
@Author: wangzhongmin
@Date: 2021/4/23
@Desc: AES 加密
"""

from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex


def add_to_16(text):
    """ 用空格将不足16位的倍数的text参数补足为16位 """
    if len(text.encode('utf-8')) % 16:
        add = 16 - (len(text.encode('utf-8')) % 16)
    else:
        add = 0
    text = text + ('\0' * add)
    return text.encode('utf-8')


def encrypt(text):
    """ 密码加密函数 """
    # key和iv是16位
    key = '1542645641245133'.encode('utf-8')
    iv = b'aes_encryption.v'
    mode = AES.MODE_CBC
    text = add_to_16(text)
    cryptos = AES.new(key, mode, iv)
    cipher_text = cryptos.encrypt(text)
    return b2a_hex(cipher_text)


def decrypt(text):
    """ 密码解密函数，解密后去掉补足的空格 """
    # key和iv是16位
    key = '1542645641245133'.encode('utf-8')
    iv = b'aes_encryption.v'
    mode = AES.MODE_CBC
    cryptos = AES.new(key, mode, iv)
    plain_text = cryptos.decrypt(a2b_hex(text)).decode().rstrip('\0')
    return plain_text

# if __name__ == '__main__':
#     # 将密码加密写入数据库
#     e = encrypt("")  # 加密密码
#     password = e
#     d = decrypt(e)  # 解密
#     print("加密:", e)
#     print("解密:", d)
