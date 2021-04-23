import time


def log_decorator(*args, **kwargs):
    """ 装饰器带参 """
    def log_time(func):
        def _log_time(*args, **kwargs):

            print('装饰器参数:', args, kwargs)
            start_time = time.time()  # 程序开始时间

            print('被装饰函数名: ', func)
            print('被装饰函数参数: ', *args, **kwargs)
            func_res = func(*args, **kwargs)
            print('被装饰函数返回值: ', func_res)

            over_time = time.time()  # 程序结束时间
            total_time = over_time - start_time
            print('程序耗时%.8f秒' % total_time)

            return func_res
        return _log_time
    return log_time



def execute_time(func):
    """ 计算程序执行时间 """

    def inner(*args, **kwargs):
        print('被装饰函数的参数:', args, kwargs)
        start_time = time.time()  # 程序开始时间

        print('被装饰函数名: ', func)
        func_res = func(*args, **kwargs)
        print('被装饰函数返回结果: ', func_res)

        over_time = time.time()  # 程序结束时间
        total_time = over_time - start_time
        print('程序耗时 %.8f 秒' % total_time)

        return func_res

    return inner


@execute_time
def test_fun1(num):
    for i in range(num):
        s = i * i
        print(s)
        time.sleep(0.5)
    return 'ok'

@log_decorator('装饰器的参数')
def test_fun2(num):
    for i in range(num):
        s = i * i
        print(s)
        time.sleep(0.5)
    return 'ok'



if __name__ == '__main__':
    # test_fun1(5)
    test_fun2(5)
