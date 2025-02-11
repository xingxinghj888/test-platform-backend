from ApiTestEngine.core.cases import run_test
from django.shortcuts import render
from rest_framework import mixins, permissions
from rest_framework.response import Response

from Testproject.models import TestEnv
# Create your views here.
from .models import TestInterFace, InterfaceCase
from .serializer import TestInterFaceSerializer, InterfaceCaseSerializer, InterfaceCaseListSerializer, \
    InterfaceCaseGetSerializer, TestInterFaceListSerializer
from rest_framework.viewsets import GenericViewSet, ModelViewSet


class TestInterFaceView(mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        mixins.ListModelMixin,
                        GenericViewSet):
    """接口管理的视图集"""
    queryset = TestInterFace.objects.all()
    # 指定序列化器类
    serializer_class = TestInterFaceSerializer
    # 设置仅限登录的用户访问
    permission_classes = [permissions.IsAuthenticated]
    # 设置查询过滤字段
    filterset_fields = ['project']

    def get_serializer_class(self):
        if self.action == 'list':
            return TestInterFaceListSerializer
        else:
            return self.serializer_class


# 接口用例管理的视图集
class InterFaceCaseView(ModelViewSet):
    """接口用例管理的视图集"""
    queryset = InterfaceCase.objects.all()
    serializer_class = InterfaceCaseSerializer

    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['interface']

    # def list(self, request, *args, **kwargs):
    #     """获取用例列表信息"""
    #     queryset = self.filter_queryset(self.get_queryset())
    #     # 使用只返回id和title的序列化器
    #     serializer2 = InterfaceCaseListSerializer(queryset, many=True)
    #     return Response(serializer2.data)
    #
    # def retrieve(self, request, *args, **kwargs):
    #     """获取单条用例详情信息"""
    #     instance = self.get_object()
    #     serializer = InterfaceCaseGetSerializer(instance)
    #     return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == 'list':
            return InterfaceCaseListSerializer
        elif self.action == 'retrieve':
            return InterfaceCaseGetSerializer
        else:
            return InterfaceCaseSerializer

    def run_cases(self, request):
        # 获取前端传过来的接口参数
        env_id = request.data.get('env')
        cases = request.data.get('cases')
        if not all([env_id, cases]):
            return Response({'error': '参数env和case不能为空！', 'status': 400})
        # 1.获取运行的测试环境数据，组装厂测试执行引擎需要的格式
        env = TestEnv.objects.get(id=env_id)
        env_config = {
            "ENV": {
                "host": env.host,
                "headers": env.header,
                **env.global_variable,
                **env.debug_global_variable
            },
            "DB": env.db,
            "global_func": env.global_func
        }
        # 2.获取用例数据，组装成测试执行引擎需要的格式
        cases_datas = [
            {
                'name': '调试运行',
                'Cases': [cases]
            }
        ]
        # 3.调用测试执行引擎的run_test方法执行用例，得到测试结果
        result, ENV = run_test(case_data=cases_datas, env_config=env_config, debug=True)
        # 将运行的环境变量保存到测试环境的debug_global_variable中
        env.debug_global_variable = ENV
        env.save()
        return Response(result['results'][0]['cases'][0])
