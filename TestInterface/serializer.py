"""
================================
-*- coding: utf-8 -*-
@Author:        zcc
@Time:          2024/5/10 22:22
@E-mail:        1270475529@qq.com
@Company:
@File:          serializer
@Desc:              
================================
"""
from rest_framework import serializers

from TestInterface.models import TestInterFace, InterfaceCase


class TestInterFaceSerializer(serializers.ModelSerializer):
    """接口管理的模型序列化器"""

    class Meta:
        model = TestInterFace
        fields = "__all__"


class InterfaceCaseSerializer(serializers.ModelSerializer):
    """接口用例管理的模型序列化器"""

    class Meta:
        model = InterfaceCase
        fields = "__all__"


class InterfaceCaseListSerializer(serializers.ModelSerializer):
    """返回接口用例列表的序列化器"""

    class Meta:
        model = InterfaceCase
        fields = ("id", "title")


class InterfaceCaseGetSerializer(serializers.ModelSerializer):
    """获取单条接口用例详情的序列化器"""
    interface = TestInterFaceSerializer()

    class Meta:
        model = InterfaceCase
        fields = "__all__"


class TestInterFaceListSerializer(serializers.ModelSerializer):
    """获取接口列表的模型序列化器"""

    # 外键关联的字段序列化
    cases = InterfaceCaseListSerializer(many=True, read_only=True, source="interfacecase_set")

    class Meta:
        model = TestInterFace
        fields = "__all__"
