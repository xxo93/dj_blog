import gc
import datetime
import warnings
import pandas as pd
from sys import maxsize
from typing import List
from django.conf import settings
from sqlalchemy.orm import Query
from django.db.models.query import QuerySet
from rest_framework.viewsets import ModelViewSet

from PyVbord.libs import sphinxapi

FLOAT_MAX_SIZE = float(maxsize)
host = settings.SPHINX_CONF['HOST']
port = settings.SPHINX_CONF['PORT']
full_text_name = settings.SPHINX_CONF['FULL_TEXT_NAME']
full_text_value = settings.SPHINX_CONF['FULL_TEXT_VALUE']


class SphinxQuerySet(sphinxapi.SphinxClient):

    def __init__(self, host=host, port=port, index='*', max_connect_time=150.0, max_match=2000, *args, **kwargs):
        """
        :param host: sphinx服务ip
        :param port: sphinx服务端口
        :param index: 使用的索引名称,'*'表示从所有的索引中查找
        :param max_connect_time: 链接最大时间设置
        :param max_match: 查询结果返回的最大匹配数
        :param kwargs:
        """
        super(SphinxQuerySet, self).__init__()
        self.SetServer(host, port)
        # 查询链接超时设置为60秒
        self.SetConnectTimeout(max_connect_time)
        # 设置常开
        self.Open()
        # 用于保存查询过滤语句
        self.query_dict = {
            "and": [],
            "or": []
        }
        self.index = index
        self.group_by_column = None
        self.max_match = max_match
        # 设置最大匹配数（默认结果只返回20条，有时候会漏信息）
        self.set_limits(0, self.max_match, self.max_match)
        # 浮点数最小精度
        self.float_precision_accuracy = 1e-15
        # 全文索引字段的名称，用于辅助“!=”查询结果
        self.full_text_name = full_text_name
        self.full_text_value = full_text_value

    def __del__(self):
        # 对象销毁时，一定要关闭长链接
        self.Close()
        gc.collect()

    def add_or(self, query):
        """使用or操作连接"""
        if not query:
            return self
        if isinstance(query, (list, tuple)):
            self.query_dict['or'].extend(query)
        else:
            self.query_dict['or'].append(query)
        return self

    def add_and(self, query):
        """
        使用and连接
        """
        if not query:
            return self
        if isinstance(query, (list, tuple)):
            self.query_dict['and'].extend(query)
        else:
            self.query_dict['and'].append(query)
        return self

    def _get_queries(self):
        or_list = self.query_dict['or'].copy()
        or_string = ' | '.join(or_list)
        and_list = self.query_dict['and'].copy()
        if or_string:
            and_list.append('(' + or_string + ')')
        query_string = ' & '.join(and_list)
        query = self.Query(query_string, self.index)
        total = query['total_found']
        return query, total

    def set_limits(self, offset, limit, max_matches):
        self.SetLimits(offset, limit, max_matches)
        return self

    def _get_total(self):
        _, total = self.set_limits(0, 1, 1)._get_queries()
        # 避免影响接下来的链式查询结果
        self.set_limits(0, self.max_match, self.max_match)
        return total

    def filter(self, and_=True, **kwargs):
        """
        帮助：1. sql_attr_*中配置的字段只能在sphinx-api中过滤
             2. sql_field_*中配置的字段既能在sphinx-api中过滤又能在扩展模式中过滤
             3. api中过滤查询的效率是扩展模式中查询效率的两倍,应尽量的使用api过滤查询获取结果; 扩展模式作为sphinx-api方式的补充适合查询复杂的条件,但是效率会低一些
        将字典对象解析成API接口查询(对于API能够过滤的属性，最好在配置文件sql_query索引源的时候，把对应属性写两个（例如:select bom_code, bom_code_ext ....）)
        说明：1.and 查询支持(__gt, __gte, __lt, __lte, __range, __in, __exclude, __contains, __startswith, __endswith, 以及全等于操作)
             2.or 查询支持(__in, __exclude, __contains, __startswith, __endswith, 以及全等于操作)
        :param kwargs: 沿用django的Q对象查询方式
        :return:
        """
        if and_:
            query_list = self.query_dict['and']
        else:
            query_list = self.query_dict['or']
        for column, val in kwargs.items():
            # and连接的逻辑，sphinx-api暂时是只支持and连接的逻辑
            if and_:
                if column.endswith("__gt"):
                    column = column.replace("__gt", "")
                    if isinstance(val, int):
                        self.SetFilterRange(column, val + 1, maxsize)
                    elif isinstance(val, float):
                        self.SetFilterFloatRange(column, val + self.float_precision_accuracy, FLOAT_MAX_SIZE)
                    elif isinstance(val, datetime.datetime):
                        timestamps = int(datetime.datetime.timestamp(val))
                        self.SetFilterRange(column, timestamps + 1, maxsize)
                    else:
                        raise Exception('__gt只支持数值和时间范围查询')
                elif column.endswith("__gte"):
                    column = column.replace("__gte", "")
                    if isinstance(val, int):
                        self.SetFilterFloatRange(column, val, maxsize)
                    elif isinstance(val, float):
                        self.SetFilterFloatRange(column, val, FLOAT_MAX_SIZE)
                    elif isinstance(val, datetime.datetime):
                        timestamps = int(datetime.datetime.timestamp(val))
                        self.SetFilterRange(column, timestamps, maxsize)
                    else:
                        raise Exception('__gte只支持数值和时间范围查询')
                elif column.endswith("__lt"):
                    column = column.replace("__lt", "")
                    if isinstance(val, int):
                        self.SetFilterRange(column, -maxsize, val - 1)
                    elif isinstance(val, float):
                        self.SetFilterFloatRange(column, -FLOAT_MAX_SIZE, val - self.float_precision_accuracy)
                    elif isinstance(val, datetime.datetime):
                        timestamps = int(datetime.datetime.timestamp(val))
                        self.SetFilterRange(column, -maxsize, timestamps - 1)
                    else:
                        raise Exception('__lt只支持数值和时间范围查询')
                elif column.endswith("__lte"):
                    column = column.replace("__lte", "")
                    if isinstance(val, int):
                        self.SetFilterRange(column, -maxsize, val)
                    elif isinstance(val, float):
                        self.SetFilterFloatRange(column, -FLOAT_MAX_SIZE, val)
                    elif isinstance(val, datetime.datetime):
                        timestamps = int(datetime.datetime.timestamp(val))
                        self.SetFilterRange(column, -maxsize, timestamps)
                    else:
                        raise Exception('__lt只支持数值和时间范围查询')
                elif column.endswith("__range"):
                    column = column.replace("__range", "")
                    assert isinstance(val, (list, tuple)), "range 操作只能支持列表或者元祖容器"
                    start, end = val
                    if isinstance(start, int):
                        self.SetFilterRange(column, start, end)
                    elif isinstance(start, float):
                        self.SetFilterFloatRange(column, start, end)
                    elif isinstance(start, datetime.datetime):
                        start, end = datetime.datetime.timestamp(start), datetime.datetime.timestamp(end)
                        self.SetFilterFloatRange(column, start, end)
                    else:
                        raise Exception('__range只支持数值和时间范围查询')
                elif column.endswith("__in"):
                    column = column.replace("__in", "")
                    assert isinstance(val, (list, tuple, set)), "__in操作只能支持列表或者元组或集合容器"
                    if isinstance(val[0], str):
                        self.SetFilterStringList(column, val)
                    elif isinstance(val[0], int):
                        self.SetFilter(column, val)
                    else:
                        raise Exception('__in只支持数值和字符串查询')
                elif column.endswith("__exclude"):
                    column = column.replace("__exclude", "")
                    query_list.append(f'((@{self.full_text_name} {self.full_text_value}) & (@{column} !"^{val}$"))')
                elif column.endswith("__contains") or column.endswith("__icontains"):
                    column = column.replace("__contains", "").replace("__icontains", "")
                    query_list.append(f'(@{column} {val})')
                elif column.endswith("__startswith"):
                    column = column.replace("__startswith", "")
                    query_list.append(f'(@{column} ^{val})')
                elif column.endswith("__endswith"):
                    column = column.replace("__endswith", "")
                    query_list.append(f'(@{column} {val}$)')
                else:
                    if isinstance(val, str):
                        self.SetFilterString(column, val)
                    elif isinstance(val, int):
                        self.SetFilter(column, [val])
                    elif isinstance(val, datetime.datetime):
                        timestamps = int(datetime.datetime.timestamp(val))
                        self.SetFilter(column, [timestamps])
                    else:
                        raise Exception('精确查询只支持日期, 数字, 字符串查询')
            # or连接查询逻辑
            else:

                if column.endswith("__in"):
                    column = column.replace("__in", "")
                    assert isinstance(val, (list, tuple, set)), "__in操作只能支持列表或者元组或集合容器"
                    if isinstance(val[0], (str, int)):
                        query_list.append('(' + '|'.join([f"(@{column} ^{v}$)" for v in val]) + ')')
                    else:
                        raise Exception('__in只支持数值和字符串查询')
                elif column.endswith("__exclude"):
                    column = column.replace("__exclude", "")
                    query_list.append(f'((@{self.full_text_name} {self.full_text_value}) & (@{column} !"^{val}$"))')
                elif column.endswith("__contains") or column.endswith("__icontains"):
                    column = column.replace("__contains", "").replace("__icontains", "")
                    query_list.append(f'(@{column} {val})')
                elif column.endswith("__startswith"):
                    column = column.replace("__startswith", "")
                    query_list.append(f'(@{column} ^{val})')
                elif column.endswith("__endswith"):
                    column = column.replace("__endswith", "")
                    query_list.append(f'(@{column} {val}$)')
                else:
                    if isinstance(val, datetime.datetime):
                        val = int(datetime.datetime.timestamp(val))
                    query_list.append(f"(@{column} ^{val}$)")

                for each in ("__gt", "__gte", "__lt", "__lte", "__range"):
                    if column.endswith(each):
                        warnings.warn(f"`or` 连接查询不支持{each}操作, {each}操作将被忽略")
            # and 和 or 都支持的操作
            # if column.endswith("__exclude"):
            #     column = column.replace("__exclude", "")
            #     query_list.append(f'((@{self.full_text_name} {self.full_text_value}) & (@{column} !"^{val}$"))')
            # elif column.endswith("__contains") or column.endswith("__icontains"):
            #     column = column.replace("__contains", "").replace("__icontains", "")
            #     query_list.append(f'(@{column} {val})')
            # elif column.endswith("__startswith"):
            #     column = column.replace("__startswith", "")
            #     query_list.append(f'(@{column} ^{val})')
            # elif column.endswith("__endswith"):
            #     column = column.replace("__endswith", "")
            #     query_list.append(f'(@{column} {val}$)')
        return self

    def reset_filter(self):
        """
        重置搜索条件
        :return:
        """
        self._reset_select()
        self.ResetFilters()
        self.ResetGroupBy()
        self.ResetQueryFlag()
        self.ResetOuterSelect()
        self.query_dict = {
            "and": [],
            "or": []
        }

    def values(self, *args):
        """
        获取结果
        :param args:
        :return: map迭代对象
        """
        query, _ = self._get_queries()
        if args:
            return map(
                lambda x: {**{each: x['attrs'][each] for each in args}, **{'id': x['id']}},
                query['matches']
            )
        else:
            return map(
                lambda x: {**x['attrs'], **{'id': x['id']}},
                query['matches']
            )

    def distinct(self, *args):
        result = self.values(*args)
        df_result = pd.DataFrame(result)
        # 去重
        return df_result.drop_duplicates().to_dict(orient="records")

    def group_by(self, group_by_column):
        self.group_by_column = group_by_column
        return self

    def order_by(self, attr, ascending=True):
        sort_mode = sphinxapi.SPH_SORT_ATTR_ASC if ascending else sphinxapi.SPH_SORT_ATTR_DESC
        self.SetSortMode(sort_mode, attr)
        return self

    def count(self, ascending=True):
        """
        解释：
            类似于sql中：select count(*) as c, group_by_column from `table_name` group by group_by_column
        :param group_by_column: 分组列
        :return:
        """
        group_by_column = self.group_by_column if self.group_by_column else 'id'
        self.group_by_column = None
        if group_by_column == 'id':
            return self._get_total()
        self.SetGroupBy(group_by_column, sphinxapi.SPH_GROUPBY_ATTR, f'@group {"desc" if not ascending else "asc"}')
        res = list(self.values(group_by_column, '@count'))
        self.ResetGroupBy()
        for each in res:
            each.pop('id')
        return res

    def distinct_count(self, distinct_column: str, ascending=True):
        """
        解释：
            类似于sql中：select count(distinct column) as c, group_by_column from `table_name` group by group_by_column
        :param group_by_column: 分组列
        :param column: 统计列
        :return:
        """
        group_by_column = self.group_by_column if self.group_by_column else 'id'
        self.group_by_column = None
        if group_by_column == 'id':
            return self._get_total()
        self.SetGroupBy(group_by_column, sphinxapi.SPH_GROUPBY_ATTR, f'@distinct {"desc" if not ascending else "asc"}')
        self.SetGroupDistinct(distinct_column)
        res = list(self.values(group_by_column, '@distinct'))
        self.ResetGroupBy()
        for each in res:
            each.pop('id')
        return res

    def _agg(self, type_, column, column_alias, ascending=True):
        """
        :param type_:
        :param column: 分组列
        :param column_alias: 分组聚合后的别名
        :param ascending: 是否为升序排列
        :return:
        """
        type_ = type_.upper()
        if not self.group_by_column:
            raise RuntimeError('请指定分组列')
        if not column_alias:
            column_alias = f"{column}_agg_alias"
        self.SetSelect(f"*, {type_}({column}) as {column_alias}")
        self.SetGroupBy(
            self.group_by_column, sphinxapi.SPH_GROUPBY_ATTR, f'@groupby {"desc" if not ascending else "asc"}')
        res = list(self.values(self.group_by_column, column_alias))
        self.ResetGroupBy()
        for each in res:
            each.pop('id')
        return res

    def sum(self, sum_column, sum_column_alias=None, ascending=True):
        return self._agg('sum', sum_column, sum_column_alias, ascending)

    def avg(self, avg_column, avg_column_alias=None, ascending=True):
        return self._agg('avg', avg_column, avg_column_alias, ascending)

    def max(self, max_column, max_column_alias=None, ascending=True):
        return self._agg('max', max_column, max_column_alias, ascending)

    def min(self, min_column, min_column_alias=None, ascending=True):
        return self._agg('min', min_column, min_column_alias, ascending)

    def set_select(self, expression):
        """
        复杂查询语句
        :param expression: 查询语法，具体请参考官方文档：http://sphinxsearch.com/
        :return:
        """
        self.SetSelect(expression)
        return self

    def _reset_select(self):
        self._select = sphinxapi.bytes_str('*')

    def execute(self, query_string):
        """
        扩展模式语句查询
        :param query_string:
        :return:
        """
        res = self.Query(query_string, self.index)
        return res

    def _get_paginated_id(self, page, page_size) -> (List[int], int):
        """
        获取分页源数据的id和总数量的字典组合
        :param page:
        :param page_size:
        :return:
        """

        limit = page_size
        offset = (page - 1) * page_size
        total = self.count()
        results = self.set_limits(offset, limit, min(limit + offset, total)).values()
        # results = self.set_limits(offset, limit, limit + offset).values()
        self.set_limits(0, 1000, self.max_match)
        ids = [result['id'] for result in results]
        return ids, total

    def get_paginated_data(self, page, page_size, sql_or_queryset, conn=None):
        """
        :param page:
        :param page_size:
        :param sql_or_queryset: 纯sql格式为：select col1, col2... from table1 join table2 where table1.id
        :param conn:
        :return: json格式的表格数据
        """
        ids, total = self._get_paginated_id(page, page_size)
        if total == 0:
            return {"results": [], "count": total}
        # 纯sql处理方式
        if isinstance(sql_or_queryset, str):
            if not conn:
                raise RuntimeError('用纯sql查询时, 请指定查询连接')
            # 拼接完整的sql
            sql_or_queryset = sql_or_queryset + f" in ({','.join(['%s'] * (page_size if page * page_size < total else total % page_size))})"
            with conn.cursor() as cur:
                cur.execute(sql_or_queryset, tuple(ids))
                col_names = [desc[0] for desc in cur.description]
                results = []
                for each in cur.fetchall():
                    results.append(dict(zip(col_names, each)))
        # django的QuerySet处理方式
        elif isinstance(sql_or_queryset, QuerySet):
            results = sql_or_queryset.filter(id__in=ids).values()
        # sqlalchemy中的orm对象处理方式
        elif isinstance(sql_or_queryset, Query):
            results = sql_or_queryset.filter(sql_or_queryset.id.in_(ids)).all()
        else:
            raise RuntimeError('只能用sql, QuerySet, Query获取数据')
        return {"results": results, "count": total}


