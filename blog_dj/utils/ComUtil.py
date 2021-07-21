# -*- coding: utf-8 -*-
"""
封装共用的代码逻辑
"""
import asyncio
import datetime
import os
import re
import traceback
from collections import namedtuple

import aiomysql
import pymysql
from django.conf import settings
import pandas as pd
from sqlalchemy import create_engine

from PyVbord.apps.Commons.common_utils import log, error

celery_err_file = os.path.join(settings.LOG_PATH, 'celery_error.log')


def time_add(time, param, format='%Y-%m-%d %X'):
    """原时间上增加时间差
    @:param：dict，如 {'days': 1}
    """
    if isinstance(time, str):
        time = datetime.datetime.strptime(time, format)

    return time + datetime.timedelta(**param)


def get_db_config(db):
    """获取db的配置信息"""
    setting = settings.DATABASES[db]
    user = setting['USER']
    pwd = setting['PASSWORD']
    ip = setting['HOST']
    port = setting['PORT']
    dbname = setting['NAME']
    Config = namedtuple('config', ['user', 'pwd', 'ip', 'port', 'dbname'])
    db_config = Config(user=user, pwd=pwd, ip=ip, port=port, dbname=dbname)
    return db_config


def generate_set_sql(fields, set_str=''):
    """连表修改，生成update table set 后的内容
    @:param: fields :t1 表和t2表的字段映射,如果名字一样也可以为列表
    @:return: set_str：返回生成的字符串：如 t1.board_code=t2.code
    """
    if isinstance(fields, list):
        fields = {x: x for x in fields}

    for col1, col2 in fields.items():
        s = f't1.{col1}=t2.{col2}'
        set_str = ','.join([set_str, s])

    if set_str.startswith(','):
        set_str = set_str[1:]
    return set_str


def gen_s(n):
    a = ['%s'] * n
    return ",".join(a)


def split_str(value, ignore_white_space=False):
    if ignore_white_space:
        rule = '[，|,|\n|\t]'
    else:
        rule = '[，|,|\n| |\t]'
    value_list = re.split(rule, value)
    value_list = [each.strip() for each in value_list if each]
    return value_list


def build_content(body_content):
    """构造邮件内容
    @params：body_content 邮件内容主体"""
    head = """
            <head>
            <meta charset="UTF-8">
            <title>Title</title>
            </head>
            """
    body = body_content
    html = "<html>" + head + body + "</html>"
    return html


def obj_to_float(x):
    if x is None:
        return x

    try:
        res = float(x)
    except:
        res = to_float(x)
    return res


def to_float(s, n=2):
    """百分比字符串转浮点"""
    return round(float(s.rstrip('%')) * 0.01, n)


def to_percent(n, digit=1):
    """浮点数转百分比字符串"""
    return f'%.{digit}f%%' % (n * 100)


def fetchall_to_dict(cursor):
    """
    功能描述  : 将fetchall()获取结果转换为字典形式
    请求参数  : cursor
    返   回  : 查询结果
    """
    res = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
    return res


def record_exception(msg, e, file_path=celery_err_file):
    """记录celery任务异常日志"""
    error(f'{msg}:{e}')
    traceback.print_exc(file=open(file_path, 'a'))


def get_full_user(request):
    return f"{request.user.get('username_en')} {request.user.get('username')[1:]}"


def user_job_num(request, initial=False):
    if initial:
        return request.user.get('username')
    return request.user.get('username')[1:]


class DBConn():
    """
    功能描述  : 数据库操作类
    """

    def __init__(self, host='localhost', port=3306, user='', pwd='', db='', charset='utf8'):
        self.conn = pymysql.connect(host=host, port=port, user=user, password=pwd, database=db, charset=charset)
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self.cursor

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.conn.commit()
        self.cursor.close()
        self.conn.close()
        log('关闭连接和游标')

    def close_conn(self):
        self.cursor.close()
        self.conn.close()

    def bulk_insert(self, sql, data):
        try:
            self.cursor.executemany(sql, data)
            self.conn.commit()
        except:
            self.conn.rollback()
            traceback.print_exc()
        # finally:
        #     self.cursor.close()


