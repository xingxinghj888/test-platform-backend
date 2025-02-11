from ApiTestEngine.core.cases import run_test
from django.shortcuts import render
from rest_framework.response import Response

from rest_framework.viewsets import ModelViewSet, GenericViewSet

from Scenes.serializer import SceneRunSerializer
from Testproject.models import TestEnv
from .models import TestTask, TestRecord, TestReport
from .serializer import TestTaskSerializer, TestTaskGetSerializer, TestRecordSerializer, TestReportSerializer
from rest_framework import permissions, mixins

from .tasks import run_test_task


class TestTaskView(ModelViewSet):
    """定义测试任务管理的视图类"""
    queryset = TestTask.objects.all()
    serializer_class = TestTaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    # 定义测试任务列表的查询参数
    filterset_fields = ['project']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TestTaskGetSerializer
        else:
            return self.serializer_class

    def run_task(self, request):
        """运行测试任务的方法"""
        # 1. 获取前端传过来的参数并进行校验
        env_id = request.data.get('env')
        task_id = request.data.get('task')
        if not env_id:
            return Response({'msg': '参数env不能为空'}, status=400)
        if not task_id:
            return Response({'msg': '参数task不能为空'}, status=400)
    # 使用celery异步执行测试任务中的用例
        run_test_task.delay(env_id, task_id, request.user.username)
        return Response({'msg': '测试任务已经开始执行'}, status=200)


#  定义测试记录查询参数实现使用的过滤器
from rest_framework import generics
from django_filters import rest_framework as filters


class TestRecordFilter(filters.FilterSet):
    """测试记录过滤的模型"""
    project = filters.NumberFilter(field_name="task__project")

    class Meta:
        model = TestRecord
        fields = ['task', 'project']


class TestRecordView(mixins.ListModelMixin,
                     GenericViewSet):
    # 返回的数据设置成按创建时间降序排列
    queryset = TestRecord.objects.all().order_by("-create_time")
    serializer_class = TestRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    # 由于TestRecord中没有project字段，所以需要自定义一个过滤器类
    # filterset_fields = ['project', 'task']
    filterset_class = TestRecordFilter


class TestReportView(mixins.RetrieveModelMixin,
                     GenericViewSet):
    queryset = TestReport.objects.all()
    serializer_class = TestReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    # 因为实际前端查询时我们不是通过测试报告id去查，而是通过点击运行记录去查看该运行记录的测试报告
    def retrieve(self, request, *args, **kwargs):
        # 1.t通过id找测试运行记录
        record = TestRecord.objects.get(id=kwargs['pk'])
        # 通过测试运行记录找测试报告
        report = TestReport.objects.get(record=record)
        serializer = self.get_serializer(report)
        return Response(serializer.data)
