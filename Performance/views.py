from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from .models import PerformanceTestPlan, PerformanceConfig, PerformancePreset, PerformanceReport
from .serializer import (
    PerformanceTestPlanSerializer, PerformanceConfigSerializer,
    PerformancePresetSerializer, PerformanceReportSerializer
)

class PerformanceTestPlanViewSet(viewsets.ModelViewSet):
    queryset = PerformanceTestPlan.objects.all()
    serializer_class = PerformanceTestPlanSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'status']
    search_fields = ['name', 'description']
    ordering_fields = ['created_time', 'updated_time']
    ordering = ['-created_time']
    
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=['post'])
    def copy(self, request, pk=None):
        """复制测试计划"""
        original_plan = self.get_object()
        new_plan_data = {
            'name': request.data.get('name', f'{original_plan.name}_copy'),
            'description': original_plan.description,
            'project': original_plan.project,
            'creator': request.user
        }
        
        new_plan = PerformanceTestPlan.objects.create(**new_plan_data)
        new_plan.scenes.set(original_plan.scenes.all())
        
        serializer = self.get_serializer(new_plan)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def batch_delete(self, request):
        """批量删除测试计划"""
        plan_ids = request.data.get('plan_ids', [])
        if not plan_ids:
            return Response({'error': '未选择要删除的计划'}, status=status.HTTP_400_BAD_REQUEST)
            
        PerformanceTestPlan.objects.filter(id__in=plan_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'])
    def batch_copy(self, request):
        """批量复制测试计划"""
        plan_ids = request.data.get('plan_ids', [])
        if not plan_ids:
            return Response({'error': '未选择要复制的计划'}, status=status.HTTP_400_BAD_REQUEST)
            
        new_plans = []
        for plan_id in plan_ids:
            try:
                original_plan = PerformanceTestPlan.objects.get(id=plan_id)
                new_plan = PerformanceTestPlan.objects.create(
                    name=f'{original_plan.name}_copy',
                    description=original_plan.description,
                    project=original_plan.project,
                    creator=request.user
                )
                new_plan.scenes.set(original_plan.scenes.all())
                new_plans.append(new_plan)
            except PerformanceTestPlan.DoesNotExist:
                continue
                
        serializer = self.get_serializer(new_plans, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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