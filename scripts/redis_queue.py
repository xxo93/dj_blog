import redis

"""部署服务器时,需要更改的变量"""
PAGE_HOST = "http://{前端域名}:8088/"
BACKEND_HOST = "http://{后端ip}:8000/"

# REDIS地址
REDIS_HOST="127.0.0.1"
# REDIS_HOST="localhost"
# REDIS_HOST="10.43.246.55"
REDIS_PORT = 6379

WARNING_TASK_QUEUE_CONFIG = {
    'host': REDIS_HOST, 'port': REDIS_PORT, 'db': 3
}


class RedisQueue(object):

    def __init__(self, name='queue'):
        self.pool = redis.ConnectionPool(**WARNING_TASK_QUEUE_CONFIG)
        self.connection = redis.Redis(connection_pool=self.pool)
        self.queue_name = name

    def r_push(self, item):
        # 向队列右边添加一个新元素
        self.connection.rpush(self.queue_name, item)

    def l_range(self):
        # 返回队列所有元素
        return self.connection.lrange(self.queue_name, 0, self.q_size())

    def l_first(self):
        # 返回队列左边第一个元素，没有则返回None
        item = self.connection.lindex(self.queue_name, 0)
        return item

    def q_size(self):
        return self.connection.llen(self.queue_name)

    def l_pop(self):
        # 删除并返回队列左边第一个元素，没有则返回None
        item = self.connection.lpop(self.queue_name)
        return item

    def l_rem(self, item):
        # 移除某个指定元素, 返回删除的数量
        return self.connection.lrem(self.queue_name, 0, item)

    def keys(self):
        # 查看3号库存在的keys列表
        return self.connection.keys()


warning_queue = RedisQueue(name='warning_type')
