from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import PerformanceTestPlan, PerformanceConfig, PerformancePreset, PerformanceReport
from .serializer import (
    PerformanceTestPlanSerializer, PerformanceConfigSerializer,
    PerformancePresetSerializer, PerformanceReportSerializer
)

class PerformanceTestPlanViewSet(viewsets.ModelViewSet):
    queryset = PerformanceTestPlan.objects.all()
    serializer_class = PerformanceTestPlanSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=['post'])
    def run(self, request, pk=None):
        plan = self.get_object()
        if plan.status == 'running':
            return Response({'error': '测试计划已在运行中'}, status=status.HTTP_400_BAD_REQUEST)
        
        plan.status = 'running'
        plan.save()
        # TODO: 启动性能测试任务
        return Response({'message': '测试计划已启动'})

    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        plan = self.get_object()
        if plan.status != 'running':
            return Response({'error': '测试计划未在运行'}, status=status.HTTP_400_BAD_REQUEST)
        
        plan.status = 'completed'
        plan.save()
        # TODO: 停止性能测试任务
        return Response({'message': '测试计划已停止'})

    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        plan = self.get_object()
        return Response({'status': plan.status})

class PerformanceConfigViewSet(viewsets.ModelViewSet):
    queryset = PerformanceConfig.objects.all()
    serializer_class = PerformanceConfigSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        plan_id = self.request.query_params.get('plan_id', None)
        if plan_id is not None:
            queryset = queryset.filter(plan_id=plan_id)
        return queryset

class PerformancePresetViewSet(viewsets.ModelViewSet):
    queryset = PerformancePreset.objects.all()
    serializer_class = PerformancePresetSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

class PerformanceReportViewSet(viewsets.ModelViewSet):
    queryset = PerformanceReport.objects.all()
    serializer_class = PerformanceReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        plan_id = self.request.query_params.get('plan_id', None)
        if plan_id is not None:
            queryset = queryset.filter(plan_id=plan_id)
        return queryset

    @action(detail=True, methods=['get'])
    def metrics(self, request, pk=None):
        report = self.get_object()
        return Response(report.metrics)

    @action(detail=True, methods=['get'])
    def errors(self, request, pk=None):
        report = self.get_object()
        return Response(report.errors)

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        report = self.get_object()
        return Response(report.summary)