"""
================================
-*- coding: utf-8 -*-
@Author:        zcc
@Time:          2024/5/18 10:33
@E-mail:        1270475529@qq.com
@Company:
@File:          tasks
@Desc:              
================================
"""
from ApiTestEngine.core.cases import run_test
from rest_framework.response import Response

from Scenes.serializer import SceneRunSerializer
from TestTask.models import TestTask, TestRecord, TestReport
from Testproject.models import TestEnv
from apiTestPlatform.celery import celery_app


@celery_app.task
def run_test_task(env_id, task_id, tester):
    """
    运行测试任务
    :param env_id:测试环境的id
    :param task_id:测试任务的id
    :param tester:接口调用者
    :return:
    """
    # 2.获取测试环境数据
    env = TestEnv.objects.get(id=env_id)
    env_config = {
        "ENV": {
            "host": env.host,
            "headers": env.header,
            **env.global_variable,
        },
        "DB": env.db,
        "global_func": env.global_func
    }
    # 3.获取测试数据（任务重的测试数据）
    # 3.1获取测试任务
    task = TestTask.objects.get(id=task_id)
    # 3.2获取任务中的所有测试业务流
    scenes_list = task.scene.all()
    # 3.3获取业务流中的测试数据,组装测试引擎需要的数据格式
    cases_in_task = []
    for scene in scenes_list:
        cases = scene.scenetocase_set.all()
        res = SceneRunSerializer(cases, many=True).data
        datas = sorted(res, key=lambda x: x['sort'])
        cases_in_task.append({
            "name": scene.name,
            "Cases": [item['icase'] for item in datas]
        })

    # 4.创建一条运行记录
    record = TestRecord.objects.create(task=task, env=env, tester=tester, status='执行中')
    # 5.运行测试
    result = run_test(cases_in_task, env_config, debug=False)
    # 6.保存测试报告，和测试运行记录
    TestReport.objects.create(info=result, record=record)
    record.all = result['all']
    record.success = result['success']
    record.fail = result['fail']
    record.error = result['error']
    record.pass_rate = f"{result['success'] / result['all']:.2f}"
    record.save()
    # 7.返回执行结果
    return result
