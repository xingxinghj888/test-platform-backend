"""
================================
-*- coding: utf-8 -*-
@Author:        zcc
@Time:          2024/5/18 10:25
@E-mail:        1270475529@qq.com
@Company:
@File:          celery
@Desc:              
================================
"""
import os

# 创建一个celery应用，并且加载settings中的配置
from celery import Celery

from celery import Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apiTestPlatform.settings')
# 创建celery应用
celery_app = Celery('zcc')
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
# 自动加载Django应用下tasks.py文件，获取celery的注册任务
celery_app.autodiscover_tasks()