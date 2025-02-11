from rest_framework import serializers
from .models import (
    PerformanceTestPlan, PerformanceConfig, PerformancePreset, 
    PerformanceReport, PerformanceMetrics, PerformanceError
)

class PerformanceConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceConfig
        fields = ['id', 'control_mode', 'test_mode', 'vus', 'duration', 
                 'ramp_up', 'step_users', 'step_time', 'error_threshold',
                 'host', 'endpoint', 'request_method', 'headers', 'body']

class PerformanceMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceMetrics
        fields = ['timestamp', 'response_time', 'rps', 'error_count', 
                 'error_rate', 'p50', 'p90', 'p95', 'cpu_usage', 
                 'memory_usage', 'network_io', 'shard_key', 
                 'aggregation_period', 'created_time']

class PerformanceErrorSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceError
        fields = ['timestamp', 'error_type', 'error_message', 'count', 
                 'stack_trace', 'request_data', 'response_data', 
                 'created_time']

class PerformanceTestPlanSerializer(serializers.ModelSerializer):
    configs = PerformanceConfigSerializer(many=True, read_only=True)
    metrics = PerformanceMetricsSerializer(many=True, read_only=True)
    errors = PerformanceErrorSerializer(many=True, read_only=True)
    creator = serializers.ReadOnlyField(source='creator.username')
    project_name = serializers.ReadOnlyField(source='project.name')

    class Meta:
        model = PerformanceTestPlan
        fields = ['id', 'name', 'description', 'project', 'project_name', 
                 'creator', 'created_time', 'updated_time', 'status', 
                 'configs', 'metrics', 'errors']

class PerformancePresetSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source='creator.username')
    project_name = serializers.ReadOnlyField(source='project.name')

    class Meta:
        model = PerformancePreset
        fields = ['id', 'name', 'description', 'project', 'project_name', 
                 'creator', 'created_time', 'config_type', 'config_data']

class PerformanceReportSerializer(serializers.ModelSerializer):
    plan_name = serializers.ReadOnlyField(source='plan.name')

    class Meta:
        model = PerformanceReport
        fields = ['id', 'plan', 'plan_name', 'start_time', 'end_time', 
                 'total_requests', 'total_failures', 'avg_response_time', 
                 'min_response_time', 'max_response_time', 'avg_rps', 
                 'p50_response_time', 'p90_response_time', 'p95_response_time', 
                 'error_types', 'performance_score', 'summary']