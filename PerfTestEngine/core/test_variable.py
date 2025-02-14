"""变量管理模块

提供性能测试中的变量管理功能，包括：
- 环境变量管理
- 临时变量管理
- 变量引用解析
"""

from typing import Dict, Any
from collections import OrderedDict
import re
import json
from numbers import Number

class VariableManager:
    """变量管理器
    
    管理性能测试过程中的变量，包括环境变量和临时变量
    """
    
    def __init__(self):
        """初始化变量管理器"""
        self._env_vars: Dict[str, Any] = {}
        self._temp_vars: Dict[str, Any] = {}
        
    def set_env_variable(self, name: str, value: Any) -> None:
        """设置环境变量
        
        Args:
            name: 变量名
            value: 变量值
        """
        self._env_vars[name] = value
        
    def set_temp_variable(self, name: str, value: Any) -> None:
        """设置临时变量
        
        Args:
            name: 变量名
            value: 变量值
        """
        self._temp_vars[name] = value
        
    def get_variable(self, name: str) -> Any:
        """获取变量值
        
        优先从临时变量中获取，如果不存在则从环境变量中获取
        
        Args:
            name: 变量名
            
        Returns:
            Any: 变量值，如果变量不存在则返回None
        """
        return self._temp_vars.get(name, self._env_vars.get(name))
        
    def delete_env_variable(self, name: str) -> None:
        """删除环境变量
        
        Args:
            name: 变量名
        """
        if name in self._env_vars:
            del self._env_vars[name]
            
    def delete_temp_variable(self, name: str) -> None:
        """删除临时变量
        
        Args:
            name: 变量名
        """
        if name in self._temp_vars:
            del self._temp_vars[name]
            
    def clear_temp_variables(self) -> None:
        """清空所有临时变量"""
        self._temp_vars.clear()
        
    def parse_variable_references(self, data: Any) -> Any:
        """解析数据中的变量引用
        
        支持在字符串中使用${variable}格式引用变量
        
        Args:
            data: 需要解析的数据
            
        Returns:
            Any: 解析后的数据
            
        Raises:
            ValueError: 当引用的变量不存在时抛出
        """
        if isinstance(data, OrderedDict):
            data = dict(data)
            
        if not isinstance(data, str):
            data = str(data)
            
        pattern = r'\$\{(.+?)\}'
        while re.search(pattern, data):
            match = re.search(pattern, data)
            var_ref = match.group(0)
            var_name = match.group(1)
            
            value = self.get_variable(var_name)
            if value is None:
                raise ValueError(f'变量引用错误：变量 {var_name} 不存在')
                
            if isinstance(value, Number):
                # 处理数字类型
                start = data.find(var_ref)
                full_ref = data[start-1:start+len(var_ref)+1]
                data = data.replace(full_ref, str(value))
            elif isinstance(value, str) and "'" in value:
                # 处理包含单引号的字符串
                data = data.replace(var_ref, value.replace("'", '"'))
            else:
                data = data.replace(var_ref, str(value))
                
        try:
            return eval(data)
        except:
            return data