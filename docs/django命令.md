
## celery
1.检查已经注册的task
celery -A tasks inspect registered
2.查看worker状态
celery -A myrecrument  status
## django
1.检查django项目语法
D:\djangotest\myrecrument>  python manage.py check  

```python
1.检查已经注册的task
D:\djangotest\myrecrument\mycelery> celery -A tasks inspect registered

2.检查django项目语法
D:\djangotest\myrecrument>  python manage.py check   

3.celery delay 坑
#########
def notify_interviewer(modeladmin,request,queryset):
    logger.info('i enter notify_interviewer...begin')
    candidates = ' '
    for obj in queryset:
        candidates = obj.username + ';' + candidates
    #dingtalk.send(candidates)
    
    send_dingtalk_message.delay(candidates)
    logger.info('i enter notify_interviewer...after delay')

#########
# 项目目录 __init__.py 忘了添加以下内容，造成task.delay卡主
from __future__ import absolute_import, unicode_literals

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app  #少了这一点，delay就卡住发送不了消息

__all__ = ('celery_app',)
```
