"""性能测试任务执行模块

提供性能测试任务的异步执行功能，包括：
- 测试任务启动
- 测试数据收集
- 测试报告生成
"""

from celery import shared_task
from django.utils import timezone
from Performance.models import PerformanceTestPlan, PerformanceReport
import time
from .core import PerformanceTestEngine

@shared_task
def run_performance_test(env_id, plan_id, config_id=None):
    """执行性能测试任务
    
    Args:
        env_id: 测试环境ID
        plan_id: 性能测试计划ID
        config_id: 性能测试配置ID，如果不指定则使用计划默认配置
        
    Returns:
        bool: 测试执行结果，成功返回True，失败返回False
    """
    try:
        plan = PerformanceTestPlan.objects.get(id=plan_id)
        
        # 创建测试报告
        report = PerformanceReport.objects.create(
            plan=plan,
            start_time=timezone.now(),
            metrics={},  # 性能指标数据
            errors=[],   # 错误信息列表
            summary={}   # 测试结果总结
        )
        
        # 获取测试配置
        if config_id:
            config = plan.configs.filter(id=config_id).first()
            if not config:
                raise ValueError('未找到指定的性能测试配置')
        else:
            config = plan.configs.first()
            if not config:
                raise ValueError('未找到性能测试配置')
        
        # 初始化测试引擎
        engine = PerformanceTestEngine()
        
        # 获取业务流关联的测试用例
        test_flows = []
        for scene in plan.scenes.all():
            # 获取业务流中的用例步骤，按执行顺序排序
            scene_cases = scene.scenetocase_set.order_by('sort')
            
            flow_steps = []
            for step in scene_cases:
                case = step.icase
                # 统一处理接口测试和性能测试的数据格式
                request_data = {}
                if hasattr(case, 'request') and case.request:
                    request_data = case.request
                elif hasattr(case, 'body') and case.body:
                    request_data = {'json': case.body}
                
                headers = {}
                if hasattr(case, 'headers') and case.headers:
                    headers = case.headers
                elif hasattr(case, 'interface') and case.interface.get('headers'):
                    headers = case.interface.get('headers')
                
                interface = {}
                if hasattr(case, 'interface'):
                    interface = case.interface
                else:
                    interface = {
                        'url': case.endpoint if hasattr(case, 'endpoint') else '',
                        'method': case.request_method if hasattr(case, 'request_method') else ''
                    }
                
                flow_steps.append({
                    'name': case.title,
                    'variables': case.variables or {},
                    'setup_script': case.setup_script or '',
                    'teardown_script': case.teardown_script or '',
                    'request': {
                        'method': interface.get('method', ''),
                        'path': interface.get('url', ''),
                        'headers': headers,
                        'data': request_data.get('json', {}),
                        'params': case.params or {},
                        'validate': case.validate or [],
                        'extract': case.extract or []
                    }
                })
            
            test_flows.append({
                'name': f'Flow-{scene.name}',
                'steps': flow_steps,
                'variables': scene.variables or {},
                'setup_script': scene.setup_script or '',
                'teardown_script': scene.teardown_script or ''
            })
            
        if not test_flows:
            # 如果没有关联业务流，则使用配置中的单接口测试
            test_flows = [{
                'name': f'Flow-{config.endpoint}',
                'variables': config.variables or {},
                'setup_script': config.setup_script or '',
                'teardown_script': config.teardown_script or '',
                'request': {
                    'method': config.request_method,
                    'path': config.endpoint,
                    'headers': config.headers,
                    'data': config.body or {},
                    'params': config.params or {},
                    'validate': config.validate or [],
                    'extract': config.extract or []
                }
            }]
        
        # 设置测试环境
        engine.setup_test(
            host=config.host,
            test_flows=test_flows,
            global_variables=config.global_variables or {},
            think_time=config.think_time,  # 思考时间
            max_retries=config.max_retries,  # 最大重试次数
            retry_interval=config.retry_interval  # 重试间隔
        )
        
        # 根据测试模式配置参数
        if config.test_mode == 'concurrent':
            # 并发模式: 指定时间内保持固定并发用户数
            engine.start_test(
                user_count=config.vus,  # 并发用户数
                spawn_rate=config.vus / config.ramp_up if config.ramp_up else config.vus,  # 用户生成速率
                run_time=config.duration  # 持续时间
            )
        elif config.test_mode == 'step':
            # 阶梯模式: 逐步增加并发用户数
            if not (config.step_users and config.step_time):
                raise ValueError('阶梯模式参数不完整')
            current_users = 0
            while current_users < config.vus:
                current_users += config.step_users
                if current_users > config.vus:
                    current_users = config.vus
                engine.start_test(
                    user_count=current_users,     # 当前阶梯的用户数
                    spawn_rate=config.step_users, # 用户增加速率
                    run_time=config.step_time     # 当前阶梯持续时间
                )
        elif config.test_mode == 'error_rate':
            # 错误率模式: 根据错误率动态调整并发用户数
            if not config.error_threshold:
                raise ValueError('错误率模式参数不完整')
            
            current_users = config.vus // 2  # 从一半的目标用户数开始
            min_users = 1
            max_users = config.vus
            check_interval = 10  # 每10秒检查一次错误率
            start_time = time.time()
            
            while True:
                # 启动当前并发用户数的测试
                engine.start_test(
                    user_count=current_users,
                    spawn_rate=config.vus / config.ramp_up if config.ramp_up else config.vus,
                    run_time=check_interval
                )
                
                # 获取测试数据
                stats = engine.get_test_stats()
                current_error_rate = stats.get('failure_rate', 0)
                
                # 根据错误率调整并发用户数
                if current_error_rate > config.error_threshold:
                    # 错误率过高，减少用户数
                    max_users = current_users
                    current_users = max(min_users, (current_users + min_users) // 2)
                else:
                    # 错误率在阈值内，尝试增加用户数
                    min_users = current_users
                    current_users = min(max_users, (current_users + max_users) // 2)
                
                # 如果用户数收敛或达到最大时间，结束测试
                if max_users - min_users <= 1 or (config.duration and time.time() - start_time >= config.duration):
                    break

        # 收集测试数据
        stats = engine.get_test_stats()
        system_stats = engine.get_system_stats()
        
        # 更新报告数据
        report.metrics.update({
            'response_times': stats.get('response_times', {}),      # 响应时间分布
            'num_requests': stats.get('num_requests', 0),          # 总请求数
            'num_failures': stats.get('num_failures', 0),          # 失败请求数
            'average_response_time': stats.get('avg_response_time', 0),  # 平均响应时间
            'percentiles': stats.get('percentiles', {}),           # 响应时间百分位数
            'system_stats': system_stats,                          # 系统资源使用统计
            'variables': engine.get_variables_stats(),             # 变量使用统计
            'validations': engine.get_validation_stats()           # 验证结果统计
        })
        
        # 更新错误信息
        for error in stats.get('errors', []):
            report.errors.append({
                'error_type': error.get('error_type', 'Unknown'),      # 错误类型
                'error_message': error.get('error_message', ''),       # 错误信息
                'occurrence_count': error.get('count', 1),            # 出现次数
                'request_data': error.get('request_data'),            # 请求数据
                'response_data': error.get('response_data'),          # 响应数据
                'variables': error.get('variables')                   # 相关变量
            })
        
        # 生成测试总结
        report.summary = {
            'total_requests': stats.get('num_requests', 0),          # 总请求数
            'total_failures': stats.get('num_failures', 0),          # 失败请求数
            'failure_rate': stats.get('failure_rate', 0),            # 失败率
            'average_response_time': stats.get('avg_response_time', 0),  # 平均响应时间
            'requests_per_second': stats.get('requests_per_sec', 0),   # 每秒请求数
            'validation_success_rate': stats.get('validation_success_rate', 0),  # 验证成功率
            'variable_usage': stats.get('variable_usage', {})          # 变量使用情况
        }
        
        # 更新测试计划状态
        plan.status = 'completed'
        plan.save()
        
        # 完成报告
        report.end_time = timezone.now()
        report.save()
        
        return True
    except Exception as e:
        if plan:
            plan.status = 'failed'
            plan.save()
        return False

@shared_task
def stop_performance_test(plan_id):
    """停止性能测试任务
    
    Args:
        plan_id: 性能测试计划ID
        
    Returns:
        bool: 操作结果，成功返回True，失败返回False
    """
    try:
        plan = PerformanceTestPlan.objects.get(id=plan_id)
        
        # TODO: 实现停止测试逻辑
        # 1. 停止测试执行
        # 2. 清理测试环境
        
        # 更新测试计划状态
        plan.status = 'completed'
        plan.save()
        
        # 更新报告结束时间
        report = plan.reports.last()
        if report and not report.end_time:
            report.end_time = timezone.now()
            report.save()
        
        return True
    except Exception as e:
        if plan:
            plan.status = 'failed'
            plan.save()
        return False