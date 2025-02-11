from django.db import models
from django.utils import timezone
from users.models import User
from Testproject.models import TestProject

class PerformanceTestPlan(models.Model):
    name = models.CharField(max_length=100, verbose_name='计划名称')
    description = models.TextField(blank=True, null=True, verbose_name='计划描述')
    project = models.ForeignKey(TestProject, on_delete=models.CASCADE, verbose_name='所属项目')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建人')
    created_time = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    status = models.CharField(max_length=20, choices=[
        ('pending', '待执行'),
        ('running', '执行中'),
        ('completed', '已完成'),
        ('failed', '执行失败')
    ], default='pending', verbose_name='执行状态')

    class Meta:
        verbose_name = '性能测试计划'
        verbose_name_plural = verbose_name
        ordering = ['-created_time']

class PerformanceConfig(models.Model):
    plan = models.ForeignKey(PerformanceTestPlan, on_delete=models.CASCADE, related_name='configs', verbose_name='所属计划')
    control_mode = models.CharField(max_length=20, choices=[
        ('single', '单独模式'),
        ('central', '集中模式')
    ], default='single', verbose_name='控制模式')
    test_mode = models.CharField(max_length=20, choices=[
        ('concurrent', '并发模式'),
        ('step', '阶梯模式'),
        ('error_rate', '错误率模式')
    ], default='concurrent', verbose_name='压测模式')
    vus = models.IntegerField(verbose_name='并发用户数')
    duration = models.IntegerField(verbose_name='持续时间(秒)')
    ramp_up = models.IntegerField(verbose_name='加压时间(秒)')
    step_users = models.IntegerField(null=True, blank=True, verbose_name='阶梯模式每阶梯用户数')
    step_time = models.IntegerField(null=True, blank=True, verbose_name='阶梯模式每阶梯持续时间')
    error_threshold = models.FloatField(null=True, blank=True, verbose_name='错误率模式阈值')
    host = models.CharField(max_length=200, verbose_name='目标主机')
    endpoint = models.CharField(max_length=200, verbose_name='测试接口')
    request_method = models.CharField(max_length=10, verbose_name='请求方法')
    headers = models.JSONField(default=dict, verbose_name='请求头')
    body = models.JSONField(default=dict, blank=True, null=True, verbose_name='请求体')

    class Meta:
        verbose_name = '性能测试配置'
        verbose_name_plural = verbose_name

class PerformanceMetrics(models.Model):
    plan = models.ForeignKey(PerformanceTestPlan, on_delete=models.CASCADE, related_name='metrics', verbose_name='所属计划')
    timestamp = models.BigIntegerField(verbose_name='时间戳')
    response_time = models.FloatField(null=True, blank=True, verbose_name='响应时间')
    rps = models.FloatField(null=True, blank=True, verbose_name='每秒请求数')
    error_count = models.IntegerField(default=0, verbose_name='错误数')
    error_rate = models.FloatField(default=0, verbose_name='错误率')
    p50 = models.FloatField(null=True, blank=True, verbose_name='P50响应时间')
    p90 = models.FloatField(null=True, blank=True, verbose_name='P90响应时间')
    p95 = models.FloatField(null=True, blank=True, verbose_name='P95响应时间')
    cpu_usage = models.FloatField(null=True, blank=True, verbose_name='CPU使用率')
    memory_usage = models.FloatField(null=True, blank=True, verbose_name='内存使用率')
    network_io = models.FloatField(null=True, blank=True, verbose_name='网络IO')
    shard_key = models.CharField(max_length=50, verbose_name='数据分片键')
    aggregation_period = models.CharField(max_length=20, null=True, blank=True, verbose_name='聚合周期')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '性能指标'
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['plan', 'timestamp']),
            models.Index(fields=['shard_key'])
        ]

class PerformanceError(models.Model):
    plan = models.ForeignKey(PerformanceTestPlan, on_delete=models.CASCADE, related_name='errors', verbose_name='所属计划')
    timestamp = models.BigIntegerField(verbose_name='时间戳')
    error_type = models.CharField(max_length=100, verbose_name='错误类型')
    error_message = models.TextField(null=True, blank=True, verbose_name='错误信息')
    count = models.IntegerField(default=1, verbose_name='出现次数')
    stack_trace = models.TextField(null=True, blank=True, verbose_name='错误堆栈')
    request_data = models.JSONField(null=True, blank=True, verbose_name='请求数据')
    response_data = models.JSONField(null=True, blank=True, verbose_name='响应数据')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '错误详情'
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['plan', 'timestamp']),
            models.Index(fields=['error_type'])
        ]

class PerformancePreset(models.Model):
    name = models.CharField(max_length=100, verbose_name='预设名称')
    description = models.TextField(blank=True, null=True, verbose_name='预设描述')
    project = models.ForeignKey(TestProject, on_delete=models.CASCADE, verbose_name='所属项目')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建人')
    created_time = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    config_type = models.CharField(max_length=20, choices=[
        ('concurrent', '并发模式'),
        ('step', '阶梯模式'),
        ('error_rate', '错误率模式')
    ], verbose_name='配置类型')
    config_data = models.JSONField(verbose_name='配置详细数据')

    class Meta:
        verbose_name = '性能测试预设配置'
        verbose_name_plural = verbose_name
        ordering = ['-created_time']

class PerformanceReport(models.Model):
    plan = models.ForeignKey(PerformanceTestPlan, on_delete=models.CASCADE, related_name='reports', verbose_name='所属计划')
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')
    total_requests = models.IntegerField(default=0, verbose_name='总请求数')
    total_failures = models.IntegerField(default=0, verbose_name='失败请求数')
    avg_response_time = models.FloatField(null=True, blank=True, verbose_name='平均响应时间')
    min_response_time = models.FloatField(null=True, blank=True, verbose_name='最小响应时间')
    max_response_time = models.FloatField(null=True, blank=True, verbose_name='最大响应时间')
    avg_rps = models.FloatField(null=True, blank=True, verbose_name='平均RPS')
    p50_response_time = models.FloatField(null=True, blank=True, verbose_name='P50响应时间')
    p90_response_time = models.FloatField(null=True, blank=True, verbose_name='P90响应时间')
    p95_response_time = models.FloatField(null=True, blank=True, verbose_name='P95响应时间')
    error_types = models.JSONField(default=dict, verbose_name='错误类型统计')
    performance_score = models.FloatField(null=True, blank=True, verbose_name='性能评分')
    summary = models.JSONField(verbose_name='测试结果汇总')

    class Meta:
        verbose_name = '性能测试报告'
        verbose_name_plural = verbose_name
        ordering = ['-start_time']