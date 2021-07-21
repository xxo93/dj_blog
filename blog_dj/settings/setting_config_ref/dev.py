"""
@Time  : 
@Author : 
@Desc : 开发环境配置
"""
from .base import *

DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '[开发库名]',
        'USER': 'root',
        'PASSWORD': '[密码]',
        'HOST': '[IP]',
        'PORT': 3306,
        'CONN_MAX_AGE': 60  # 数据库连接生命周期-- 60 seconds
    },
}
