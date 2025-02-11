from django.shortcuts import render
from rest_framework import permissions, mixins

# Create your views here.
from .serializer import BugManageSerializer, BugHandleSerializer, BugManageListSerializer
from .models import BugManage, BugHandle
from rest_framework.viewsets import GenericViewSet


class BugManageView(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.ListModelMixin,
                    GenericViewSet):
    queryset = BugManage.objects.all()
    serializer_class = BugManageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return BugManageListSerializer
        else:
            return self.serializer_class

    def create(self, request, *args, **kwargs):
        """自定义的bug提交处理方法"""
        # 创建1条bug数据
        result = super().create(request, *args, **kwargs)
        bug = BugManage.objects.get(id=result.data.get('id'))
        handle_info = F"提交bug,bug状态是{result.data.get('status')}"
        # 新增1条Bug处理记录
        BugHandle.objects.create(bug=bug, handle=handle_info, update_user=request.user.username)
        return result

    def update(self, request, *args, **kwargs):
        """自定义的bug处理方法"""
        # 1.修改bug相关信息
        result = super().update(request, *args, **kwargs)
        bug = self.get_object()
        # 2.新增1条bug处理记录

        handle_info = F"更新bug,bug状态是{result.data.get('status')}"
        BugHandle.objects.create(bug=bug, handle=handle_info, update_user=request.user.username)
        return result
