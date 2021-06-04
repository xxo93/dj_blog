# -*- coding: utf-8 -*-

"""定制错误码"""

LOGIN_REQUIRED = 1001  # 未登录

SEND_EMAIL_FAILURE = 1002  # 邮件发送失败

LOGIN_FAILURE = 1003  # 登录失败

PARAMS_REQUIRED = 1004  # 参数必传

PARAMS_WRONG = 1005  # 参数有误

LDAP_LOGIN_ERROR = 1006  # ldap服务器连接失败

ACCOUNT_ERROR = 1007  # 账号错误或不存在

RECORD_ALREADY_EXISTS = 2001  # 插入数据时，数据库中已存在该记录

VALIDATE_FAILURE = 2002  # 导入数据时，字段校验错误

RECORD_NOT_EXISTS = 2003  # 记录不存在

OUT_OF_LIMIT = 2004 # 超出最大范围限制

UNIQUE_EXISTS = 1008  # 重复或已存在

TASK_ALREADY_EXISTS = 3001  # 队列中已存在此任务

TASK_ALREADY_CREATED = 3002 # 队列中创建了一个任务
