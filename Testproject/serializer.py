"""
================================
-*- coding: utf-8 -*-
@Author:        zcc
@Time:          2024/5/7 11:56
@E-mail:        1270475529@qq.com
@Company:
@File:          serializer
@Desc:              
================================
"""
from .models import TestProject, TestEnv, TestFile
from rest_framework import serializers


class TestProjectSerializer(serializers.ModelSerializer):
    """项目的序列化器"""

    class Meta:
        model = TestProject
        fields = '__all__'


class TestEnvSerializer(serializers.ModelSerializer):
    """测试环境的序列化器"""

    class Meta:
        model = TestEnv
        fields = '__all__'


class TestFileSerializer(serializers.ModelSerializer):
    """测试文件的序列化器"""

    class Meta:
        model = TestFile
        fields = '__all__'
