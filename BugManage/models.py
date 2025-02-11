from django.db import models

from TestInterface.models import TestInterFace


# Create your models here.
class BugManage(models.Model):
    """bug管理"""
    interface = models.ForeignKey(TestInterFace, on_delete=models.CASCADE, help_text='所属接口',
                                  verbose_name='所属接口')
    create_time = models.DateTimeField(auto_now_add=True, help_text='bug提交时间', verbose_name='bug提交时间')
    desc = models.CharField(max_length=200, help_text='bug描述', verbose_name='bug描述', blank=True)
    info = models.JSONField(help_text='测到bug的用例详情', verbose_name='测到bug的用例详情', blank=True, default=dict)
    status = models.CharField(max_length=20, help_text='bug状态', verbose_name='bug状态')
    user = models.CharField(max_length=20, help_text='提交bug的用户', verbose_name='提交bug的用户', blank=True)


    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'bug_manage'
        verbose_name = 'bug管理表'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']


class BugHandle(models.Model):
    """bug处理记录表"""
    bug = models.ForeignKey(BugManage, on_delete=models.CASCADE, help_text='所属bug',
                            verbose_name='所属bug')
    create_time = models.DateTimeField(auto_now_add=True, help_text='操作时间', verbose_name='操作时间')
    handle = models.TextField(max_length=200, help_text='操作内容', verbose_name='操作内容', blank=True)
    update_user = models.CharField(max_length=20, help_text='操作人', verbose_name='操作人', blank=True)

    class Meta:
        db_table = 'bug_handle'
        verbose_name = 'bug处理记录表'
        verbose_name_plural = verbose_name
