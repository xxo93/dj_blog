# -*- coding: utf-8 -*-
""" 
@Author: zhongmin
@Date: 2021/6
@Desc: 数据库的值与显示的值映射关系
"""
from django.db import models
from rest_framework import serializers


class SexType():
    MALE = 'M'
    FEMALE = 'F'
    UNKNOWN = 'N/A'

    CHOICES = (
        (MALE, '男'),
        (FEMALE, '女'),
        (UNKNOWN, u'未知'),
    )


class User(models.Model):
    username = models.CharField(max_length=20, unique=True, verbose_name='名称')
    sex = models.CharField(max_length=3, default=SexType.UNKNOWN, choices=SexType.CHOICES, verbose_name='性别')
    create_time = models.DateTimeField(auto_now_add=True)


class UserSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(format('%Y-%m-%d %X'))
    sex_t = serializers.CharField(source='get_sex_display', read_only=True, required=False)
    # source='get_sex_display' 固定写法 get_xxx_display
    
    class Meta:
        model = User
        fields = ('id', 'name', 'sex', 'sex_t', 'create_time')
