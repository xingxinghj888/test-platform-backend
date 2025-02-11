"""
================================
-*- coding: utf-8 -*-
@Author:        zcc
@Time:          2024/5/16 22:18
@E-mail:        1270475529@qq.com
@Company:
@File:          serializer
@Desc:              
================================
"""
from rest_framework import serializers

from Cronjob.models import CronJob


class CronJobSerializer(serializers.ModelSerializer):
    task_name = serializers.StringRelatedField(read_only=True, source='task.name')
    env_name = serializers.StringRelatedField(read_only=True, source='env.name')

    class Meta:
        model = CronJob
        fields = "__all__"
