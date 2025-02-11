from django.db import models
from Testproject.models import TestProject, TestEnv
from Scenes.models import TestScenes


# Create your models here.


class TestTask(models.Model):
    """测试任务的模型类"""
    project = models.ForeignKey(TestProject, on_delete=models.PROTECT, max_length=50, help_text="所属项目id",
                                verbose_name="所属项目id")
    name = models.CharField(max_length=50, help_text="任务名称", verbose_name="任务名称")
    scene = models.ManyToManyField(TestScenes, help_text="包含的测试业务流", verbose_name="包含的测试业务流业务流")

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'test_task'
        verbose_name = '测试任务表'
        verbose_name_plural = verbose_name


class TestRecord(models.Model):
    """测试记录的模型类"""
    task = models.ForeignKey(TestTask, on_delete=models.PROTECT, max_length=50, help_text="所属测试任务id",
                             verbose_name="所属测试任务id")
    env = models.ForeignKey(TestEnv, on_delete=models.PROTECT, max_length=50, help_text="执行环境",
                            verbose_name="执行环境")
    all = models.IntegerField(help_text="总用例数", verbose_name="总用例数", default=0, blank=True)
    success = models.IntegerField(help_text="通过用例数", verbose_name="通过用例数", default=0, blank=True)
    fail = models.IntegerField(help_text="失败用例数", verbose_name="失败用例数", default=0, blank=True)
    error = models.IntegerField(help_text="错误用例数", verbose_name="错误用例数", default=0, blank=True)
    pass_rate = models.CharField(help_text="通过率", verbose_name="通过率", default="0", blank=True, max_length=20)
    tester = models.CharField(max_length=20, help_text="执行人", verbose_name="执行人", blank=True)
    status = models.CharField(max_length=20, help_text="执行状态", verbose_name="执行状态", default="未执行")
    create_time = models.DateTimeField(auto_created=True, help_text="执行时间", verbose_name="执行时间",
                                       auto_now_add=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'test_record'
        verbose_name = '测试运行记录表'
        verbose_name_plural = verbose_name


class TestReport(models.Model):
    """测试报告模型"""
    info = models.JSONField(help_text="报告信息", verbose_name="报告信息", default=dict, null=True, blank=True)
    record = models.OneToOneField(TestRecord, on_delete=models.CASCADE, max_length=50, help_text="运行记录id",
                                  verbose_name="运行记录id")

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'test_report'
        verbose_name = '测试报告表'
        verbose_name_plural = verbose_name
