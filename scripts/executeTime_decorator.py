import time

def log_decorator(*args,**kwargs):
    def log_time(func):
        def make_decorater(num):
            print('len(args):', len(args))
            print(args[0]) if len(args)>=1 else print('')

            start_time = time.time()  # 程序开始时间
            ret = func(num)
            over_time = time.time()  # 程序结束时间
            total_time = over_time - start_time

            print(args[1]) if len(args)>=2 else print('')
            print('程序耗时%.8f秒' %total_time)
            return ret
        return make_decorater
    return log_time


def execute_time(func):
    def int_time(*args, **kwargs):
        print('---')
        start_time = time.time()  # 程序开始时间
        ret = func(*args,**kwargs)
        over_time = time.time()   # 程序结束时间
        total_time = over_time - start_time
        print('+++')
        print('程序耗时%s秒' % total_time)
        return ret
    return int_time


@log_decorator('开始')
def fun(num):
    for i in range(num):
        s =  i*i
        print(s)
        time.sleep(0.5)


if __name__ == '__main__':
    fun(5)

