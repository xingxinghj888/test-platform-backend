from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from users.models import User
from Testproject.models import TestProject
from Scenes.models import TestScenes

class PerformanceTestPlan(models.Model):
    """性能测试计划模型
    用于存储性能测试的基本信息和执行状态
    """
    name = models.CharField(max_length=100, verbose_name='计划名称')
    description = models.TextField(blank=True, null=True, verbose_name='计划描述')
    project = models.ForeignKey(TestProject, on_delete=models.CASCADE, verbose_name='所属项目')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建人')
    scenes = models.ManyToManyField(TestScenes, verbose_name='关联业务流', blank=True)
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
    """性能测试配置模型
    用于存储性能测试的详细配置参数，包括测试模式、并发用户数、持续时间等
    """
    plan = models.ForeignKey(PerformanceTestPlan, on_delete=models.CASCADE, related_name='configs', verbose_name='所属计划')
    control_mode = models.CharField(max_length=20, choices=[
        ('single', '单独模式'),  # 单机执行
        ('central', '集中模式'),  # 分布式执行
        ('distributed', '分布式模式')  # 多节点协同执行
    ], default='single', verbose_name='控制模式')
    test_mode = models.CharField(max_length=20, choices=[
        ('concurrent', '并发模式'),  # 固定并发用户数
        ('step', '阶梯模式'),        # 逐步增加并发用户
        ('error_rate', '错误率模式'),  # 基于错误率的动态调整
        ('adaptive', '自适应模式')    # 基于系统响应的自适应调整
    ], default='concurrent', verbose_name='压测模式')
    vus = models.IntegerField(verbose_name='并发用户数', validators=[MinValueValidator(1)])
    duration = models.IntegerField(verbose_name='持续时间(秒)', validators=[MinValueValidator(1)])
    ramp_up = models.IntegerField(verbose_name='加压时间(秒)', validators=[MinValueValidator(0)])
    step_users = models.IntegerField(null=True, blank=True, verbose_name='阶梯模式每阶梯用户数', validators=[MinValueValidator(1)])
    step_time = models.IntegerField(null=True, blank=True, verbose_name='阶梯模式每阶梯持续时间', validators=[MinValueValidator(1)])
    error_threshold = models.FloatField(null=True, blank=True, verbose_name='错误率模式阈值', validators=[MinValueValidator(0.0)])
    adaptive_target = models.JSONField(null=True, blank=True, verbose_name='自适应模式目标参数')
    env = models.ForeignKey('Testproject.TestEnv', on_delete=models.CASCADE, verbose_name='测试环境')
    protocol = models.CharField(max_length=20, choices=[
        ('http', 'HTTP/HTTPS'),
        ('websocket', 'WebSocket'),
        ('grpc', 'gRPC'),
        ('tcp', 'TCP/IP'),
        ('udp', 'UDP')
    ], default='http', verbose_name='协议类型')
    data_source_type = models.CharField(max_length=20, choices=[
        ('none', '无数据源'),
        ('csv', 'CSV文件'),
        ('pool', '数据池'),
        ('generator', '数据生成器'),
        ('database', '数据库'),
        ('api', '外部API')
    ], default='none', verbose_name='数据源类型')
    data_config = models.JSONField(default=dict, blank=True, null=True, verbose_name='数据配置', help_text='包含数据源配置、变量映射、转换规则、验证规则等')
    data_cache_ttl = models.IntegerField(default=3600, verbose_name='数据缓存时间(秒)', validators=[MinValueValidator(0)])
    
    # 分布式执行配置
    node_count = models.IntegerField(default=1, verbose_name='执行节点数', validators=[MinValueValidator(1)])
    node_distribution = models.JSONField(default=dict, blank=True, null=True, verbose_name='节点分布配置')
    load_balance_strategy = models.CharField(max_length=20, choices=[
        ('round_robin', '轮询'),
        ('weight', '权重'),
        ('dynamic', '动态')
    ], default='round_robin', verbose_name='负载均衡策略')
    
    # 性能测试执行配置
    execution_config = models.JSONField(default=dict, verbose_name='执行配置', help_text='包含思考时间、重试配置、超时设置等')

    def clean(self):
        if self.test_mode == 'step' and (not self.step_users or not self.step_time):
            raise ValidationError({'step_users': '阶梯模式必须设置每阶梯用户数和持续时间'})
        if self.test_mode == 'error_rate' and not self.error_threshold:
            raise ValidationError({'error_threshold': '错误率模式必须设置阈值'})
        if self.test_mode == 'adaptive' and not self.adaptive_target:
            raise ValidationError({'adaptive_target': '自适应模式必须设置目标参数'})

    class Meta:
        verbose_name = '性能测试配置'
        verbose_name_plural = verbose_name

