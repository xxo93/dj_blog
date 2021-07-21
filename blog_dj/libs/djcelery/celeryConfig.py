""" celery配置文件
# 多任务队列(消息队列)、多worker执行
celery指令：
    启动beat：
        celery beat -A PyVbord.libs.djcelery -l INFO
    启动多个worker (-n workerName@%h)，订阅 指定消息队列(-Q queueName)：
    -- 默认worker(-n celery@%h)
        # 订阅默认队列'celery'
        celery worker -A PyVbord.libs.djcelery -P eventlet -l INFO -Q celery
        # 启动用于执行含有调用requests模块的任务 worker，订阅 for_contains_requests_use 消息队列：
        celery worker -A PyVbord.libs.djcelery -c 1 -P solo -l INFO -Q for_contains_requests_use
    -- 自定义worker(-n workName@%h) linux下 ‘%’为特殊字符，需要‘%%’代替
        celery worker -A PyVbord.libs.djcelery -P eventlet -l INFO -n asynchronous_task@%%h -Q asynchronous_task     # 异步任务队列
        celery worker -A PyVbord.libs.djcelery -P eventlet -l INFO -n email_alert@%%h -Q email_alert           # 预警提醒消息队列
        celery worker -A PyVbord.libs.djcelery -P eventlet -l INFO -n certification_risk@%%h -Q certification_risk    # 认证预警任务队列
"""
from kombu import Exchange, Queue

from blog_dj.utils.deploy import REDIS_HOST, REDIS_PORT

BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/2'     # (消息中间件)任务调度队列,接收任务,使用redis
BROKER_POOL_LIMIT = 100     # Borker 连接池, 默认是10

CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_ACCEPT_CONTENT = ['json']

TASK_SERIALIZER = 'json'

CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/1'  # 任务结果存储
CELERY_RESULT_SERIALIZER = 'json'
CELERY_MAX_CACHED_RESULTS = 1000  # 任务结果最大缓存数量

CELERYD_FORCE_EXECV = True    # 只有当worker执行完任务后,才会告诉MQ,消息被消费，防止死锁
CELERY_ACKS_LATE = True
CELERY_TASK_RESULT_EXPIRES = 24 * 60 * 60   # 任务过期时间，celery任务执行结果的超时时间，设为24小时

# 日志等级
WORKER_REDIRECT_STDOUTS_LEVEL = 'INFO'

"""
多任务队列，多worker配置说明：
    1) Queue celery(默认队列)：celery会将未配置路由的任务默认发布推送到 celery Queue；
    2) Queue asynchronous_task：存放异步任务的队列
    3) Queue for_contains_requests_use: 当任务中调用了爬虫相关模块(如：requests)可以将任务发布到该队列
    4) Queue email_alert: 独立出预警消息提醒队列
    5) Queue certification_risk: 独立出认证拦截预警队列
"""
# 创建任务队列， 可以将不同类型的任务发布到不同的任务队列
CELERY_QUEUES = (
    # 默认自动创建一个名为'celery'的队列
    # Queue("{队列名}", Exchange("{交换机名}", type="{默认为直连交换机direct}"), routing_key="{路由键}"),
    Queue("asynchronous_task", Exchange("asynchronous_task"), routing_key="asynchronous_task"),
    Queue("for_contains_requests_use", Exchange("for_contains_requests_use"), routing_key="for_contains_requests_use"),
    Queue("email_alert", Exchange("email_alert"), routing_key="email_alert"),
    Queue("certification_risk", Exchange("certification_risk"), routing_key="certification_risk"),
)
# 路由配置，任务和消息队列的映射关系
CELERY_ROUTES = {
    # '{定时/异步任务名称路径}':{
    #     'queue': '{指定推送的队列名, 不指定路由配置则使用默认的[celery]队列}',
    #     "routing_key": "{指定路由键}"
    # },

    # PDM器件编码，定时刷新数据调用远程外部接口
    'blog_dj.apps.PDMPreferredMaintenance.tasks.update_remote_device_code':{
        'queue': 'for_contains_requests_use',
        "routing_key": "for_contains_requests_use",
    },
    # 异步发送xxx消息
    'blog_dj.utils.EspaceMessage.async_send':{
        'queue': 'asynchronous_task',
        "routing_key": "asynchronous_task",
    },
    # 预警提醒发送espace消息
    'blog_dj.apps.WebPage.send_email.tasks.email_alert': {
        'queue': 'email_alert',
        "routing_key": "email_alert",
    },
    # 认证拦截预警，每分钟执行一次
    'blog_dj.apps.ComplianceCertification.tasks.update_certification_risk': {
        'queue': 'certification_risk',
        "routing_key": "certification_risk",
    },

}
