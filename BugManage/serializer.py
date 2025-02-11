"""
================================
-*- coding: utf-8 -*-
@Author:        zcc
@Time:          2024/5/20 20:57
@E-mail:        1270475529@qq.com
@Company:
@File:          serializer
@Desc:              
================================
"""
from rest_framework import serializers

from TestInterface.models import TestInterFace
from .models import BugManage, BugHandle


class BugHandleSerializer(serializers.ModelSerializer):
    """bug处理记录序列化器"""

    class Meta:
        model = BugHandle
        fields = "__all__"


class BugManageSerializer(serializers.ModelSerializer):
    """bug管理序列化器"""
    interface_url = serializers.StringRelatedField(read_only=True, source='interface.url')
    handle = BugHandleSerializer(many=True, source='bughandle_set', read_only=True)

    class Meta:
        model = BugManage
        fields = "__all__"


class BugManageListSerializer(serializers.ModelSerializer):
    """bug管理序列化器"""
    interface_url = serializers.StringRelatedField(source='interface.url', read_only=True)

    class Meta:
        model = BugManage
        fields = ['interface_url', 'create_time', 'desc', 'status', 'user', 'id']
