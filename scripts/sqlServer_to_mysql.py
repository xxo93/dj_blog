"""
备份目标表的原有数据并同步新数据至目标表

"""
import arrow
import pandas as pd
from sqlalchemy import create_engine


sqlserver_config = {
    'host': '{ip}',
    'port': 1433,
    'user': 'sa',
    'password': '{pwd}',
    'database': '{dbName}',
}


mysql_config = {
    'host': '{ip}',
    'port': 3306,
    'user': 'root',
    'password': '{pwd}',
    'database': '{dbName}',
}


"""
需要参数: 数据库配置信息, 数据表
"""
class SqlServer2Mysql(object):
    def __init__(self, sql_server, mysql):
        self.sql_server_engine = self.connect(sql_server, 'mssql+pymssql')
        self.mysql_engine = self.connect(mysql, 'mysql+pymysql')

        self.df_data = None
        self.to_table = None

    def run(self, table):

        self.read_original_table(table, self.sql_server_engine)
        print('源数据:\n ', self.df_data)

        self.to_table = self.add_underline(table)
        print('目标表: ', self.to_table)

        self.to_mysql(self.to_table, self.df_data, self.mysql_engine)

    def connect(self, config, mode):
        sql_server_connection_format = '{}://{}:{}@{}:{}/{}?charset=utf8'
        sql_server_connection_str = sql_server_connection_format.format(
            mode, config['user'], config['password'], config['host'],
            config['port'], config['database']
        )
        return create_engine(sql_server_connection_str, echo=False)

    def read_original_table(self, table, engine):
        self.df_data = pd.read_sql_table(table, engine)
        self.df_data.replace('None', '', inplace=True)
        self.df_data.rename(columns=self.get_columns_dict(), inplace=True)
        self.df_data.index = self.df_data.index + 1
        self.df_data.insert(0, 'id', self.df_data.index)

    def get_columns_dict(self):
        if self.df_data is not None:
            columns = self.df_data.columns.values.tolist()
            return dict(zip(columns, [col.lower() for col in columns]))
        else:
            return {}

    def to_mysql(self, table, df_data, mysql_con):
        self.backup_table(table, mysql_con)
        try:
            print('truncate_table:', table)
            self.truncate_table(table, mysql_con)
            df_data.to_sql(name=table, con=mysql_con, if_exists='append', index=False)
            print('to_mysql append over...')
        except:
            print('to_mysql replace:', table)
            df_data.to_sql(name=table, con=mysql_con, if_exists='replace', index=False)
            self.set_key(table, mysql_con)
            print('to_mysql replace over...')

    def backup_table(self, table, engine):
        print('backup table ...')
        now_time = arrow.now().format("YYYYMMDD_HHmmss")
        table_copy = f'{table}_{now_time}'  # 备份的表名
        with engine.connect() as con:
            bool = con.execute(f"SHOW TABLES LIKE '{table}'").fetchall()
            if len(bool)==0:
                # todo 创建数据表
                pass
            else:
                con.execute(f'CREATE TABLE IF NOT EXISTS `{table_copy}` LIKE `{table}`;')
                con.execute(f'INSERT INTO `{table_copy}` SELECT * FROM `{table}`;')

    def set_key(self, table, engine):
        with engine.connect() as con:
            con.execute(f'ALTER TABLE `{table}` ADD PRIMARY KEY (`id`) AUTO_INCREMENT;')

    def truncate_table(self, table, engine):
        with engine.connect() as con:
            con.execute(f'TRUNCATE TABLE `{table}`;')

    def drop_table(self, table, engine):
        with engine.connect() as con:
            con.execute(f'DROP TABLE `{table}`;')

    @staticmethod
    def add_underline(text: str) -> str:
        """
        :description: hump to underline
        :param text: t_TableTest
        :return: t_table_test
        """
        lst = []
        for index, char in enumerate(text):
            if char == '_':
                pass
            elif char.isupper() and index != 0:
                lst.append("_")
            lst.append(char)
        return "".join(lst).lower()


if __name__ == "__main__":
    sql_server_table = 't_work_order_trate'
    obj = SqlServer2Mysql(sqlserver_config, mysql_config)
    columns = obj.run(sql_server_table)


    print('-- over! --')
