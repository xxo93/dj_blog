import os
from win32com.client import Dispatch

xlApp = Dispatch('Excel.Application')
# xlApp.Visible = True

fileBase = os.path.abspath('器件替代模板.xlsx')
wb1 = xlApp.Workbooks.Open(fileBase)

"""
sh1 = wb1.Worksheets('综述')  # 获得模板表
sh2 = wb1.Worksheets('checklist')  # 获得模板表
sh3 = wb1.Worksheets('通用信号规范')  # 获得模板表
sh4 = wb1.Worksheets('版本说明')  # 获得模板表
"""
file = os.path.abspath('DRMOS器件替代模板.xlsx')

wb2 = xlApp.Workbooks.Open(file)
for i in range(4, 0, -1):
    copy_sht = wb1.Worksheets(i)

    sheet = wb2.Worksheets(1)
    copy_sht.Copy(Before=sheet)

wb2.Save()  # 保存excel
wb2.Close()  # 关闭excel

wb1.Save()  # 保存excel
wb1.Close()  # 关闭excel
