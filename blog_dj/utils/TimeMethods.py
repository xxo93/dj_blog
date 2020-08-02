# -*- coding: utf-8 -*-
"""
关于时间的相关方法
"""
import arrow
import time
import pandas as pd

date_obj = arrow.now()


def excute_time(func):
    def int_time(*args, **kwargs):
        start_time = time.time()
        ret = func(*args, **kwargs)
        total_time = time.time() - start_time
        print('程序耗时*.8f' % total_time)
        return ret
    return int_time


def timestamp():
    """ 时间戳 """
    return time.time()
    

def consecutive_ym(m:int=0, n:int=0, char:str=None) -> list:
    """
    描述：返回从当月往前推m个月、往后推n个月的连续月份数组
    1. 默认格式: 2020年12月
    2. 自定格式: 2020-12、 2020/12 ...
    """
    today = datetime.date.today()

    curr_month = today.month    # 当前月份
    year = today.year - int(((m + 12 - curr_month)/12)) # 推算年份

    for i in range(m):
        curr_month -= 1
        if curr_month < 1:
            curr_month = 12
    month = curr_month  # 推算月份

    ym_default = [str(year) + "年" + str(month) + "月" ]
    ym_customize = [str(year) + f"{char}" + str(month).zfill(2)]

    for j in range(m+n):
        month += 1
        if month > 12:
            month = 1
            year = year + 1
        date_default = str(year) + "年" + str(month) + "月"
        date_customize = str(year) + f"{char}" + str(month).zfill(2)

        ym_default.append(date_default)
        ym_customize.append(date_customize)

    if char is not None:
        return  ym_customize

    return ym_default


def range_day(start_date: str, end_date: str) -> int:
    """
    计算两个日期之间相差的天数
    :param start_date: 起始时间 (xxxx-xx-xx)
    :param end_date: 结束时间 (xxxx-xx-xx)
    :return: 相差天数
    """
    start = datetime.date(*map(int, start_date.split('-')))
    end = datetime.date(*map(int, end_date.split('-')))
    return (end - start).days


def forward_day(date: str, days: int) -> str:
    """
    计算某个日期向前推n天的日期
    例: 2020-12-20 向前推 5 天, 返回的日期是 2020-12-15
    """
    forward = datetime.date(*map(int, date.split('-'))) - datetime.timedelta(days=days)
    return forward.strftime('%Y-%m-%d')


def back_day(date: str, days: int) -> str:
    """
    计算某个日期向前推n天的日期
    例: 2020-12-20 向后推 5 天, 返回的日期是 2020-12-25
    """
    back = datetime.date(*map(int, date.split('-'))) + datetime.timedelta(days=days)
    return back.strftime('%Y-%m-%d')


def current_time(format="YYYY-MM-DD HH:mm:ss"):
    return date_obj.format(format)


def now(days=0, format="YYYY-MM-DD HH:mm:ss"):
    return date_obj.shift(days=days).format(format)


def today(days=0, format="YYYY-MM-DD"):
    return date_obj.shift(days=days).format(format)


def month_shift(months=0, format="YYYY-MM"):
    return date_obj.shift(months=months).format(format)


def year_shift(years=0, format="YYYY"):
    return date_obj.shift(years=years).format(format)


def struct_time():
    return time.localtime(time.time())


def datetime2str(dt):
    if isinstance(dt, datetime.datetime):
        return dt.strftime('%Y-%m-%d')
    return dt


def str2datetime(date):
    return datetime.datetime.strptime(date, '%Y-%m-%d')


# 待完善...
def getTheMonth(date:str, n:int, format='%Y%m')->str:
    """
    获取指定月份 往前推n个月 的月份信息
    :param date: str
    :param n:
    :param format:
    :return: str
    """
    date = datetime.datetime.strptime(date, format)
    month = date.month
    year = date.year
    for i in range(n):
        if month == 1:
            year -= 1
            month = 12
        else:
            month -= 1
    return datetime.date(year, month, 1).strftime(format)
        
        
