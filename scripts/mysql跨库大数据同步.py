# -*- coding: utf-8 -*-
""" 
@Author: wwx800191
@Date: 2021/3/3
@Desc: 100万以上数据传输/同步
"""
import pymysql
import datetime
import pandas as pd
import sqlalchemy.types as types
from sqlalchemy import create_engine

""" 发料数据 data """
config_1 = {
    'driver': 'mysql+mysqldb',
    'user': 'root',
    'password': '[pwd]',
    'host': '[ip1]',
    'port': 3306,
    'db': '[db_name]',    # 源数据库
    'charset': 'utf8',
}

config_2 = {
    'driver' : 'mysql+mysqldb',
    'user' : 'root',
    'password' : '[pwd2]',
    'host' : '[IP2]',
    'port' : 3306,
    'db' : '[db_name]',   # 目标数据库
    'charset' : 'utf8',
}

engine_1 = create_engine(
    "{}://{}:{}@{}:{}/{}?charset={}".format(
        config_1['driver'],
        config_1['user'],
        config_1['password'],
        config_1['host'],
        config_1['port'],
        config_1['db'],
        config_1['charset']), pool_pre_ping=True
    )

engine_2 = create_engine(
    "{}://{}:{}@{}:{}/{}?charset={}".format(
        config_2['driver'],
        config_2['user'],
        config_2['password'],
        config_2['host'],
        config_2['port'],
        config_2['db'],
        config_2['charset']), pool_pre_ping=True
    )


def set_d_type_dict(df):
    type_dict = {}
    for i, j in zip(df.columns, df.dtypes):
        if "object" in str(j):
            type_dict.update({i: types.NVARCHAR(255)})
        if "float" in str(j):
            type_dict.update({i: types.DECIMAL(19, 2)})
        if "int" in str(j):
            type_dict.update({i: types.INTEGER})
    return type_dict

def today(format='%Y-%m-%d'):
    return datetime.datetime.now().strftime(format)

def forward_day(date: str, days: int, format='%Y-%m-%d') -> str:
    """
    计算某个日期向前推n天的日期
    例: 2020-12-20 向前推 5 天, 返回的日期是 2020-12-15
    """
    forward = datetime.date(*map(int, date.split('-'))) - datetime.timedelta(days=days)
    return forward.strftime(format)

def read_sql_table(table, engine):
    return pd.read_sql_table(table, engine)

def read_sql(sql, engine, chunksize=10000, params=None):
    return pd.read_sql(sql, engine, chunksize=chunksize, params=params)

def save(df, table, engine, if_exist='append', chunksize=10000, index=False):
    type_dict = set_d_type_dict(df)
    df.to_sql(table, engine, if_exists=if_exist, index=index, dtype=type_dict, chunksize=chunksize)


if __name__ == '__main__':

    st_date = forward_day(today(), 30)
    ed_date = today()

    print(st_date)
    print(ed_date)
    sql = f"""SELECT * FROM [table] WHERE [col_time] >= '{st_date}' AND [col_time] < '{ed_date}' """
    print(sql)
    df_read = read_sql(sql, engine_1)

    for i, df_write in enumerate(df_read, 1):
        print(f'第{i}次')
        print(df_write)
        save(df_write, '[table_name]', engine_2, )
        print(f'第{i}次 完成...{df_write.shape[0]}条')





    print('-- over --')
