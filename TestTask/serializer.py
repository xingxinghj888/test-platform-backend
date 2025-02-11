"""
================================
-*- coding: utf-8 -*-
@Author:        zcc
@Time:          2024/5/13 21:29
@E-mail:        1270475529@qq.com
@Company:
@File:          serializer
@Desc:              
================================
"""
from .models import TestTask, TestRecord, TestReport
from rest_framework import serializers
from Scenes.serializer import TestSceneSerializer


class TestTaskSerializer(serializers.ModelSerializer):
    """测试任务的序列化器"""

    class Meta:
        model = TestTask
        fields = "__all__"


class TestTaskGetSerializer(serializers.ModelSerializer):
    """测试任务的序列化器"""
    scene = TestSceneSerializer(many=True)

    class Meta:
        model = TestTask
        fields = "__all__"


class TestRecordSerializer(serializers.ModelSerializer):
    """测试运行记录"""
    # StringRelatedField的作用默认是返回这个关联模型的__str__方法的值，通过source可以指定返回关联模型的其他字段，
    # 你那个scrource = env，错误提示参数加上去是多余的。
    # 正确的写法是scrource = env.name ,意思是返回env的这个关联字段的name属性，就是环境名称。
    env = serializers.StringRelatedField(read_only=True, source='env.name')
    task = serializers.StringRelatedField(read_only=True, source="task.name")

    class Meta:
        model = TestRecord
        fields = "__all__"


class TestReportSerializer(serializers.ModelSerializer):
    """测试报告"""

    class Meta:
        model = TestReport
        fields = "__all__"