def get_all_field(col_names, tb_name, cur):
    """获取指定列所有值"""
    col_name_list = col_names.split(',') if isinstance(col_names, str) else col_names
    res = {}
    for col in col_name_list:
        sql = f"""select distinct {col} from {tb_name}"""
        cur.execute(sql)
        res[col] = [x[0] for x in cur.fetchall()]
    return res


def format_datetime(datetime_obj, type='datetime'):
    if type == 'datetime':
        res = datetime_obj.strftime('%Y-%m-%d %X')
    elif type == 'date':
        res = datetime_obj.strftime('%Y-%m-%d')
    else:
        res = None
    return res


def table_name(md):
    return md._meta.db_table


def engine(db):
    setting = settings.DATABASES[db]
    user = setting['USER']
    pwd = setting['PASSWORD']
    ip = setting['HOST']
    port = setting['PORT']
    dbname = setting['NAME']
    conn = create_engine(f'mysql+pymysql://{user}:{pwd}@{ip}:{port}/{dbname}?charset=utf8')
    return conn


def last_month(target_time):
    """获取指定时间上个月的月份号"""
    # 获取本月的第一天
    begin_day_cur_month = target_time.replace(day=1)
    # 获取上月的最后一天
    end_day_last_month = begin_day_cur_month - datetime.timedelta(days=1)
    return end_day_last_month.month


def get_differ_month(target_time, n):
    """获取指定时间的前或后n月的年月"""
    month = target_time.month
    year = target_time.year
    for i in range(abs(n)):
        if n < 0:
            if month == 1:
                year -= 1
                month = 12
            else:
                month -= 1
        else:
            if month == 12:
                year += 1
                month = 1
            else:
                month += 1
    return datetime.date(year, month, 1).strftime('%Y-%m')


def now(to_str=True, format="%Y-%m-%d %X"):
    """返回当前日期时间（对象或字符串）"""
    if to_str:
        return datetime.datetime.now().strftime(format)
    return datetime.datetime.now()


def now_date(to_str=True, format="%Y-%m-%d"):
    """返回当前日期（对象或字符串）"""
    if to_str:
        return datetime.date.today().strftime(format)
    return datetime.date.today()


def time_to_obj(dt_str, format='dt'):
    """时间字符串转为时间对象"""
    fmt = format
    if format == 'dt':
        fmt = '%Y-%m-%d %X'
    elif format == 'd':
        fmt = '%Y-%m-%d'
    return datetime.datetime.strptime(dt_str, fmt)


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False


def delete_duplicate(data_list, duplicate_key_list):
    """
    根据字典的key列表去重
    :param data_list: 原始列表
    :param duplicate_key_list: 键列表，去重依据
    :return:
    """
    data_set = set()
    res = []
    for row in data_list:
        val_tuple = tuple([row[key] for key in duplicate_key_list])
        if val_tuple not in data_set:
            data_set.add(val_tuple)
            res.append(row)
    return res


