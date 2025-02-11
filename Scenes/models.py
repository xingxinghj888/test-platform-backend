from django.db import models
from Testproject.models import TestProject
from TestInterface.models import InterfaceCase


# Create your models here.

class TestScenes(models.Model):
    """测试业务流的模型类"""
    project = models.ForeignKey(TestProject, on_delete=models.CASCADE, max_length=50, help_text="所属项目id",
                                verbose_name="所属项目id")
    name = models.CharField(max_length=50, help_text="业务流名称", verbose_name="业务流名称", null=False, blank=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'test_scenes'
        verbose_name = '测试业务流'
        verbose_name_plural = verbose_name


class SceneToCase(models.Model):
    icase = models.ForeignKey(InterfaceCase, on_delete=models.PROTECT, max_length=50,
                              help_text="所属接口用例", verbose_name="所属接口用例")
    scene = models.ForeignKey(TestScenes, on_delete=models.PROTECT, max_length=50,
                              help_text="所属业务流", verbose_name="所属业务流")
    sort = models.IntegerField(help_text="业务流中的用例执行顺序", verbose_name="业务流中的用例执行顺序", null=True,
                               blank=True)

    def __str__(self):
        return self.icase.title

    class Meta:
        db_table = 'scene_to_case'
        verbose_name = '测试业务流中的执行步骤'
        verbose_name_plural = verbose_name
