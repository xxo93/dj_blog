# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.exceptions import APIException


class ParamsException(APIException):
    """自定义异常类"""
    def __init__(self, msg):
        self.detail = msg


class RequestException(APIException):
    """请求错误"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'a bad request!!!'

    def __init__(self, msg):
        self.detail = msg

