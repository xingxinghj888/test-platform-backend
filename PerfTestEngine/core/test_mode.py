"""性能测试执行策略模块

提供不同的测试执行策略实现，包括：
- 并发模式：固定并发用户数
- 阶梯模式：逐步增加并发用户数
- 错误率模式：基于错误率动态调整并发用户数
"""

from abc import ABC, abstractmethod
from typing import Dict
import time
import logging
from locust import Environment
from .datasource import DataSource
from .case_run_log import CaseRunLog

class TestStrategy(ABC):
    """测试执行策略基类
    
    所有具体测试策略的抽象基类，定义了策略的基本接口。
    """
    
    def __init__(self, env: Environment, data_source: DataSource = None):
        """初始化策略
        
        Args:
            env: Locust测试环境实例用于创建和管理测试运行器
            data_source: 可选，数据源实例，用于提供测试数据
        """
        self.env = env
        self.runner = None
        self.data_source = data_source
        self._current_data = None
        self.logger = CaseRunLog()
        self._paused = False
        self._error_handlers = {}
        self._status_listeners = []
        
    def get_test_data(self) -> Dict:
        """获取测试数据
        
        从数据源获取测试数据。如果数据源未设置，返回空字典。
        
        Returns:
            Dict: 测试数据字典
        """
        if not self.data_source:
            return {}
            
        if not self._current_data:
            self._current_data = self.data_source.get_data()
            
        # 更新全局变量
        if self._current_data:
            self.env.user_classes[0].global_variables.update(self._current_data)
            
        return self._current_data
        
    def update_test_data(self) -> None:
        """更新测试数据
        
        从数据源获取新的测试数据。如果数据源未设置，不执行任何操作。
        """
        if self.data_source:
            self._current_data = self.data_source.get_data()
            # 更新全局变量
            if self._current_data:
                self.env.user_classes[0].global_variables.update(self._current_data)
            
    def add_error_handler(self, error_type: type, handler: callable) -> None:
        """添加错误处理器
        
        Args:
            error_type: 错误类型
            handler: 处理函数
        """
        self._error_handlers[error_type] = handler
        
    def add_status_listener(self, listener: callable) -> None:
        """添加状态监听器
        
        Args:
            listener: 状态变更监听函数
        """
        self._status_listeners.append(listener)
        
    def notify_status_change(self, status: str, data: Dict = None) -> None:
        """通知状态变更
        
        Args:
            status: 状态名称
            data: 可选，状态相关数据
        """
        for listener in self._status_listeners:
            try:
                listener(status, data)
            except Exception as e:
                self.logger.error(f'状态监听器执行失败: {str(e)}')
                
    def handle_error(self, error: Exception) -> None:
        """处理错误
        
        Args:
            error: 异常对象
        """
        handler = self._error_handlers.get(type(error))
        if handler:
            try:
                handler(error)
            except Exception as e:
                self.logger.error(f'错误处理器执行失败: {str(e)}')
        else:
            self.logger.error(f'未处理的错误: {str(error)}')
            
    def pause(self) -> None:
        """暂停测试"""
        if self.runner and not self._paused:
            self._paused = True
            self.runner.stop()
            self.notify_status_change('paused')
            
    def resume(self) -> None:
        """恢复测试"""
        if self.runner and self._paused:
            self._paused = False
            self.runner.start(user_count=self.runner.target_user_count)
            self.notify_status_change('resumed')
            
    @abstractmethod
    def execute(self, config: Dict) -> None:
        """执行测试
        
        Args:
            config: 测试配置参数字典，包含具体策略所需的配置项
        """
        pass
        
class ConcurrentStrategy(TestStrategy):
    """并发模式策略
    
    固定并发用户数执行测试。在整个测试过程中保持固定数量的并发用户。
    """
    
    def execute(self, config: Dict) -> None:
        """执行并发模式测试
        
        Args:
            config: 测试配置参数字典，必须包含以下字段：
                - vus: 并发用户数
                - ramp_up: 可选，加压时间(秒)
                - duration: 可选，测试持续时间(秒)
                - data_update_interval: 可选，数据更新间隔(秒)
        """
        try:
            # 验证配置
            validator = ConcurrentStrategyValidator()
            validator.validate(config)
            
            self.runner = self.env.create_local_runner()
            self.notify_status_change('starting', {'config': config})
        
        # 初始化测试数据
            # 初始化测试数据
            self.get_test_data()
        except Exception as e:
            self.logger.error(f'执行并发模式测试失败: {str(e)}')
            self.handle_error(e)
            raise
        
        # 启动测试
        self.runner.start(
            user_count=config['vus'],
            spawn_rate=config['vus'] / config.get('ramp_up', 1) if config.get('ramp_up') else config['vus']
        )
        
        # 执行测试并定期更新数据
        if config.get('duration'):
            start_time = time.time()
            update_interval = config.get('data_update_interval', 60)  # 默认60秒更新一次数据
            last_update = start_time
            
            while time.time() - start_time < config['duration']:
                if time.time() - last_update >= update_interval:
                    self.update_test_data()
                    last_update = time.time()
                time.sleep(1)
            
            self.runner.stop()
            
