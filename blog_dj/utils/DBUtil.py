import os
import traceback

from django.conf import settings
from django.db import models
import pandas as pd
import sqlalchemy.types as types
from sqlalchemy import create_engine

from PyVbord.utils.PropertiesUtil import prop

"""      
@Desc : SQL工具类
"""
class DbUtil(object):
    def __init__(self, file_name=None, config=None, conn_name=None, db_name=None):
        if conn_name:
            config = dict()
            conf = settings.DATABASES.get(conn_name)
            config['host'] = conf['HOST']
            config['port'] = conf['PORT']
            config['database'] = conf['NAME']
            config['user'] = conf['USER']
            config['password'] = conf['PASSWORD']
            config['charset'] = 'utf8'
            config['driver'] = 'mysql+mysqldb'
        if not config:
            config_file = 'PyVbord/static/{}'.format(file_name)
            properties = prop.get_config_dict(config_file)
            config = {
                'host': properties['host'],
                'port': int(properties['port']),
                'database': properties['database'],
                'user': properties['user'],
                'password': properties['password'],
                'charset': properties['charset'],
                'driver': properties['driver'],
            }
        if db_name:
            config['database'] = db_name
        self.engine = create_engine(
            "{}://{}:{}@{}:{}/{}?charset={}".format(config['driver'], config['user'], config['password'],
                                                    config['host'], config['port'], config['database'],
                                                    config['charset']), pool_pre_ping=True, pool_size=100,
            pool_recycle=3600, max_overflow=100)

    def read_sql_table(self, table):
        return pd.read_sql_table(table, self.engine)

    def read_sql(self, sql, params=None):
        return pd.read_sql(sql, self.engine, params=params)

    def save(self, df, table, if_exist='append', chunksize=100, index=False):
        type_dict = set_d_type_dict(df)
        df.to_sql(table, self.engine, if_exists=if_exist, index=index, dtype=type_dict, chunksize=chunksize)

    def save_replace(self, df, table, if_exist='replace', chunksize=100, index=False):
        df.to_sql(table, self.engine, if_exists=if_exist, index=index, chunksize=chunksize)

    def query(self, sql):
        return self.engine.execute(sql).fetchall()

    def query_single(self, sql):
        return self.engine.execute(sql).fetchone()

    def update(self, sql):
        return self.engine.execute(sql)

    def update_prepared_statement(self, prepared_sql, params):
        """ 对SQL语句预编译，避免SQL语句中含有%等特殊符号时写入报错
            参考用法：
            db = DBUtil('...')
            sql = text("insert issue_info_library_copy2 set `value` = :value,field = :field,issue_id = :issue_id")
            params = {
              'value': 'value', 'field': 1, 'issue_id': 'issue_id'
            }
            db.update_prepared_statement(prepared_sql, params)
        """
        return self.engine.execute(prepared_sql, params)

    def batch_operator(self, df, table_name, batch_size, update=False, updates=None, exclude_columns=[]):
        """
        批量插入、更新操作
        :param df:
        :param table_name:
        :param batch_size: 一次插入的条数
        :param update: 是否更新
        :param updates: 更新语句
        :param exclude_columns: updates未指定时执行批量更新的时候要排除的列，解决某些情况下唯一键冲突导致入库失败的问题
        :return:
        """
        if len(df) == 0:
            return
        batch_num = int(len(df) / batch_size) + 1
        for i in range(batch_num):
            start = i * batch_size
            if start >= len(df):
                break
            chunk = df[start: start + batch_size]
            if update:
                self.update(
                    self.generate_update_sql(chunk, table_name, exclude_columns=exclude_columns, updates=updates))
            else:
                self.update(self.generate_insert_sql(chunk, table_name))

    def batch_save(self, df, table_name, batch_size=10000):
        """
        批量插入
        :param df:
        :param table_name:
        :param batch_size: 一次插入的条数
        :return:
        """
        self.batch_operator(df, table_name, batch_size)

    def batch_update(self, df, table_name, batch_size=10000, updates=None, exclude_columns=[]):
        """
        批量更新，利用MySQl on duplicate key语法，根据唯一建去重
        :param df:
        :param table_name
        :param batch_size
        :param updates
        :param exclude_columns: updates未指定时执行批量更新的时候要排除的列，解决某些情况下唯一键冲突导致入库失败的问题
        :return:
        """
        self.batch_operator(df, table_name, batch_size, True, updates, exclude_columns)

    @staticmethod
    def serialize_data(df):
        # 将nan转为None
        df = df.where(df.notnull(), None)
        for col, dtype in zip(df.columns, df.dtypes):
            if 'datetime' in dtype.name:
                df.loc[:, col] = df[col].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))
            elif 'date' in dtype.name:
                df.loc[:, col] = df[col].apply(lambda x: x.strftime('%Y-%m-%d'))
            elif 'object' in dtype.name:
                df.loc[:, col] = df[col].apply(lambda x: str(x) if x else x)
        if len(df.columns) == 1:
            col = df.columns.values[0]
            vals_str = "),(".join([f"'{x.strip()}'" for x in df[col].to_list()])
            data = f"({vals_str})"
        else:
            data = str(df.to_records(index=False).tolist())[1:-1]
        return data.replace('nan', 'null').replace('None', 'null').replace('%', '%%')

    def generate_update_sql(self, df, table_name, updates=None, exclude_columns=[]):
        columns = list(df.columns.values)
        cols = ",".join([f"`{x}`" for x in columns])
        if not updates:
            updates = ",".join([f"{x}=values({x})" for x in columns if x not in exclude_columns])
        data = self.serialize_data(df)
        sql = f"insert into `{table_name}` ({cols}) values {data} on duplicate key update {updates};"
        return sql

    def generate_insert_sql(self, df, table_name):
        """
        生成批量插入SQL的语句
        :param df:
        :param table_name: 表名
        :return:
        """
        columns = list(df.columns.values)
        cols = ",".join([f"`{x}`" for x in columns])
        data = self.serialize_data(df)
        sql = f"INSERT INTO `{table_name}` ({cols}) VALUES {data};"
        return sql


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


from PyVbord.utils.SphinxTool import SphinxQuerySet
class CustomerDBManager(models.Manager):
    """
    功能描述  : 自定义数据库管理类，用于实现数据表模型与数据库的映射关系
    
    CustomerDBManager使用案例:

    class MyTableModel(models.Model):
        use_db = 'special_db'  # core
        objects = CustomerDBManager()  # core
        field_1 = models.CharField(max_length=200)
        field_2...
    """

    def get_queryset(self):
        qs = super().get_queryset()
        # if `use_db` is set on model use that for choosing the DB
        if hasattr(self.model, 'use_db'):
            qs = qs.using(self.model.use_db)
        return qs

