import json
import os

from django.shortcuts import render
from rest_framework.response import Response

# Create your views here.
# 测试项目管理 增删查改接口的实现
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from Testproject.models import TestProject, TestEnv, TestFile
from Testproject.serializer import TestProjectSerializer, TestEnvSerializer, TestFileSerializer
from rest_framework import permissions, mixins

from apiTestPlatform import settings


class TestProjectView(ModelViewSet):
    """这是项目视图集"""
    queryset = TestProject.objects.all()
    serializer_class = TestProjectSerializer
    # 添加视图的权限校验(需要登录才能访问，访问的时候需在请求头中添加token)
    permission_classes = [permissions.IsAuthenticated]


# 测试环境管理的接口开发(增删查改)

class TestEnvView(ModelViewSet):
    """这是测试环境视图集"""
    queryset = TestEnv.objects.all()
    serializer_class = TestEnvSerializer
    # 添加视图的权限校验(需要登录才能访问，访问的时候需在请求头中添加token)
    permission_classes = [permissions.IsAuthenticated]
    # 在视图集中添加过滤器条件
    filterset_fields = ['project']


# 测试文件管理的接口开发（上传文件、删除文件、获取文件列表）
class TestFileView(mixins.CreateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
    """这是测试文件管理视图集"""
    queryset = TestFile.objects.all()
    serializer_class = TestFileSerializer
    # 添加视图的权限校验(需要登录才能访问，访问的时候需在请求头中添加token)
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """文件上传的方法"""
        # 要求：1.文件大小不能超过300kb；2.文件不能重复上传
        # 步骤1：获取上传的文件大小
        file_size = request.data["file"].size
        file_name = request.data["file"].name
        if file_size > 3000 * 1024:
            return Response({"error": "文件大小不能超过300kb"}, status=400)
        # if TestFile.objects.filter(file=file_name).exists():
        #     return Response({"error": "文件不能重复上传"}, status=400)
        if os.path.isfile(settings.MEDIA_ROOT / file_name):
            return Response({"error": "文件不能重复上传"}, status=400)
        # 修改info字段的值
        file_type = request.data["file"].content_type
        request.data["info"] = json.dumps([file_name, F'files/{file_name}', file_type])
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """删除文件的方法"""
        file_path = self.get_object().info[1]
        # 调用父类的方法进行数据库文件的删除
        result = super().destroy(request, *args, **kwargs)

        # 删除本地的文件
        os.remove(file_path)
        return result
