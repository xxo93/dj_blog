# -*- coding: utf-8 -*-
def logit1(func):
    def with_logging(*args, **kwargs):
        print(func.__name__)
        print(func.__doc__)
        return func(*args, **kwargs)

    return with_logging


@logit1
def addition_func(x):
    """ 测试1: Do some math."""
    return x + x


result = addition_func(4)

# 不使用 @wraps(func) 装饰后，函数名类型会变: <function logit.<locals>.with_logging at 0x00000172968C70D0>
print(addition_func)

# ##########################################
print('-----------------------------------')
# ##########################################

from functools import wraps


def logit2(func):
    @wraps(func)
    def with_logging(*args, **kwargs):
        print(func.__name__)
        print(func.__doc__)
        return func(*args, **kwargs)

    return with_logging


@logit2
def addition_func(x):
    """ 测试2: Do some math. """
    return x + x


result2 = addition_func(6)
# 使用 @wraps(func) 装饰后，函数名类型不变: <function addition_func at 0x0000025DC73170D0>
print(addition_func)