class PerformanceMetrics(models.Model):
    """性能指标模型
    用于存储性能测试过程中收集的各项性能指标数据
    """
    plan = models.ForeignKey(PerformanceTestPlan, on_delete=models.CASCADE, related_name='metrics', verbose_name='所属计划')
    timestamp = models.BigIntegerField(verbose_name='时间戳')
    metrics_data = models.JSONField(verbose_name='性能指标数据', help_text='包含响应时间、RPS、错误率、系统资源使用等指标')
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
    """性能测试错误记录模型
    用于存储性能测试过程中出现的错误信息
    """
    plan = models.ForeignKey(PerformanceTestPlan, on_delete=models.CASCADE, related_name='errors', verbose_name='所属计划')
    timestamp = models.BigIntegerField(verbose_name='时间戳')
    error_data = models.JSONField(verbose_name='错误详情', help_text='包含错误类型、信息、堆栈、请求响应数据等')
    count = models.IntegerField(default=1, verbose_name='出现次数')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '错误详情'
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['plan', 'timestamp'])
        ]

class PerformancePreset(models.Model):
    """性能测试预设配置模型
    用于存储可重用的性能测试配置模板
    """
    name = models.CharField(max_length=100, verbose_name='预设名称')
    description = models.TextField(blank=True, null=True, verbose_name='预设描述')
    project = models.ForeignKey(TestProject, on_delete=models.CASCADE, verbose_name='所属项目')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建人')
    created_time = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    config_type = models.CharField(max_length=20, choices=[
        ('concurrent', '并发模式'),
        ('step', '阶梯模式'),
        ('error_rate', '错误率模式'),
        ('adaptive', '自适应模式')
    ], verbose_name='配置类型')
    config_data = models.JSONField(verbose_name='配置详细数据')

    def clean(self):
        try:
            if not isinstance(self.config_data, dict):
                raise ValidationError({'config_data': '配置数据必须是有效的JSON对象'})
            # 根据不同配置类型验证必要字段
            required_fields = {
                'concurrent': ['vus', 'duration'],
                'step': ['initial_users', 'step_users', 'step_time', 'max_users'],
                'error_rate': ['initial_users', 'error_threshold'],
                'adaptive': ['initial_users', 'target_metrics']
            }
            if self.config_type in required_fields:
                for field in required_fields[self.config_type]:
                    if field not in self.config_data:
                        raise ValidationError({'config_data': f'配置类型 {self.config_type} 必须包含字段 {field}'})
        except Exception as e:
            raise ValidationError({'config_data': str(e)})

    class Meta:
        verbose_name = '性能测试预设配置'
        verbose_name_plural = verbose_name
        ordering = ['-created_time']

class PerformanceReport(models.Model):
    """性能测试报告模型
    用于存储性能测试的执行结果和统计数据
    """
    plan = models.ForeignKey(PerformanceTestPlan, on_delete=models.CASCADE, related_name='reports', verbose_name='所属计划')
    summary = models.JSONField(verbose_name='测试结果汇总', help_text='包含开始时间、结束时间、请求统计、响应时间、错误统计等完整测试结果数据')
    performance_score = models.FloatField(null=True, blank=True, verbose_name='性能评分', help_text='基于响应时间、错误率等指标的综合评分')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '性能测试报告'
        verbose_name_plural = verbose_name
        ordering = ['-created_time']