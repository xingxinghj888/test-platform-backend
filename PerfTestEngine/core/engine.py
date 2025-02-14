"""性能测试引擎主类模块

提供性能测试的核心功能实现，包括：
- 测试环境配置
- 测试执行控制
- 测试数据收集
- 测试结果分析
"""

import threading
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Dict, List, Optional, Type
from locust import Environment
from .test_user import PerformanceTestUser
from .performance_stats import StatsCollector
from .test_mode import StrategyFactory
from .report import ReportGenerator
from .datasource import DataSourceFactory
from .plugin import PluginManager
from ..ApiTestEngine.core.cases import CaseRunLog

class PerformanceTestEngine:
    """性能测试引擎主类
    
    负责管理整个性能测试的生命周期，包括：
    - 测试环境初始化
    - 测试用户管理
    - 测试执行控制
    - 测试数据收集
    """
    
    def __init__(self):
        """初始化测试引擎"""
        self.env = None
        self.strategy = None
        self.stats_collector = None
        self.report_generator = ReportGenerator()
        self.data_source = None
        self.test_plan = None
        self._monitor_thread = None
        self._stop_monitor = False
        self._config_lock = threading.Lock()
        self.plugin_manager = PluginManager()
        self.data_storage = None
        
        # 初始化日志系统
        self.logger = CaseRunLog()
        self.log_data = []
        self.logger.info_log('性能测试引擎初始化完成')


    def register_plugin(self, plugin_type: str, plugin_class: Type[Plugin]) -> None:
        """注册插件
        
        Args:
            plugin_type: 插件类型(protocol/datasource/report)
            plugin_class: 插件类
        """
        self.logger.debug_log(f'注册插件: {plugin_type} - {plugin_class.__name__}')
        self.plugin_manager.register_plugin(plugin_type, plugin_class)
        
    def setup_test(self, host: str, plan_data: Dict):
        """配置测试环境
        
        Args:
            host: 目标主机地址
            plan_data: 测试计划配置数据
        """
        self.logger.info_log(f'开始配置测试环境: {host}')
        with self._config_lock:
            # 初始化数据存储
            test_id = str(int(time.time()))
            self.data_storage = PerformanceDataStorage(test_id)
            self.logger.debug_log('初始化数据存储管理器')
            
            # 解析测试计划
            self.test_plan = TestPlan(plan_data)
            self.logger.debug_log(f'测试计划配置: {plan_data}')
            
            # 创建测试环境
            self.env = Environment(user_classes=[PerformanceTestUser])
            self.env.host = host
            
            # 配置测试用户类
            self.env.user_classes[0].test_flows = self.test_plan.flows
            self.env.user_classes[0].global_variables = self.test_plan.variables
            
            # 初始化数据收集器
            self.stats_collector = StatsCollector(self.env)
            
            # 初始化报告生成器
            if 'report_plugin' in plan_data:
                plugin_config = plan_data['report_plugin']
                plugin = self.plugin_manager.get_plugin('report', plugin_config['type'])()
                plugin.initialize(plugin_config.get('config', {}))
                self.report_generator = plugin
            else:
                self.report_generator = ReportGenerator()
            self.report_generator.start_test()
            
            # 初始化数据源
            if 'data_source' in plan_data:
                source_config = plan_data['data_source']
                if source_config['type'] in self.plugin_manager.get_plugin_names('datasource'):
                    plugin = self.plugin_manager.get_plugin('datasource', source_config['type'])()
                    plugin.initialize(source_config.get('config', {}))
                    self.data_source = plugin
                else:
                    self.data_source = DataSourceFactory.create_data_source(
                        source_type=source_config['type'],
                        config=source_config['config']
                    )
            
    def start_test(self, test_mode: str, config: Dict):
        """启动性能测试
        
        Args:
            test_mode: 测试模式（concurrent/step/error_rate）
            config: 测试配置参数
        """
        self.logger.info_log(f'开始执行性能测试: 模式={test_mode}')
        self.logger.debug_log(f'测试配置参数: {config}')
        
        with self._config_lock:
            if not self.env:
                self.logger.error_log('测试环境未初始化')
                raise RuntimeError('测试环境未初始化')
                
            # 创建并执行测试策略
            self.strategy = StrategyFactory.create_strategy(test_mode, self.env)
            self.logger.info_log(f'创建测试策略: {test_mode}')
            
            # 启动性能监控
            self._start_monitoring()
            self.logger.info_log('启动性能监控')
            
            # 执行测试
            self.logger.info_log('开始执行测试策略')
            self.strategy.execute(config)
                
    def stop_test(self):
        """停止性能测试"""
        self.logger.info_log('停止性能测试')
        with self._config_lock:
            if self.strategy and self.strategy.runner:
                self.strategy.runner.stop()
                self.logger.info_log('停止测试策略执行')
                
            # 停止性能监控
            self._stop_monitoring()
            self.logger.info_log('停止性能监控')
            
            # 完成报告生成
            self.report_generator.end_test()
            self.logger.info_log('完成测试报告生成')
            
            # 清理数据存储
            if self.data_storage:
                self.data_storage.cleanup()
                self.logger.info_log('清理测试数据存储')

    def get_test_stats(self) -> Dict:
        """获取测试统计数据"""
        if not self.env or not self.strategy or not self.strategy.runner:
            return {}
            
        stats = {
            'num_requests': self.env.stats.num_requests,
            'num_failures': self.env.stats.num_failures,
            'avg_response_time': self.env.stats.total.avg_response_time,
            'current_rps': self.env.stats.total.current_rps,
            'median_response_time': self.env.stats.total.median_response_time,
            'percentile_95': self.env.stats.total.get_response_time_percentile(0.95),
            'percentile_99': self.env.stats.total.get_response_time_percentile(0.99),
            'error_types': self._get_error_types(),
            'user_count': self.strategy.runner.user_count,
        }
        
        # 存储数据到Redis
        if self.data_storage:
            self.data_storage.store_test_data(stats)
        
        # 更新报告数据
        self.report_generator.update_test_stats(stats)
        return stats
        
    def get_system_stats(self) -> Dict:
        """获取系统资源使用统计"""
        if not self.stats_collector:
            return {}
            
        stats = self.stats_collector.get_stats()
        self.report_generator.update_system_stats(stats)
        return stats
        
    def get_report(self) -> Dict:
        """获取测试报告"""
        return self.report_generator.generate_report()
        
    def _start_monitoring(self):
        """启动性能监控线程"""
        if self.stats_collector and not self._monitor_thread:
            self._stop_monitor = False
            self._monitor_thread = threading.Thread(
                target=self.stats_collector.start_collecting,
                args=(lambda: self._stop_monitor,)
            )
            self._monitor_thread.start()
            
    def _stop_monitoring(self):
        """停止性能监控线程"""
        if self._monitor_thread:
            self._stop_monitor = True
            self._monitor_thread.join()
            self._monitor_thread = None
            
    def _get_error_types(self) -> Dict:
        """获取错误类型统计"""
        error_types = {}
        for error in self.env.stats.errors.values():
            error_types[error.name] = {
                'count': error.occurrences,
                'error_type': error.error,
                'method': error.method,
                'name': error.name
            }
        return error_types