import codecs

import xlwt
from django.db.models import query
from django.forms import model_to_dict
from django.http import StreamingHttpResponse
from django.shortcuts import HttpResponse
from django.utils.http import urlquote
from urllib import parse
from sqlalchemy import create_engine
from django.conf import settings
import pandas as pd
import io
import time
import datetime

from PyVbord.utils.errors import ParamsException
from PyVbord.utils.errors_code import PARAMS_REQUIRED

xls_max_sheet_name_length = 31


class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value

class Excel:
    '''
    功能描述：包含导出数据到excel的函数export_excel, 从excel导入数据到数据库import_excel_to_database
    '''
    def get_response(self, file_name, out, already_format_file_name=False):
        file_name = file_name if already_format_file_name else '{}---{}.xlsx'.format(
            file_name, time.strftime('%Y%m%d', time.localtime(time.time())))
        response = HttpResponse(out.getvalue())
        response['content_type'] = 'application/vnd.ms-excel'
        response['Access-Control-Expose-Headers'] = "Content-Disposition"  # Content-Disposition为自定义头的key
        response['Content-Disposition'] = "attachment; filename=%s" % file_name
        return response

    def export_template_excel(self, columns=None, filename='', mark_columns=list()):
        '''
        功能描述：当meta_data为None时导出模板,当meta_data不为空的时候导出页面的数据;
        请求参数：excel中的数据（字典格式）
                    返回：文件对象（pd.ExcelWriter）
        :param columns为数据表的每列名称的列表;name为模板名称
        :mark_columns 需要高亮显示的列
        :return:
        '''

        # 设置HTTPResponse的类型
        data = pd.DataFrame(columns=columns)
        out = io.BytesIO()
        writer = pd.ExcelWriter(out, engine='xlsxwriter')
        data.to_excel(excel_writer=writer, index=False, sheet_name='模板', encoding="utf-8")
        # 修改单元格的样式
        if mark_columns:
            work_book = writer.book
            work_sheet = writer.sheets['模板']
            red_font = work_book.add_format({'font_color': 'red'})
            for mark_column in mark_columns:
                index = columns.index(mark_column)
                work_sheet.set_column(f"{chr(ord('A') + index)}:{chr(ord('A') + index)}", 16, cell_format=red_font)
        writer.save()
        writer.close()

        file_name = '{}-{}.xlsx'.format(filename, time.strftime('%Y%m%d', time.localtime(time.time())))
        file_name = urlquote(file_name.encode("utf-8"))
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Access-Control-Expose-Headers'] = "Content-Disposition"  # Content-Disposition为自定义头的key
        response['Content-Disposition'] = "attachment; filename=%s" % file_name
        response.write(out.getvalue())
        return response

    def export_excel2(self, meta_data, file_name=""):
        '''
        功能描述：当meta_data不为空的时候导出页面的数据;
        请求参数：excel中的数据（字典格式）
                    返回：文件对象（pd.ExcelWriter）
        :param meta_data:形如：

          {'SaleName': ['RRU5602','RRU5909'], 'SaleCode': ['02312EQP','02312FYP']...}
        :return:
        '''
        if meta_data:
            # if(len(meta_data) > 10):
            #     return {"error": "超过上限", 'msg': "excel最多导出10万行"}
            # else:
            table_data = pd.DataFrame(meta_data)
            table_data.fillna('', inplace=True)
            out = io.BytesIO()
            writer = pd.ExcelWriter(out, engine='xlsxwriter')
            table_data.to_excel(excel_writer=writer, index=False, sheet_name='数据')
            writer.save()
            writer.close()

            return self.get_response(file_name=file_name, out=out)

    def export_excel3(self, df, file_name="", index=False, merge_cell=True, already_format_file_name=False):
        """
        :param df: 文件表格数据，DataFrame
        :param file_name: 文件名 str
        :return: response
        """
        df.fillna('', inplace=True)
        out = io.BytesIO()
        writer = pd.ExcelWriter(out, engine='xlsxwriter')
        df.to_excel(excel_writer=writer, index=index, sheet_name='数据', merge_cells=merge_cell)
        writer.save()
        writer.close()
        return self.get_response(file_name, out, already_format_file_name)

    def export_excel_for_many_sheet(self, df_list, sheet_name_list, file_name=''):
        """
        导出多个sheet的excel文件
        :param df_list:
        :param sheet_name_list:
        :param file_name:
        :return:
        """
        out = io.BytesIO()
        writer = pd.ExcelWriter(out, engine='xlsxwriter')
        for i, each_df in enumerate(df_list):
            each_df.to_excel(excel_writer=writer, index=False, sheet_name=sheet_name_list[i])
        writer.save()
        writer.close()

        file_name = '{}.xlsx'.format(file_name)
        response = HttpResponse(out.getvalue())
        response['content_type'] = 'application/vnd.ms-excel'
        response['Access-Control-Expose-Headers'] = "Content-Disposition"  # Content-Disposition为自定义头的key
        response['Content-Disposition'] = "attachment; filename=%s" % file_name
        return response

    def export_excel(self, meta_data, file_name=""):
        '''
        功能描述：当meta_data不为空的时候导出页面的数据;
        请求参数：excel中的数据（字典格式）
                    返回：文件对象（pd.ExcelWriter）
        :param meta_data:形如：
        [
          {'SaleName': 'RRU5602', 'SaleCode': '02312EQP', 'PartCode': '02312RBL', 'zhishi': 'FDD', 'RXUtype': 'SVA小站', 'Hardware_platform': 'WY', 'Bands': '1800M+2100M+2100M+2600M+LAA+WiFi', 'SubBands': 'None', 'XTxR': '2T2R/1T2R', 'Power': '6*0.1W', 'Volume': '24L(不含外壳)', 'Market': '日本定制', 'TallyTime': '201204', 'Shipment': '0'},
          {'SaleName': 'RRU5909', 'SaleCode': '02312FYP', 'PartCode': '02312RJS', 'zhishi': 'FDD', 'RXUtype': 'SVA小站', 'Hardware_platform': 'WY', 'Bands': '1.8+2.1', 'SubBands': 'None', 'XTxR': '2T2R/1T2R', 'Power': '1*100mV', 'Volume': '24L(不含外壳)', 'Market': '全球', 'TallyTime': '201504', 'Shipment': '0'}
          ]
        :return:
        '''
        if meta_data:
            # if(len(meta_data) > 10):
            #     return {"error": "超过上限", 'msg': "excel最多导出10万行"}
            # else:
            table_data = {}
            columns = list(meta_data[0].keys())
            # print("原始数据：",meta_data[0])
            # print(columns)
            for column in columns:
                table_data[column] = []
                for each in meta_data:
                    table_data[column].append(each[column])
            table_data = pd.DataFrame(table_data)
            table_data.fillna('', inplace=True)
            out = io.BytesIO()
            writer = pd.ExcelWriter(out, engine='xlsxwriter')
            table_data.to_excel(excel_writer=writer, index=False, sheet_name='数据')
            writer.save()
            writer.close()
            return self.get_response(file_name=file_name, out=out)

    def export_csv(self, df, file_name="", index=False, merge_cell=True):
        import csv
        # from django.http import StreamingHttpResponse
        #
        # pseudo_buffer = Echo()
        # writer = csv.writer(pseudo_buffer)
        # response = StreamingHttpResponse(
        #     (writer.writerow(row) for row in self.parse_result(df=df)),
        #     content_type="text/csv;charset=gbk"
        # )
        # file_name = parse.quote(file_name)
        # response['Content-Disposition'] = 'attachment; filename="%s.csv"' % file_name
        # response['Access-Control-Expose-Headers'] = "Content-Disposition"
        # return response
        resp = HttpResponse(content_type='text/csv;charset=gbk')
        # attachment 代表这个csv文件作为一个附件的形式下载
        resp['content-disposition'] = "attachment; filename=%s.csv" % parse.quote(file_name)
        resp['Access-Control-Expose-Headers'] = "Content-Disposition"
        writer = csv.writer(resp)
        writer.writerow(list(df.columns))
        for i, row in df.iterrows():
            writer.writerow(list(row.values))
        # writer.writerow(['username', 'age', 'height', 'weight'])
        # writer.writerow(['zhiliao', '18', '180', '100'])
        return resp

    def parse_result(self, df):
        columns = df.columns
        yield columns
        for _, row in df.iterrows():
            yield row.values

    def import_excel_to_database(self, file, columns, tablename, chinese_english_map):
        '''
                功能描述：将excel中的内容导入到数据库;
                请求参数：excel中的数据（字典格式）
                            返回：文件对象（pd.ExcelWriter）
                :param file: 文件对象
                       columns: 需要导入数据的列名的列表
                       daname: 需要导入数据的目标数据库
                       chinese_english_map: 列名的中英文字典
                :return:
                '''
        response = {}
        file_content_df = pd.DataFrame(pd.read_excel(io=file))

        # 循环中校验数据的列,同时校验完毕后将中文列名改为英文方便数据库操作
        temp_columns = []
        for each_column in file_content_df.columns:
            if each_column not in columns.split(","):
                response["code"] = 500
                response["msg"] = "'{}'这一列不在数据库中,请按照模板导入数据".format(each_column)
                return response
            # 将file_content_df的列转化为英文, 以便存入数据库(mysql的列名不为中文,所以需要转换)
            temp_columns.append(chinese_english_map[each_column])
        file_content_df.columns = temp_columns
        file_content_df["creation_date"] = datetime.datetime.now()

        try:
            setting = settings.DATABASES['default']
            user = setting['USER']
            pwd = setting['PASSWORD']
            ip = setting['HOST']
            port = setting['PORT']
            dbname = setting['NAME']
            # 建立连接，数据库配置 {'default': {'ENGINE': 'django.db.backends.mysql', 'NAME': 'pyvboard', 'USER': 'root', 'PASSWORD': 'Wireless&BBU2019', 'HOST': '10.93.57.25', 'PORT': 3306, 'ATOMIC_REQUESTS': False, 'AUTOCOMMIT': True, 'CONN_MAX_AGE': 0, 'OPTIONS': {}, 'TIME_ZONE': None, 'TEST': {'CHARSET': None, 'COLLATION': None, 'NAME': None, 'MIRROR': None}}}
            conn = create_engine(
                'mysql+pymysql://{user}:{pwd}@{ip}:{port}/{dbname}'.format(user=user, pwd=pwd, ip=ip, port=port,
                                                                           dbname=dbname), encoding='utf8')
            # 写入数据，table_name为表名，‘replace’表示如果同名表存在就替换掉， ‘append添加’
            file_content_df.to_sql(tablename, conn, if_exists='replace', index_label='id')
            response["code"] = 200
            response["msg"] = "导入成功"
            return response
        except Exception as e:
            response["code"] = 500
            response["msg"] = "数据插入失败：{}".format(e)
            return response

    @staticmethod
    def export_by_queryset(data, file_name, headers=None, column_list=None):
        """
        功能描述：导出到excel;
        请求参数：data：数据-->eg：Queryset对象，或者如 [{},{}] 形式
                file_name:文件名，header:表头, column_list:字段列表，用于指定导出的列名
        返回：文件对象
        """
        wb = xlwt.Workbook(encoding='utf-8')

        Excel.add_sheet(wb, file_name[:xls_max_sheet_name_length], headers, data, column_list)

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        filename = parse.quote(f"{file_name}.xls".encode("utf-8"))
        response = HttpResponse(output.getvalue())
        response['content_type'] = 'application/vnd.ms-excel'
        response['Access-Control-Expose-Headers'] = "Content-Disposition"
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        return response


    @staticmethod
    def export_by_queryset_multSheet(data, file_name, headers=None, column_dict=None):
        """
        @Author: 
        @Date: 
        @Desc: 多sheet导出，返回文件对象
        :param data: 所有sheet的数据格式。 eg: {
            sheet_name1: [{col_1: value1, col_2: value2}, {col_1: value3, col_2: value4},...]   # sheet1 数据
            sheet_name2: [{col_x: value1, col_y: value2}, {col_x: value3, col_y: value4},...]   # sheet2 数据
            ...
            }
        :param headers: dict 指定每个sheet的表头。eg: {
            sheet_name1: [col_11, col_12, ...],     # [str, str, ...]
            sheet_name2: [col_21, col_22, ...],     # [str, str, ...]
            ...
            }
        :param column_dict: dict 指定每个sheet的需要导出的字段。eg: {
            sheet_name1: [field_11, field_12, ...],     # [str, str, ...]
            sheet_name2: [field_21, field_22, ...],     # [str, str, ...]
            ...
            }
        """
        wb = xlwt.Workbook(encoding='utf-8')

        for sheet_name, sheet_data in data.items():
            sheet_headers = headers.get(sheet_name, None) if headers else None
            sheet_name = sheet_name.replace('/', ',')   # sheet_name 不能存在非法字符: 如 '/','\' 等
            Excel.add_sheet(wb, sheet_name, sheet_headers, sheet_data, column_dict[sheet_name])

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        filename = parse.quote(f"{file_name}.xls".encode("utf-8"))
        response = HttpResponse(output.getvalue())
        response['content_type'] = 'application/vnd.ms-excel'
        response['Access-Control-Expose-Headers'] = "Content-Disposition"
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        return response

    @staticmethod
    def add_sheet(wb, sheet_name, headers, data, column_list=None):
        """
        @Author: 
        @Date: 
        @Desc: 新增一个sheet表
        :param wb: excel 对象 <xlwt.Workbook 对象>
        :param sheet_name: sheet name <str>
        :param headers: sheet 表头 <list>
        :param data: sheet 数据 eg: Queryset对象，或者如 [{},{}] 形式
        :param column_list: 字段列表。queryset 数据 指定某些字段进行导出; 不指定则导出所有字段。
        :return:
        """
        sheet = wb.add_sheet(sheet_name)
        row = 0

        if headers:
            for i in range(len(headers)):
                sheet.write(0, i, str(headers[i]))
            row = 1

        if isinstance(data, query.QuerySet):
            data = [model_to_dict(obj) for obj in data]
        
        if isinstance(data, pd.core.frame.DataFrame):
            data = data.to_dict(orient='records')
            
        if data:
            column_names = column_list if column_list else data[0].keys()
            for d in data:
                col = 0
                for col_name in column_names:
                    if isinstance(d.get(col_name), datetime.datetime):
                        value = d.get(col_name).strftime('%Y-%m-%d %X')
                    elif isinstance(d.get(col_name), datetime.date):
                        value = d.get(col_name).strftime('%Y-%m-%d')
                    else:
                        value = d.get(col_name)
                    sheet.write(row, col, value)
                    col += 1
                row += 1


excel = Excel()
if __name__ == "__main__":
    data = [
        {'SaleName': 'RRU5602', 'SaleCode': '02312EQP', 'PartCode': '02312RBL', 'zhishi': 'FDD', 'RXUtype': 'SVA小站',
         'Hardware_platform': 'WY', 'Bands': '1800M+2100M+2100M+2600M+LAA+WiFi', 'SubBands': 'None',
         'XTxR': '2T2R/1T2R', 'Power': '6*0.1W', 'Volume': '24L(不含外壳)', 'Market': '日本定制', 'TallyTime': '201204',
         'Shipment': '0'},
        {'SaleName': 'RRU5909', 'SaleCode': '02312FYP', 'PartCode': '02312RJS', 'zhishi': 'FDD', 'RXUtype': 'SVA小站',
         'Hardware_platform': 'WY', 'Bands': '1.8+2.1', 'SubBands': 'None', 'XTxR': '2T2R/1T2R', 'Power': '1*100mV',
         'Volume': '24L(不含外壳)', 'Market': '全球', 'TallyTime': '201504', 'Shipment': '0'}
    ]
    ex = Excel()
    ex.export_excel(data)
