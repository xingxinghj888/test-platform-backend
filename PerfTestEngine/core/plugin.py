"""插件管理模块

提供插件系统的核心功能，支持：
- 协议插件扩展
- 数据源插件扩展
- 报告生成插件扩展
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Type

class Plugin(ABC):
    """插件基类
    
    所有插件必须继承此类并实现相关接口
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """插件名称"""
        pass
        
    @property
    @abstractmethod
    def version(self) -> str:
        """插件版本"""
        pass
        
    @property
    @abstractmethod
    def description(self) -> str:
        """插件描述"""
        pass
        
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """初始化插件
        
        Args:
            config: 插件配置参数
        """
        pass
        
class ProtocolPlugin(Plugin):
    """协议插件基类
    
    用于扩展支持新的协议类型，如WebSocket、gRPC等
    """
    
    @abstractmethod
    def create_client(self, config: Dict[str, Any]) -> Any:
        """创建协议客户端
        
        Args:
            config: 客户端配置参数
            
        Returns:
            Any: 协议客户端实例
        """
        pass
        
    @abstractmethod
    def execute_request(self, client: Any, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行请求
        
        Args:
            client: 协议客户端实例
            request_data: 请求参数
            
        Returns:
            Dict[str, Any]: 响应数据
        """
        pass
        
class DataSourcePlugin(Plugin):
    """数据源插件基类
    
    用于扩展支持新的数据源类型
    """
    
    @abstractmethod
    def get_data(self) -> Dict[str, Any]:
        """获取数据
        
        Returns:
            Dict[str, Any]: 数据字典
        """
        pass
        
    @abstractmethod
    def reset(self) -> None:
        """重置数据源状态"""
        pass
        
class ReportPlugin(Plugin):
    """报告生成插件基类
    
    用于扩展支持新的报告格式和展示方式
    """
    
    @abstractmethod
    def generate(self, test_data: Dict[str, Any], system_data: Dict[str, Any]) -> Any:
        """生成报告
        
        Args:
            test_data: 测试数据
            system_data: 系统数据
            
        Returns:
            Any: 生成的报告
        """
        pass
        
class PluginManager:
    """插件管理器
    
    负责插件的注册、获取和管理
    """
    
    def __init__(self):
        self._plugins: Dict[str, Dict[str, Type[Plugin]]] = {
            'protocol': {},
            'datasource': {},
            'report': {}
        }
        
    def register_plugin(self, plugin_type: str, plugin_class: Type[Plugin]) -> None:
        """注册插件
        
        Args:
            plugin_type: 插件类型
            plugin_class: 插件类
        """
        if plugin_type not in self._plugins:
            raise ValueError(f'不支持的插件类型: {plugin_type}')
            
        plugin = plugin_class()
        self._plugins[plugin_type][plugin.name] = plugin_class
        
    def get_plugin(self, plugin_type: str, plugin_name: str) -> Type[Plugin]:
        """获取插件类
        
        Args:
            plugin_type: 插件类型
            plugin_name: 插件名称
            
        Returns:
            Type[Plugin]: 插件类
        """
        if plugin_type not in self._plugins:
            raise ValueError(f'不支持的插件类型: {plugin_type}')
            
        if plugin_name not in self._plugins[plugin_type]:
            raise ValueError(f'插件未注册: {plugin_name}')
            
        return self._plugins[plugin_type][plugin_name]
        
    def get_plugin_names(self, plugin_type: str) -> List[str]:
        """获取指定类型的所有插件名称
        
        Args:
            plugin_type: 插件类型
            
        Returns:
            List[str]: 插件名称列表
        """
        if plugin_type not in self._plugins:
            raise ValueError(f'不支持的插件类型: {plugin_type}')
            
        return list(self._plugins[plugin_type].keys())