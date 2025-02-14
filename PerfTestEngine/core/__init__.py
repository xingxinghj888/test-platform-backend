"""性能测试引擎核心模块

此模块包含性能测试引擎的核心功能实现，包括：
- 测试用户行为管理
- 负载生成控制
- 性能指标收集
- 测试数据处理
"""

from .engine import PerformanceTestEngine
from .user import PerformanceTestUser
from .stats import StatsCollector
from .variable import VariableManager

__all__ = [
    'PerformanceTestEngine',
    'PerformanceTestUser',
    'StatsCollector',
    'VariableManager'
]