def get_host_ip():
    import socket
    """
    查询本机ip地址
    :return: ip
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


class NormalizeTool:
    def __init__(self, SERVER, PASSWORD, PORT, DATABASE, USER='root',
                 result_table="`stockmanagement_db`.`t_tallbarcode_aut_fh_result`", customer_col='CUSTOMER_NAME',
                 province_col='', city_col='', country_city_table="`materials_db`.`t_province_city_county`"):
        """
        :param SERVER: 数据库ip
        :param PASSWORD:密码
        :param PORT: 端口
        :param DATABASE: 数据表名称
        :param USER: 数据库用户
        :param result_table: 结果表的名称
        :param customer_col: 来源字段的名称
        :param province_col: 身份字段的名称
        :param city_col: 城市字段的名称
        :param country_city_table: 全国省市区配置表的名称
        """
        self.server, self.pwd, self.port, self.database, self.user = SERVER, PASSWORD, PORT, DATABASE, USER
        self.country_city_table = country_city_table
        self.result_table = result_table
        self.customer_col = customer_col
        self.province_col = province_col
        self.city_col = city_col
        # 直辖县级市
        self.province_city_map = {
            "河南": ["济源"],
            "湖北": ["仙桃市", "潜江市", "天门市", "神农架林区"],
            "新疆": ["石河子市", "阿拉尔市", "图木舒克市", "五家渠市", "北屯市", "铁门关市", "双河市", "可克达拉市", "昆玉市", "胡杨河市", "新星市"],
            "海南": ["五指山市", "文昌市", "琼海市", "万宁市", "东方市", "定安县", "屯昌县", "澄迈县", "临高县", "琼中黎族苗族自治县", "保亭黎族苗族自治县", "白沙黎族自治县",
                   "昌江黎族自治县", "乐东黎族自治县", "陵水黎族自治县"],
        }
        # 全国省市关系
        all_province_city = {'北京市': ['北京市'], '天津市': ['天津市'], '上海市': ['上海市'], '重庆市': ['重庆市'],
                             '河北省': ['石家庄市', '唐山市', '秦皇岛市', '邯郸市', '邢台市', '保定市', '张家口市', '承德市', '沧州市', '廊坊市',
                                     '衡水市'],
                             '山西省': ['太原市', '大同市', '阳泉市', '长治市', '晋城市', '朔州市', '晋中市', '运城市', '忻州市', '临汾市', '吕梁市'],
                             '内蒙古自治区':
                                 ['呼和浩特市', '包头市', '乌海市', '赤峰市', '通辽市', '鄂尔多斯市', '呼伦贝尔市', '巴彦淖尔市', '乌兰察布市', '兴安盟',
                                  '锡林郭勒盟',
                                  '阿拉善盟'],
                             '辽宁省': ['沈阳市', '大连市', '鞍山市', '抚顺市', '本溪市', '丹东市', '锦州市', '营口市', '阜新市', '辽阳市', '盘锦市',
                                     '铁岭市', '朝阳市', '葫芦岛市'],
                             '吉林省': ['长春市', '吉林市', '四平市', '辽源市', '通化市', '白山市', '松原市', '白城市',
                                     '延边朝鲜族自治州'],
                             '黑龙江省': ['哈尔滨市', '齐齐哈尔市', '鸡西市', '鹤岗市', '双鸭山市', '大庆市', '伊春市', '佳木斯市', '七台河市',
                                      '牡丹江市', '黑河市', '绥化市', '大兴安岭地区'],
                             '江苏省': ['南京市', '无锡市', '徐州市', '常州市', '苏州市', '南通市', '连云港市',
                                     '淮安市', '盐城市', '扬州市', '镇江市', '泰州市', '宿迁市'],
                             '浙江省': ['杭州市', '宁波市', '温州市', '嘉兴市', '湖州市', '绍兴市',
                                     '金华市', '衢州市', '舟山市', '台州市', '丽水市'],
                             '安徽省': ['合肥市', '芜湖市', '蚌埠市', '淮南市', '马鞍山市', '淮北市', '铜陵市',
                                     '安庆市', '黄山市', '滁州市', '阜阳市', '宿州市', '六安市', '亳州市', '池州市', '宣城市'],
                             '福建省': ['福州市', '厦门市', '莆田市',
                                     '三明市', '泉州市', '漳州市', '南平市', '龙岩市', '宁德市'],
                             '江西省': ['南昌市', '景德镇市', '萍乡市', '九江市', '新余市', '鹰潭市',
                                     '赣州市', '吉安市', '宜春市', '抚州市', '上饶市'],
                             '山东省': ['济南市', '青岛市', '淄博市', '枣庄市', '东营市', '烟台市', '潍坊市',
                                     '济宁市', '泰安市', '威海市', '日照市', '莱芜市', '临沂市', '德州市', '聊城市', '滨州市', '菏泽市'],
                             '河南省': ['郑州市', '开封市',
                                     '洛阳市', '平顶山市', '安阳市', '鹤壁市', '新乡市', '焦作市', '濮阳市', '许昌市', '漯河市', '三门峡市', '南阳市',
                                     '商丘市', '信阳市',
                                     '周口市', '驻马店市'],
                             '湖北省': ['武汉市', '黄石市', '十堰市', '宜昌市', '襄阳市', '鄂州市', '荆门市', '孝感市', '荆州市', '黄冈市',
                                     '咸宁市', '随州市', '恩施土家族苗族自治州'],
                             '湖南省': ['长沙市', '株洲市', '湘潭市', '衡阳市', '邵阳市', '岳阳市', '常德市', '张家界市',
                                     '益阳市', '郴州市', '永州市', '怀化市', '娄底市', '湘西土家族苗族自治州'],
                             '广东省': ['广州市', '韶关市', '深圳市', '珠海市', '汕头市',
                                     '佛山市', '江门市', '湛江市', '茂名市', '肇庆市', '惠州市', '梅州市', '汕尾市', '河源市', '阳江市', '清远市',
                                     '东莞市',
                                     '中山市', '潮州市',
                                     '揭阳市', '云浮市'],
                             '广西壮族自治区': ['南宁市', '柳州市', '桂林市', '梧州市', '北海市', '防城港市', '钦州市', '贵港市', '玉林市',
                                         '百色市', '贺州市', '河池市', '来宾市', '崇左市'],
                             '四川省': ['成都市', '自贡市', '攀枝花市', '泸州市', '德阳市', '绵阳市', '广元市',
                                     '遂宁市', '内江市', '乐山市', '南充市', '眉山市', '宜宾市', '广安市', '达州市', '雅安市', '巴中市', '资阳市',
                                     '阿坝藏族羌族自治州',
                                     '甘孜藏族自治州', '凉山彝族自治州'],
                             '贵州省': ['贵阳市', '六盘水市', '遵义市', '安顺市', '毕节市', '铜仁市', '黔西南布依族苗族自治州',
                                     '黔东南苗族侗族自治州', '黔南布依族苗族自治州'],
                             '云南省': ['昆明市', '曲靖市', '玉溪市', '保山市', '昭通市', '丽江市', '普洱市',
                                     '临沧市', '楚雄彝族自治州', '红河哈尼族彝族自治州', '文山壮族苗族自治州', '西双版纳傣族自治州', '大理白族自治州',
                                     '德宏傣族景颇族自治州', '怒江傈僳族自治州', '迪庆藏族自治州'],
                             '陕西省': ['西安市', '铜川市', '宝鸡市', '咸阳市', '渭南市', '延安市',
                                     '汉中市', '榆林市', '安康市', '商洛市'],
                             '甘肃省': ['兰州市', '嘉峪关市', '金昌市', '白银市', '天水市', '武威市', '张掖市', '平凉市',
                                     '酒泉市', '庆阳市', '定西市', '陇南市', '临夏回族自治州', '甘南藏族自治州'],
                             '青海省': ['西宁市', '海东市', '海北藏族自治州',
                                     '黄南藏族自治州', '海南藏族自治州',
                                     '果洛藏族自治州', '玉树藏族自治州',
                                     '海西蒙古族藏族自治州'],
                             '宁夏回族自治区': ['银川市',
                                         '石嘴山市', '吴忠市', '固原市', '中卫市'], '海南省': ['海口市', '三亚市', '三沙市', '儋州市'],
                             '西藏自治区': ['拉萨市', '日喀则市',
                                       '昌都市', '林芝市', '山南市', '那曲市', '阿里地区'],
                             '新疆维吾尔自治区': ['乌鲁木齐市', '克拉玛依市', '吐鲁番市', '哈密市',
                                          '昌吉回族自治州', '博尔塔拉蒙古自治州',
                                          '巴音郭楞蒙古自治州', '阿克苏地区',
                                          '克孜勒苏柯尔克孜自治州', '喀什地区', '和田地区',
                                          '伊犁哈萨克自治州', '塔城地区', '阿勒泰地区']}
        # 直辖市
        self.zhi_xia_city = ("北京", "上海", "天津", "重庆")
        self.invalid_city_pattern = r"白族自治州|地区|市|县|藏族自治州|彝族自治州|尼族彝族自治州|壮族苗族自治州|傣族自治州|白族自治州|傣族景颇族自治州|傈僳族自治州|朝鲜族自治州|藏族羌族自治州|回族自治州|蒙古自治州|哈萨克自治州|土家族苗族自治州|回族自治州|布依族苗族自治州|苗族侗族自治州|蒙古族藏族自治州|盟|左旗|右旗"
        self.invalid_county_pattern = r"人民政府|地区|市|县|藏族自治县|彝族自治县|尼族彝族自治县|壮族苗族自治县|傣族自治县|白族自治县|傣族景颇族自治县|傈僳族自治县|朝鲜族自治县|藏族羌族自治县|回族自治县|蒙古自治县|哈萨克自治县|土家族苗族自治县|回族自治县|布依族苗族自治县|苗族侗族自治县|蒙古族藏族自治县"
        # 并发数
        self.async_num = 20
        self.unknown_city = "未知城市"
        self.unknown_province = "未知省份"
        self.common_city_name = ("直辖县级行政区划", "省直辖级行政区划", "自治区直辖级行政区划")
        self.pd_conn = create_engine(
            'mysql+pymysql://{user}:{pwd}@{ip}:{port}/{dbname}'.format(
                user=self.user,
                pwd=self.pwd,
                ip=self.server,
                port=self.port,
                dbname=self.database
            ),
            encoding='utf8'
        )
        DATABASE = settings.DATABASES['db_MaterialsQuality']
        USER, SERVER, PASSWORD, PORT, DATABASE = DATABASE['USER'], DATABASE['HOST'], DATABASE['PASSWORD'], DATABASE[
            'PORT'], DATABASE['NAME']
        pd_conn = create_engine(
            'mysql+pymysql://{user}:{pwd}@{ip}:{port}/{dbname}'.format(
                user=USER,
                pwd=PASSWORD,
                ip=SERVER,
                port=PORT,
                dbname=DATABASE
            ),
            encoding='utf8'
        )
        self.df_country_city = pd.read_sql(
            sql=f"select concat_ws('', province, city, county) as c_p, province, city, county from {self.country_city_table}",
            con=pd_conn
        )
        self.customer_name_city_dict = {}

    def longest_common_subsequence(self, text1: str, text2: str) -> int:
        # dp[i][j] 代表考虑 text1 的前 i 个字符、考虑 text2 的前 j 的字符，形成的最长公共子序列长度
        # 初始状态: 空字符串和空字符串的公共子序列长度为0
        # 递推方程：
        #       1. dp[i][j] = dp[i-1][j-1] + 1 (text1[i] = text2[j])
        #       2. dp[i][j] = max(dp[i-1][j], dp[i][j-1]) (text1[i] != text2[j])
        l1, l2 = len(text1), len(text2)
        dp = [[0 for _ in range(l2 + 1)] for __ in range(l1 + 1)]
        for i in range(1, l1 + 1):
            for j in range(1, l2 + 1):
                if text1[i - 1] == text2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
        return dp[l1][l2]

    def convert_city(self, province, customer_name) -> (str, str):
        """
        根据“省份”和“客户名称”来匹配省份和城市（只针对中国大陆内陆地区）：
            1.若省份和客户名称都为空，直接返回“未知省份”, “未知城市”；
            2.没有匹配到城市信息的
                1. 有省份信息的返回当前省份的省会城市
                2. 没有省份信息的返回 “未知城市”
            3.根据最长匹配信息返回当前城市名称；
        :param province: 省份
        :param customer_name: 客户名称
        :return: 返回省市名称
        """
        if not province and not customer_name:
            return self.unknown_province, self.unknown_city
        elif province in self.zhi_xia_city:
            return province, province
        if province:
            df_country_city = self.df_country_city[self.df_country_city['province'] == province]
        else:
            df_country_city = self.df_country_city
        # length标识城市的最小长度
        res_city, res_province, length = self.unknown_city, self.unknown_province, 1
        # city_list, province_list = set(), set()
        for i, row in df_country_city.iterrows():
            c_p, province_, city, county = row
            city = re.sub(self.invalid_city_pattern, '', city)
            county = re.sub(self.invalid_county_pattern, '', county)
            temp_length = 0
            if (not province_ or province_ not in customer_name) and \
                    (not city or city not in customer_name) and \
                    (not county or county not in customer_name):
                continue
                # 直辖县级行政区划
            elif any([each in city for each in self.common_city_name]):
                city_range = self.province_city_map.get(province_)
                for each_city in city_range:
                    each_city = re.sub(self.invalid_city_pattern, '', each_city)
                    if province_ not in customer_name and each_city not in customer_name:
                        continue
                    temp_length = max(temp_length,
                                      self.longest_common_subsequence(customer_name, c_p.replace(city, each_city)))
                    if temp_length > length:
                        length = temp_length
                        res_city = each_city
                        res_province = province_
            else:
                temp_length = max(temp_length, self.longest_common_subsequence(customer_name, c_p))
                if temp_length > length:
                    length = temp_length
                    res_city, res_province = city, province_
                    # city_list.add(res_city)
                    # province_list.add(res_province)
        res_province = res_province if res_province != self.unknown_province else province
        if res_province in self.zhi_xia_city:
            res_city = res_province
        return res_province, res_city

    def get_china_province_customer_name_dict(self, params=dict()):
        condition = ' and '.join([f"{key}='{val}'" for key, val in params.items()])
        if self.province_col:
            if condition:
                sql = f"select distinct ifnull({self.province_col}, '') as province, ifnull({self.customer_col}, '') as customer_name from {self.result_table} where {condition}"
            else:
                sql = f"select distinct ifnull({self.province_col}, '') as province, ifnull({self.customer_col}, '') as customer_name from {self.result_table}"
        else:
            if condition:
                sql = f"select distinct '' as province, ifnull({self.customer_col}, '') as customer_name from {self.result_table} where {condition}"
            else:
                sql = f"select distinct '' as province, ifnull({self.customer_col}, '') as customer_name from {self.result_table} where {condition}"

        df = pd.read_sql(
            sql=sql,
            con=self.pd_conn
        )
        for index, row in df.iterrows():
            province, customer_name = row
            _, city = self.convert_city(province if province != '中国' else '', customer_name)
            self.customer_name_city_dict.__setitem__(customer_name, city)
        print(self.customer_name_city_dict)

    async def update_single_city(self, customer_name, city, semaphore):
        async with semaphore:
            conn = await aiomysql.connect(
                host=self.server,
                port=self.port,
                user=self.user,
                password=self.pwd,
                db=self.database
            )
            cur = await conn.cursor()
            await cur.execute(
                f'''update {self.result_table} set {self.city_col}=%s where {self.customer_col}=%s''',
                (city, customer_name,)
            )
            await conn.commit()
            await cur.close()
            conn.close()
        print(customer_name, city)

    async def update_city(self):
        semaphore = asyncio.Semaphore(self.async_num)
        task_list = []
        for customer_name, city in self.customer_name_city_dict.items():
            task_list.append(asyncio.create_task(self.update_single_city(customer_name, city, semaphore)))
        await asyncio.wait(task_list)

    def run_city(self, params):
        # 更新客户名称和城市字典
        self.get_china_province_customer_name_dict(params)
        # 将数据填充到数据库
        asyncio.run(self.update_city())