class SphinxModelViewSet(ModelViewSet):
    def get_queryset(self):
        queryset = super(SphinxModelViewSet, self).get_queryset()
        model = self.queryset.model
        index_name = getattr(model, 'sphinx_index_name', '*')
        setattr(queryset, 'sphinx_query', SphinxQuerySet(index=index_name))
        return queryset


class SphinxManagerDescriptor:

    def __init__(self, manager):
        self.manager = manager

    def __get__(self, instance, cls=None):
        if instance is not None:
            raise AttributeError("Manager isn't accessible via %s instances" % cls.__name__)

        return self.manager


if __name__ == '__main__':
    import pymysql

    s = SphinxQuerySet('10.64.234.212', 9312, 'dist_online_quality__t_inv_record')
    s_queryset = s.filter(id__in=[6, 8])
    print(s_queryset.values())
    s_queryset = s.filter(region='中国地区部')  # 6.809
    # 查询结果
    print(list(s_queryset.values()))
    print(list(s_queryset.values('board_name', 'barcode', 'region')))
    # 查询count(*)
    print(s_queryset.group_by('board_name').count(ascending=False))
    # 聚合查询count(distinct column)
    print(s_queryset.group_by('board_name').distinct_count('barcode', ascending=False))
    # 分页查询例子
    sql = """
                select t_inv_record.id, data_set,region,country,city,operator_group as groups,operator,net_meta_name as site_name,carbet_num,frame_num,slot_num,hardware_type,t_inv_record.platform as HPID,net_meta_type,net_meta_fdn,bios_version,ext_bios_version,t_inv_record.board_name as board_name_stock,t_board_info_small.board_name as board_name,t_board_info_small.board_type as board_type,last_serve_time,manufacture_date,ext_date,asset_serial_num as barcode,assets_unit_flag,assets_unit_type,pub_num,bom_code,t_board_info_small.bbom as make_code,t_board_info_small.freq_band as bands,t_board_info_small.platform as hardware_platform,t_board_info_small.product as product_belong_to,t_board_info_small.alias as special_note,lan_version,logic_version,mbus_version,special_info,belong_modu_num,port,board_slot_pos,software_version,gusset_slot_num,asset_unit_pos_info,user_friend_name,supply_name,asset_belong_type,asset_unit_type_code,hardware_version,work_mode,online_date,retire_date,refresh_date,is_have_flt_log, add_time from t_inv_record left join t_board_info_small on `t_inv_record`.`make_code`=t_board_info_small.bbom
                where t_inv_record.id 
            """
    conn = pymysql.connect(
        host='xx.xx.xxx.xxx',
        user='root',
        password='[pwd]',
        db='db_name',
        port=3306
    )
    r1 = s.filter(country='广东', operator='中国移动').order_by('board_name', ascending=False).get_paginated_data(10, 10,
                                                                                                            sql_or_queryset=sql,
                                                                                                            conn=conn)
    r2 = s.filter(country='广东', operator='中国移动').order_by('board_name', ascending=False).get_paginated_data(11, 10,
                                                                                                            sql_or_queryset=sql,
                                                                                                            conn=conn)
    r3 = s.filter(country='广东', operator='中国移动').order_by('board_name', ascending=False).get_paginated_data(10, 20,
                                                                                                            sql_or_queryset=sql,
                                                                                                            conn=conn)
    print(r1['count'], r2['count'], r3['count'])
    print(r1['results'] + r2['results'])
    print(r3['results'])
    print(r1['results'] + r2['results'] == r3['results'])
