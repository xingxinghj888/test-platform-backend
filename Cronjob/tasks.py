"""
================================
-*- coding: utf-8 -*-
@Author:        zcc
@Time:          2024/5/18 10:31
@E-mail:        1270475529@qq.com
@Company:
@File:          tasks
@Desc:              
================================
"""
from apiTestPlatform.celery import celery_app


@celery_app.task
def work1():
    print('work01')


@celery_app.task
def work2():
    print('work02')
