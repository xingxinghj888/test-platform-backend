"""
================================
-*- coding: utf-8 -*-
@Author:        zcc
@Time:          2024/5/19 16:55
@E-mail:        1270475529@qq.com
@Company:
@File:          views
@Desc:
================================
"""
import json

from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import permissions, mixins
from Cronjob.models import CronJob
from Cronjob.serializer import CronJobSerializer

from django_celery_beat.models import CrontabSchedule, PeriodicTask
from django.db import transaction

# Create your views here.

import json

from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import permissions, mixins
from Cronjob.models import CronJob
from Cronjob.serializer import CronJobSerializer

from django_celery_beat.models import CrontabSchedule, PeriodicTask
from django.db import transaction


# Create your views here.


class CronJobView(mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin,
                  GenericViewSet):
    """定时任务增删查改的序列化器"""
    queryset = CronJob.objects.all()
    serializer_class = CronJobSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['project', 'task']

    def create(self, request, *args, **kwargs):
        """创建定时任务的方法"""
        # 开启事务
        with transaction.atomic():
            # 创建一个事务保存节点
            save_point = transaction.savepoint()
            try:
                # 调用父类的方法创建一条定时任务（只是在CronJob表中新赠一条数据）
                result = super().create(request, *args, **kwargs)
                # 获取创建定时任务的规则
                rule = result.data.get('rule').split(" ")
                rule_dict = dict(zip(['minute', 'hour', 'day_of_week', 'day_of_month', 'month_of_year'], rule))
                # 使用django-celer-beat中的CrontabSchedule模型创建一个规则对象
                try:
                    cron = CrontabSchedule.objects.get(**rule_dict)
                except:
                    cron = CrontabSchedule.objects.create(**rule_dict)
                # 使用django-celer-beat中的PeriodicTask创建一个周期性调度任务
                PeriodicTask.objects.create(
                    name=result.data.get('id'),
                    task='TestTask.tasks.run_test_task',
                    crontab=cron,
                    kwargs=json.dumps({
                        "env_id": result.data.get('env'),
                        "task_id": result.data.get('task'),
                        "tester": request.user.username
                    }),
                    enabled=result.data.get('status'),
                )
            except:
                # 进行事物回滚
                transaction.savepoint_rollback(save_point)
                return Response({'error': "定时任务创建失败！"}, status=500)
            else:
                # 提交事物
                transaction.savepoint_commit(save_point)
                return Response(result.data)

    def update(self, request, *args, **kwargs):
        with transaction.atomic():
            save_point = transaction.savepoint()
            try:
                # 调用父类的方法更新数据
                res = super().update(request, *args, **kwargs)
                cronjob = self.get_object()
                # 更新周期任务和定期任务的时间规则
                ptask = PeriodicTask.objects.get(name=cronjob.id)
                # 更新执行的任务和测试环境
                ptask.kwargs = json.dumps({
                    "env_id": res.data.get('env'),
                    "task_id": res.data.get('task'),
                })
                # 更新定时任务的状态
                ptask.enabled = res.data.get('status')
                # 获取定期执行的规则
                rule = res.data.get('rule').split(" ")
                rule_dict = dict(zip(['minute', 'hour', 'day_of_week', 'day_of_month', 'month_of_year'], rule))
                # 使用django-celer-beat中的CrontabSchedule模型创建一个规则对象
                try:
                    cron = CrontabSchedule.objects.get(**rule_dict)
                except:
                    cron = CrontabSchedule.objects.create(**rule_dict)
                # 更新周期规则
                ptask.crontab = cron
                ptask.save()
            except:
                transaction.savepoint_rollback(save_point)
                return Response({"error": "修改失败！"})
            else:
                transaction.savepoint_commit(save_point)
                return res

    def destroy(self, request, *args, **kwargs):
        with transaction.atomic():
            save_point = transaction.savepoint()
            try:
                cronjob = self.get_object()
                ptask = PeriodicTask.objects.get(name=cronjob.id)
                ptask.enabled = False
                ptask.delete()
                res = super().destroy(request, *args, **kwargs)
            except:
                transaction.savepoint_rollback(save_point)
                return Response({"error": "删除失败！"})
            else:
                transaction.savepoint_commit(save_point)
                return res
