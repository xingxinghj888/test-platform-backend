from ApiTestEngine.core.cases import run_test
from django.shortcuts import render
from rest_framework import permissions, mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from Scenes.models import TestScenes, SceneToCase
from Scenes.serializer import TestSceneSerializer, SceneToCaseSerializer, SceneToCaselistSerializer, SceneRunSerializer
from Testproject.models import TestEnv


# Create your views here.
class TestScenesView(mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     mixins.ListModelMixin,
                     GenericViewSet):
    """测试流程的视图"""
    queryset = TestScenes.objects.all()
    serializer_class = TestSceneSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['project']

    def run_scene(self, request):
        """运行测试业务流"""
        # 1. 获取前端传过来的接口参数并进行校验
        env_id = request.data.get('env')
        scene_id = request.data.get('scene')
        if not env_id:
            return Response({'msg': '参数env不能为空'}, status=400)
        if not scene_id:
            return Response({'msg': '参数scene不能为空'}, status=400)
        # 2. 获取测试运行环境数据
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

        # 3. 获取测试业务流中的用例数据
        scene = TestScenes.objects.get(id=scene_id)
        cases = scene.scenetocase_set.all()
        # 3.1对查询集中的用例数据进行序列化
        res = SceneRunSerializer(cases, many=True).data
        # 3.2对业务流中的用例按照sort字段进行排序
        datas = sorted(res, key=lambda x: x['sort'])
        # 3.3 组装成测试执行引擎所需要的测试用例格式
        cases_data = [
            {
                "name": scene.name,
                "Cases": [item['icase'] for item in datas]
            }
        ]
        # 4. 使用测试执行引擎运行测试
        result = run_test(cases_data, env_config, debug=False)
        # 5. 返回测试执行结果
        return Response(result["results"][0], status=200)


class SceneToCaseView(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.ListModelMixin,
                      GenericViewSet):
    """测试业务流中的用例执行顺序"""
    queryset = SceneToCase.objects.all()
    serializer_class = SceneToCaseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['scene']

    def get_serializer_class(self):
        """
        实现访问不同的方法时使用不同的序列化器
        :return:
        """
        if self.action == 'list':
            return SceneToCaselistSerializer
        else:
            return self.serializer_class


class UpdateSceneCaseOrder(APIView):
    """修改测试场景中的用例执行顺序"""

    def patch(self, request):
        datas = request.data
        for item in datas:
            # 通过id获取用例执行步骤视图类的对象，然后修改执行顺序sort
            # SceneToCase.objects.filter(id=items['id']).update(sort=items['sort'])
            obj = SceneToCase.objects.get(id=item['id'])
            obj.sort = item['sort']
            obj.save()
        return Response({"msg": "成功", "data": datas})
