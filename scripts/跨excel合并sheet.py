import os
from win32com.client import Dispatch


def getAllFilesOfWalk(dir):
    """
    @desc: 使用listdir循环遍历
    @author: ZhongMinWang 2021/6/7
    :return: file_list
    """
    if not os.path.isdir(dir):
        print(dir)
        return
    dirlist = os.walk(dir)
    file_list = []
    for root, dirs, files in dirlist:
        # print(root, dirs, files)
        for file in files:
            # print(os.path.join(root, file))
            file_list.append(os.path.join(root, file))
    return file_list


class ExcelCOM():
    def __init__(self):
        self.xlApp = Dispatch('Excel.Application')
        # xlApp.Visible = True

    def merge_sheet(self, file1, file2):
        """
        @desc: COM 接口操作Excel进行sheet复制到另一个Excel中
        @author: ZhongMinWang 2021/6/7
        """
        excelBase = os.path.abspath(file1)
        wb1 = self.xlApp.Workbooks.Open(excelBase)

        """
        sh1 = wb1.Worksheets('综述')  # 获得模板表
        sh2 = wb1.Worksheets('checklist')  # 获得模板表
        sh3 = wb1.Worksheets('通用信号规范')  # 获得模板表
        sh4 = wb1.Worksheets('版本说明')  # 获得模板表
        """
        excel = os.path.abspath(file2)

        wb2 = self.xlApp.Workbooks.Open(excel)
        for i in range(4, 0, -1):
            copy_sht = wb1.Worksheets(i)
            try:
                # 获取目标sheet
                sheet = wb2.Worksheets(1)
            except:
                self.xlApp.Worksheets.Add().Name = 'sheet1'
            else:
                # 将copy_sht复制到目标sheet表之前的位置
                copy_sht.Copy(Before=sheet)

        wb2.Save()  # 保存excel
        wb2.Close()  # 关闭excel

        wb1.Save()  # 保存excel
        wb1.Close()  # 关闭excel


if __name__ == '__main__':
    basepath = 'D:\项目资料\系统开发\替代测试系统开发\无线器件替代可视化协同平台（第三版）\硬件器件替代测试计划和报告模板'
    file_list1 = getAllFilesOfWalk(basepath + '\电源类自动生成模板')
    # file_list2 = getAllFilesOfWalk(basepath + '\电源类自动生成模板')
    # file_list3 = getAllFilesOfWalk(basepath + '\电源类自动生成模板')
    file_list = [
        *file_list1,
        # *file_list2,
        # *file_list3,
    ]
    print(len(file_list))

    basefile = basepath + '\器件替代模板.xlsx'

    obj = ExcelCOM()
    for i, file in enumerate(file_list, 1):
        # print(file)
        obj.merge_sheet(basefile, file)
        print(f'已合并{i}个项目')

    print('-- over! --')
