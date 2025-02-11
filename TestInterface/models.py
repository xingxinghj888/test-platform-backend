from django.db import models

from Testproject.models import TestProject


# Create your models here.
class TestInterFace(models.Model):
    """接口管理模型"""
    CHOICES = {
        ("1", "项目接口"),
        ("2", "第三方接口")
    }
    project = models.ForeignKey(TestProject, on_delete=models.CASCADE, max_length=50, help_text="所属项目id",
                                verbose_name="所属项目id", null=False, blank=False)
    name = models.CharField(max_length=50, help_text="接口名称", verbose_name="接口名称", null=False, blank=False)
    url = models.CharField(max_length=200, help_text="接口地址", verbose_name="接口地址", null=False, blank=False)
    method = models.CharField(max_length=10, help_text="请求方法", verbose_name="请求方法", null=False, blank=False)
    type = models.CharField(max_length=10, help_text="接口类型", verbose_name="接口类型", choices=CHOICES, default='1',
                            null=False, blank=False)

    def __str__(self):
        return self.url

    class Meta:
        db_table = 'interface'
        verbose_name = '接口管理表'
        verbose_name_plural = verbose_name


# 接口用例管理模型
class InterfaceCase(models.Model):
    """接口用例管理模型"""
    title = models.CharField(max_length=50, help_text="接口用例名称", verbose_name="接口用例名称", null=False,
                             blank=False)
    interface = models.ForeignKey(TestInterFace, on_delete=models.CASCADE, max_length=50, help_text="所属接口",
                                  verbose_name="所属接口", null=False, blank=False)
    headers = models.JSONField(help_text="请求头配置", verbose_name="请求头配置", null=True, blank=True, default=dict)
    request = models.JSONField(help_text="请求参数", verbose_name="请求参数", null=True, blank=True, default=dict)
    file = models.JSONField(help_text="请求上传的文件参数", verbose_name="请求上传的文件参数", null=True, blank=True,
                            default=list)
    setup_script = models.TextField(help_text="前置脚本", verbose_name="前置脚本", null=True, blank=True, default="")
    teardown_script = models.TextField(help_text="后置脚本", verbose_name="后置脚本", null=True, blank=True, default="")

    def __str__(self):
        return self.title
    class Meta:
        db_table = 'interface_case'
        verbose_name = '接口用例管理表'
        verbose_name_plural = verbose_name
