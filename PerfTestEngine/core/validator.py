"""配置验证模块

提供测试配置的验证功能，包括：
- 基础配置验证
- 测试策略配置验证
- 数据源配置验证
"""

from typing import Dict, Any
from abc import ABC, abstractmethod

class ConfigValidator(ABC):
    """配置验证器基类
    
    所有具体验证器的抽象基类，定义了验证器的基本接口。
    """
    
    @abstractmethod
    def validate(self, config: Dict[str, Any]) -> None:
        """验证配置
        
        Args:
            config: 待验证的配置字典
            
        Raises:
            ValueError: 当配置无效时抛出
        """
        pass
        
class ConcurrentStrategyValidator(ConfigValidator):
    """并发模式配置验证器"""
    
    def validate(self, config: Dict[str, Any]) -> None:
        """验证并发模式配置
        
        Args:
            config: 配置字典，必须包含以下字段：
                - vus: 并发用户数
                - ramp_up: 可选，加压时间(秒)
                - duration: 可选，测试持续时间(秒)
                - data_update_interval: 可选，数据更新间隔(秒)
                
        Raises:
            ValueError: 当配置无效时抛出
        """
        if 'vus' not in config:
            raise ValueError('并发模式配置缺少必需参数：vus')
            
        if not isinstance(config['vus'], int) or config['vus'] <= 0:
            raise ValueError('并发用户数必须是正整数')
            
        if 'ramp_up' in config and (not isinstance(config['ramp_up'], (int, float)) or config['ramp_up'] <= 0):
            raise ValueError('加压时间必须是正数')
            
        if 'duration' in config and (not isinstance(config['duration'], (int, float)) or config['duration'] <= 0):
            raise ValueError('测试持续时间必须是正数')
            
        if 'data_update_interval' in config and (not isinstance(config['data_update_interval'], int) or config['data_update_interval'] <= 0):
            raise ValueError('数据更新间隔必须是正整数')
            
class StepStrategyValidator(ConfigValidator):
    """阶梯模式配置验证器"""
    
    def validate(self, config: Dict[str, Any]) -> None:
        """验证阶梯模式配置
        
        Args:
            config: 配置字典，必须包含以下字段：
                - vus: 目标并发用户数
                - step_users: 每阶梯增加的用户数
                - step_time: 每阶梯持续时间(秒)
                
        Raises:
            ValueError: 当配置无效时抛出
        """
        required_fields = ['vus', 'step_users', 'step_time']
        for field in required_fields:
            if field not in config:
                raise ValueError(f'阶梯模式配置缺少必需参数：{field}')
                
        if not isinstance(config['vus'], int) or config['vus'] <= 0:
            raise ValueError('目标并发用户数必须是正整数')
            
        if not isinstance(config['step_users'], int) or config['step_users'] <= 0:
            raise ValueError('每阶梯增加的用户数必须是正整数')
            
        if not isinstance(config['step_time'], (int, float)) or config['step_time'] <= 0:
            raise ValueError('每阶梯持续时间必须是正数')
            
        if config['step_users'] > config['vus']:
            raise ValueError('每阶梯增加的用户数不能大于目标并发用户数')
            
class ErrorRateStrategyValidator(ConfigValidator):
    """错误率模式配置验证器"""
    
    def validate(self, config: Dict[str, Any]) -> None:
        """验证错误率模式配置
        
        Args:
            config: 配置字典，必须包含以下字段：
                - vus: 最大并发用户数
                - error_threshold: 错误率阈值
                - ramp_up: 可选，加压时间(秒)
                - duration: 可选，测试总持续时间(秒)
                
        Raises:
            ValueError: 当配置无效时抛出
        """
        if 'vus' not in config:
            raise ValueError('错误率模式配置缺少必需参数：vus')
            
        if 'error_threshold' not in config:
            raise ValueError('错误率模式配置缺少必需参数：error_threshold')
            
        if not isinstance(config['vus'], int) or config['vus'] <= 0:
            raise ValueError('最大并发用户数必须是正整数')
            
        if not isinstance(config['error_threshold'], (int, float)) or not 0 <= config['error_threshold'] <= 1:
            raise ValueError('错误率阈值必须是0到1之间的数值')
            
        if 'ramp_up' in config and (not isinstance(config['ramp_up'], (int, float)) or config['ramp_up'] <= 0):
            raise ValueError('加压时间必须是正数')
            
        if 'duration' in config and (not isinstance(config['duration'], (int, float)) or config['duration'] <= 0):
            raise ValueError('测试总持续时间必须是正数')
            
class ValidatorFactory:
    """验证器工厂类
    
    用于创建对应测试策略的配置验证器实例。
    """
    
    _validators = {
        'concurrent': ConcurrentStrategyValidator,
        'step': StepStrategyValidator,
        'error_rate': ErrorRateStrategyValidator
    }
    
    @classmethod
    def create_validator(cls, strategy_type: str) -> ConfigValidator:
        """创建验证器实例
        
        Args:
            strategy_type: 策略类型，可选值：'concurrent'、'step'、'error_rate'
            
        Returns:
            ConfigValidator: 验证器实例
            
        Raises:
            ValueError: 当指定的策略类型不支持时抛出
        """
        validator_class = cls._validators.get(strategy_type)
        if not validator_class:
            raise ValueError(f'不支持的测试策略类型: {strategy_type}')
        return validator_class()