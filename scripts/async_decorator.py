"""
有待优化...
"""
from threading import Thread


class ReThread(Thread):
    def __init__(self, target, args):
        super(ReThread, self).__init__()
        self.func = target
        self.args = args

    def run(self):
        self.result = self.func(*self.args)
        print(self.result)
        return self.result

    def get_result(self):
        try:
            return self.result
        except Exception as err:
            return err


def _async(func):
    def wrapper(*args, **kwargs):
        thr = Thread(target=func, args=args, kwargs=kwargs)
        thr.start()
    return wrapper

# test
# def _async(func):
#     def wrapper(*args, **kwargs):
#
#         # user = args[1]
#         # begin = args[2]
#         # end = args[3]
#         # warning_type = args[4]
#         # warning_label = constants.warning_type[warning_type]['label']
#         # now_time = current_time()
#         #
#         # print('.....args参数1:', args[1])
#         # print('.....args参数2:', args[2])
#         # print('.....args参数3:', args[3])
#         # print('.....args参数4:', args[4])
#         # print('.....warning_label:', warning_label)
#
#         thr = Thread(target=func, args=args, kwargs=kwargs)
#         thr.start()
#         # result = func(*args)
#
#         print('............Thread')
#         # # 发邮件
#         # EspaceMsg.send(
#         #     operator=user,  # 操作者
#         #     title='手动执行任务',  # 操作者
#         #     detail=f"[{now_time}] {result}",  # 发送信息
#         #     to=user,  # 接收者
#         # )
#         # # 任务结束，从队列中移除任务
#         # # warning_queue.l_rem(warning_type)
#         # a = warning_queue.l_rem(warning_type)
#         # print(a)
#
#     return wrapper



# def _async(user, begin, end):
#     def decorate(func):
#         def wrapper(*args, **kwargs):
#             print('.....args参数1:', user)
#             print('.....args参数2:', begin)
#             print('.....args参数3:', end)
#             thr = Thread(target=func, args=args, kwargs=kwargs)
#             thr.start()
#             result = func(*args)
#             #  发邮件
#             print('..........结果:', result)
#         return wrapper
#     return decorate

