""" 配置 celery 定时任务时间
注意：读取正式环境配置 prod.py
"""

import os

from celery import Celery
from celery.schedules import crontab
from datetime import timedelta

from blog_dj.apps.Commons.common_utils import now
from . import celeryConfig

from blog_dj.settings import prod

# 设置 Django 的配置文件
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Pyblog_djVbord.settings.prod')

# 创建 celery 实例
celery_app = Celery('blog_dj')
# 加载 celery 配置文件
celery_app.config_from_object(celeryConfig)
# 检测异步任务
celery_app.autodiscover_tasks(lambda: prod.INSTALLED_APPS)

""" 配置定时任务 """

celery_app.conf.update(
    CELERYBEAT_SCHEDULE={
        # 按指定时间
        'func1': {
            'task': 'blog_dj.apps.app_name.tasks.func1',
            'schedule': crontab(minute='0', hour='10, 17', day_of_week='*'),
        },
        # 按间隔时间
        'func2': {
            'task': 'PyVbord.apps.app_name.tasks.func2',
            'schedule': timedelta(hours=1)
        },
    }
)
