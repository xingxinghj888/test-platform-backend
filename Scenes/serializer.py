"""
================================
-*- coding: utf-8 -*-
@Author:        zcc
@Time:          2024/5/12 19:59
@E-mail:        1270475529@qq.com
@Company:
@File:          serializer
@Desc:              
================================
"""

from rest_framework import serializers

from Scenes.models import TestScenes, SceneToCase
from TestInterface.serializer import InterfaceCaseListSerializer, InterfaceCaseGetSerializer


class TestSceneSerializer(serializers.ModelSerializer):
    """测试业务流的序列化器"""

    class Meta:
        model = TestScenes
        fields = "__all__"


class SceneToCaseSerializer(serializers.ModelSerializer):
    """测试业务流中的执行步骤序列化器"""

    class Meta:
        model = SceneToCase
        fields = "__all__"


class SceneToCaselistSerializer(serializers.ModelSerializer):
    """测试业务流中所有的用例执行步骤序列化器"""
    icase = InterfaceCaseListSerializer()

    class Meta:
        model = SceneToCase
        fields = "__all__"


class SceneRunSerializer(serializers.ModelSerializer):
    """业务流执行序列化器：测试用例数据中的所有字段序列化出来"""
    icase = InterfaceCaseGetSerializer()

    class Meta:
        model = SceneToCase
        fields = "__all__"