class StepStrategy(TestStrategy):
    """阶梯模式策略
    
    逐步增加并发用户数，按照配置的步长和时间间隔增加用户数，直到达到目标并发数。
    """
    
    def execute(self, config: Dict) -> None:
        """执行阶梯模式测试
        
        Args:
            config: 测试配置参数字典，必须包含以下字段：
                - vus: 目标并发用户数
                - step_users: 每阶梯增加的用户数
                - step_time: 每阶梯持续时间(秒)
        """
        try:
            # 验证配置
            validator = StepStrategyValidator()
            validator.validate(config)
            
            self.runner = self.env.create_local_runner()
            self.notify_status_change('starting', {'config': config})
            
            # 初始化测试数据
            self.get_test_data()
            current_users = 0
            
            # 执行阶梯加压测试
            while current_users < config['vus']:
                current_users += config['step_users']
                if current_users > config['vus']:
                    current_users = config['vus']
                    
                self.runner.start(
                    user_count=current_users,
                    spawn_rate=config['step_users']
                )
                self.runner.run(config['step_time'])
                
        except Exception as e:
            self.logger.error(f'执行阶梯模式测试失败: {str(e)}')
            self.handle_error(e)
            raise
            
class ErrorRateStrategy(TestStrategy):
    """错误率模式策略
    
    基于错误率动态调整并发用户数。当错误率超过阈值时减少用户数，
    当错误率低于阈值时增加用户数，通过二分查找方式找到最优并发数。
    """
    
    def execute(self, config: Dict) -> None:
        """执行错误率模式测试
        
        Args:
            config: 测试配置参数字典，必须包含以下字段：
                - vus: 最大并发用户数
                - error_threshold: 错误率阈值
                - ramp_up: 可选，加压时间(秒)
                - duration: 可选，测试总持续时间(秒)
        """
        try:
            # 验证配置
            validator = ErrorRateStrategyValidator()
            validator.validate(config)
            
            self.runner = self.env.create_local_runner()
            self.notify_status_change('starting', {'config': config})
            self.logger.info(f'开始执行错误率模式测试，目标错误率阈值: {config["error_threshold"]}')
            
            current_users = config['vus'] // 2  # 从最大用户数的一半开始
            min_users = 1
            max_users = config['vus']
            check_interval = 10  # 每10秒检查一次错误率
            start_time = time.time()
            
            while True:
                self.runner.start(
                    user_count=current_users,
                    spawn_rate=config['vus'] / config.get('ramp_up', 1) if config.get('ramp_up') else config['vus']
                )
                self.runner.run(check_interval)
                
                stats = self.runner.stats
                current_error_rate = stats.total.fail_ratio if stats.total.num_requests > 0 else 0
                
                if current_error_rate > config['error_threshold']:
                    max_users = current_users
                    current_users = max(min_users, (current_users + min_users) // 2)
                else:
                    min_users = current_users
                    current_users = min(max_users, (current_users + max_users) // 2)
                    
                if max_users - min_users <= 1 or (config.get('duration') and time.time() - start_time >= config['duration']):
                    break
                    
        except Exception as e:
            self.logger.error(f'执行错误率模式测试失败: {str(e)}')
            self.handle_error(e)
            raise
            
class StrategyFactory:
    """测试策略工厂类
    
    用于根据策略类型创建对应的测试策略实例。支持并发模式、阶梯模式和错误率模式。
    """
    
    _strategies = {
        'concurrent': ConcurrentStrategy,
        'step': StepStrategy,
        'error_rate': ErrorRateStrategy
    }
    
    @classmethod
    def create_strategy(cls, strategy_type: str, env: Environment, data_source: DataSource = None) -> TestStrategy:
        """创建测试策略实例
        
        Args:
            strategy_type: 策略类型，可选值：'concurrent'、'step'、'error_rate'
            env: Locust测试环境实例
            data_source: 可选，数据源实例，用于提供测试数据
            
        Returns:
            TestStrategy: 测试策略实例
            
        Raises:
            ValueError: 当指定的策略类型不支持时抛出
        """
        strategy_class = cls._strategies.get(strategy_type)
        if not strategy_class:
            raise ValueError(f'不支持的测试策略类型: {strategy_type}')
        return strategy_class(env, data_source)