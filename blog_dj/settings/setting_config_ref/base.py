"""
@Time  : 
@Author : 
@Desc : 公共配置
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import datetime
import os
from PyVbord.utils.deploy import REDIS_HOST, REDIS_PORT
from corsheaders.middleware import CorsMiddleware
from corsheaders.defaults import default_headers

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '(^4re1ov_*g!*ar@yzy3^#tar%zic#5jdyv*s%x*tm4tkb+k#r'

# W3鉴权接口地址
W3_TOKEN_URL = "http://10.43.246.48:9000/sso/login"

# ORT远端数据采集接口
ORT_DATA_GET_URL = "http://100.100.83.40:8888"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'api.pyvboard.cn',
]

SPHINX_CONF = {
    'HOST': 'xx.xx.xxx.xxx',
    'PORT': 9312,
    'FULL_TEXT_NAME': 'full_text_name',
    'FULL_TEXT_VALUE': 'select_all',
}

# CORS组的配置信息（添加白名单）
CORS_ORIGIN_WHITELIST = (
    "https://www.vuevboard.cn:8080",
)
CORS_ALLOW_CREDENTIALS = True  # 允许ajax跨域请求时携带cookie
CORS_ORIGIN_ALLOW_ALL = True
# CORS_ALLOW_HEADERS = default_headers + ('Cookie', 'Auth')
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'corsheaders',
    'rest_framework',
    'django_filters',

    '[app_name]',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # 'PyVbord.utils.email_conf_middleware.EmailConf',
    # 'PyVbord.utils.log_middleware.LogMiddle',
]

ROOT_URLCONF = 'blog_dj.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'PyVbord.wsgi.application'

# add by zm
DATABASE_ROUTERS = ['PyVbord.database_router.DatabaseAppsRouter']
DATABASE_APPS_MAPPING = {
    # example:
    # 'app_name':'database_name',
    'DFXSystem': 'common_db',
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'zh-hans'

# TIME_ZONE = 'UTC'
TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

# django-redis配置
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/3",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # 'PASSWORD': '', 密码配置
        }
    },
    'local_cache': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        "OPTIONS": {
            "MAX_ENTERS": 100
        }
    },
    'data_base_cache': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'mysql_cache',
        # 设置缓存的生命周期，以秒为单位，若为None，则永不过期
        'TIMEOUT': 60 * 30,
        'OPTIONS': {
            # MAX_ENTRIES代表最大缓存记录的数量
            'MAX_ENTRIES': 1000,
            # 当缓存到达最大数量之后，设置剔除缓存的数量
            'CULL_FREQUENCY': 300,
        }
    }
}

# rest_framework相关配置
REST_FRAMEWORK = {
    # 身份校验
    'DEFAULT_AUTHENTICATION_CLASSES': (
        #     'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        #     'rest_framework.authentication.SessionAuthentication',
        #     'rest_framework.authentication.BasicAuthentication',

        'PyVbord.utils.UserAuthentication.UserAuth',
    ),

    # 权限管理
    "DEFAULT_PERMISSION_CLASSES": (
        # 'PyVbord.utils.permissions.ModulePermission',
        # 'PyVbord.utils.permissions.UrlPermission',
    ),

    # 过滤配置  根据条件来查找数据
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),

    # 分页配置
    # 扩展默认分页类，支持参数设置分页大小，默认分页大小参数：page_size
    'DEFAULT_PAGINATION_CLASS': 'PyVbord.utils.GlobalPagination.PageNumberSizePagination',
    'PAGE_SIZE': 10,  # 每页几条数据
}

# jwt 配置
JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(hours=24),  # 过期时间
}

# 存放日志路径
LOG_PATH = os.path.join(BASE_DIR, 'logs')
# 配置日志
LOGGING = {
    'version': 1,  # 版本号，目前只能为1
    'disable_existing_loggers': False,  # 禁用Django默认logger
    'formatters': {  # 格式化器
        'standard': {  # 标准的格式
            'format': '[%(asctime)s][%(threadName)s:%(thread)d][task_id:%(name)s][%(filename)s:%(lineno)d]'
                      '[%(levelname)s][%(message)s]'
        },
        'simple': {  # 简单的格式
            'format': '[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d]%(message)s'
        },
        'custom': {  # 自定义格式，名字随意
            'format': '%(message)s'
        },
        'celery': {
            'format': '[%(levelname)s][%(asctime)s]%(message)s'
        }
    },
    'filters': {  # 过滤器
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {  # 处理器
        'console': {  # 定义一个在终端输出的处理器
            'level': 'WARNING',  # 日志级别
            'filters': ['require_debug_true'],  # debug为True时才在屏幕打印日志
            'class': 'logging.StreamHandler',
            'formatter': 'simple'  # 用简单格式打印日志
        },
        # 'SF': {  # 定义一个名为SF的日志处理器
        #     'level': 'INFO',  # 日志级别
        #     'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件，根据文件大小自动切
        #     'filename': '%s/log.log' % LOG_PATH,  # 日志文件
        #     'maxBytes': 1024 * 1024 * 50,  # 日志大小 50M
        #     'backupCount': 3,  # 备份数为3  xx.log --> xx.log.1 --> xx.log.2 --> xx.log.3
        #     'formatter': 'standard',  # 用标准格式打印日志
        #     'encoding': 'utf-8',
        # },
        'TF': {  # 定义一个名为TF的日志处理器
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',  # 保存到文件，根据时间自动切分
            'filename': '%s/log.log' % LOG_PATH,  # 日志文件
            'backupCount': 3,  # 保存最近三份日志文件
            'when': 'midnight',  # 可选值有S/秒 M/分 H/小时 D/天 W0-W6/周(0=周一) midnight/如果没指定时间就默认在午夜
            'interval': 1,  # 具体时间间隔
            'formatter': 'standard',
            'encoding': 'utf-8',
        },
        'celery': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件，自动切
            'filename': '%s/celery_worker.log' % LOG_PATH,  # 日志文件
            'maxBytes': 1024 * 1024 * 50,  # 日志大小 50M
            'backupCount': 5,
            'formatter': 'celery',
            'encoding': 'utf-8',
        },
        'celery_error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件，自动切
            'filename': '%s/celery_error.log' % LOG_PATH,  # 日志文件
            'maxBytes': 1024 * 1024 * 50,  # 日志大小 50M
            'backupCount': 5,
            'formatter': 'celery',
            'encoding': 'utf-8',
        },

    },
    'loggers': {
        '': {  # 日志实例对象默认配置
            'handlers': ['console', 'TF'],  # 使用哪几种处理器，上线后可以把'console'移除
            'level': 'DEBUG',  # 实例的级别
            'propagate': True,  # 是否向上传递日志流
        },
        'celery_log': {
            'handlers': ['celery', 'celery_error', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },

    },
}

DATA_UPLOAD_MAX_NUMBER_FIELDS = 102400  # higher than the count of fields

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
