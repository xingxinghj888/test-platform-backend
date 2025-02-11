from django.db import models

from TestTask.models import TestTask
from Testproject.models import TestProject, TestEnv


class CronJob(models.Model):
    """定时任务表"""
    project = models.ForeignKey(TestProject, on_delete=models.CASCADE, max_length=50, help_text="所属项目",
                                verbose_name="所属项目")
    env = models.ForeignKey(TestEnv, on_delete=models.CASCADE, max_length=50, help_text="执行环境",
                            verbose_name="执行环境")
    task = models.ForeignKey(TestTask, on_delete=models.CASCADE, max_length=50, help_text="所属测试任务id",
                             verbose_name="所属测试任务id")
    create_time = models.DateTimeField(auto_now_add=True, help_text="创建时间", verbose_name="创建时间")
    name = models.CharField(max_length=50, help_text="定时任务名称", verbose_name="定时任务名称")
    status = models.BooleanField(help_text="定时任务状态", verbose_name="定时任务状态", default=False)
    rule = models.CharField(max_length=50, help_text="定时任务规则", verbose_name="定时任务规则")

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'CronJob'
        verbose_name = '定时任务表'
        verbose_name_plural = verbose_name
