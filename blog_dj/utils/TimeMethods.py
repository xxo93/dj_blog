# -*- coding: utf-8 -*-
"""
关于时间的相关方法
"""
import arrow
import time
import datetime
import calendar
from dateutil.relativedelta import relativedelta

import pandas as pd


def execute_time(func):
    def int_time(*args, **kwargs):
        start_time = time.time()  # 程序开始时间
        ret = func(*args,**kwargs)
        total_time = time.time() - start_time
        print('程序耗时%.8f秒' % total_time)
        return ret
    return int_time


def timestamp():
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


def forward_day(date: str, days: int, format='%Y-%m-%d') -> str:
    """
    计算某个日期向前推n天的日期
    例: 2020-12-20 向前推 5 天, 返回的日期是 2020-12-15
    """
    forward = datetime.date(*map(int, date.split('-'))) - datetime.timedelta(days=days)
    return forward.strftime(format)


def back_day(date: str, days: int, format='%Y-%m-%d') -> str:
    """
    计算某个日期向前推n天的日期
    例: 2020-12-20 向后推 5 天, 返回的日期是 2020-12-25
    """
    back = datetime.date(*map(int, date.split('-'))) + datetime.timedelta(days=days)
    return back.strftime(format)


def current_time(format="YYYY-MM-DD HH:mm:ss"):
    date_obj = arrow.now()
    return date_obj.format(format)


def now(days=0, format="YYYY-MM-DD HH:mm:ss"):
    date_obj = arrow.now()
    return date_obj.shift(days=days).format(format)


def today(days=0, format="YYYY-MM-DD"):
    date_obj = arrow.now()
    return date_obj.shift(days=days).format(format)


def month_shift(months=0, format="YYYY-MM"):
    date_obj = arrow.now()
    return date_obj.shift(months=months).format(format)


def year_shift(years=0, format="YYYY"):
    date_obj = arrow.now()
    return date_obj.shift(years=years).format(format)


def struct_time():
    return time.localtime(time.time())


def datetime2str(dt, format='%Y-%m-%d'):
    if isinstance(dt, datetime.datetime):
        return dt.strftime(format)
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


def get_current_month_date_range():
    """
    获取当前月份的日期范围
    :return:
    """
    day_now = time.localtime()
    date_start_str = '%s-%s-01' % (day_now.tm_year, day_now.tm_mon)
    w_day, month_range = calendar.monthrange(day_now.tm_year, day_now.tm_mon)
    date_end_str = '%s-%s-%s' % (day_now.tm_year, day_now.tm_mon, month_range)
    return date_start_str, date_end_str


def get_date_range_by_year_and_month(year: int = datetime.datetime.now().year,
                                     month: int = datetime.datetime.now().month) -> tuple:
    """
    :param year: 年份 int，默认为当年。eg: 2021
    :param month: 月份 int，默认为当月。eg: 4
    :return: 返回该月份的第1天和最后1天日期。eg: ('2021-04-01', '2021-04-30')
    """
    w_day, month_range = calendar.monthrange(year, month)
    month = str(month).zfill(2)
    return "%s-%s-01" % (year, month), "%s-%s-%s" % (year, month, month_range)


def get_current_6_month_forward_range():
    """
    获取当前月及往前的6个月的年月组合列表
    :return: eg  [(2020, 3), (2020, 4), (2020, 5), (2020, 6), (2020, 7), (2020, 8)]
    """
    month_lis = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
    now_time = time.localtime()
    cur_year = now_time.tm_year
    cur_month = now_time.tm_mon

    data = []
    if cur_month - 6 >= 0:
        for m in month_lis[cur_month-6: cur_month]:
            data.append((cur_year, m))
    else:
        for m in month_lis[cur_month - 6:]:
            data.append((cur_year - 1, m))
        for m in month_lis[:cur_month]:
            data.append((cur_year, m))
    return data

def ran_month(value):
    """
    根据月份返回时间格式的月份范围, 例：
    :param: '202007'
    :return: [datetime.datetime(2020, 7, 1, 0, 0), datetime.datetime(2020, 8, 1, 0, 0)]
    """
    start = "".join([value[:4], '-', value[4:], '-01'])
    start = datetime.datetime.strptime(start, "%Y-%m-%d")
    return [start, start + relativedelta(months=+1)]


def get_date_list(begin_date: str, end_date: str, format='%Y-%m-%d') -> list:
    """
    根据输入日期范围生成日期列表, 例:
    :param begin_date: '20200803' 或 2020-08-03 或 '2020/08/03'
    :param end_date: '20200806' 或 '2020-08-06' 或 '2020/08/06'
    :param format: format
    :return: ['2020-08-03', '2020-08-04', '2020-08-05', '2020-08-06']
    """
    date_list = [x.strftime(format) for x in list(pd.date_range(start=begin_date, end=end_date))]
    return date_list


def get_month_list(month: str, input_format: str, output_format: str = None, forward: int = 0, backward: int = 0) -> list:
    """
    描述：根据月份返回之前m个月、之后n个月的连续月份数组
    :param month: '202107' 或 '2021-07' 或 '2021/07'
    :param input_format: '%Y%m' 或 '%Y-%m' 或 '%Y/%m'...
    :param output_format: None（默认与input_format相同）或'%Y%m' 或 '%Y-%m' 或 '%Y/%m'...
    :param forward: 前推月份
    :param backward: 后推月份
    """
    date = datetime.datetime.strptime(month, input_format)
    if not output_format:
        output_format = input_format
    month_list = [datetime.datetime.strftime(date, output_format)]

    year = date.year
    month = date.month
    for _ in range(forward):
        if month == 1:
            month = 12
            year -= 1
        else:
            month -= 1
        month_list.append(datetime.datetime.strftime(datetime.datetime(year, month, 1), output_format))
    year = date.year
    month = date.month
    for _ in range(backward):
        if month == 12:
            month = 1
            year += 1
        else:
            month += 1
        month_list.append(datetime.datetime.strftime(datetime.datetime(year, month, 1), output_format))
    month_list = sorted(list(set(month_list)))
    return month_list

