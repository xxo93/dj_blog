import os
from win32com.client import Dispatch

def getAllFilesOfWalk(dir):
    """
    @desc: 使用listdir循环遍历
    @author: ZhongMinWang 2021/6/7
    """
    if not os.path.isdir(dir):
        print(dir)
        return
    dirlist = os.walk(dir)
    for root, dirs, files in dirlist:
        print(root, dirs, files)
        for file in files:
            print(os.path.join(root, file))


def merge_sheet():
    """
    @desc: COM 接口操作Excel进行sheet复制到另一个Excel中
    @author: ZhongMinWang 2021/6/7
    """
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
        # 将copy_sht复制到sheet表之前的位置
        copy_sht.Copy(Before=sheet)

    wb2.Save()  # 保存excel
    wb2.Close()  # 关闭excel

    wb1.Save()  # 保存excel
    wb1.Close()  # 关闭excel
