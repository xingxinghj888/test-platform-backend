"""性能测试数据源管理模块

提供测试数据的加载和管理功能，支持多种数据源类型：
- CSV文件数据源
- 数据池数据源
- 数据生成器
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Iterator, List
import csv
import random
import string
from faker import Faker
import re

class DataSourceError(Exception):
    pass

class DataSource(ABC):
    """数据源基类"""
    
    def __init__(self):
        self.validation_rules = {}
        self.transform_rules = {}
        self._cache = {}
        self._cache_size = 1000  # 默认缓存大小
        self._cache_hits = 0
        self._cache_misses = 0
    
    def _get_cache_key(self, **kwargs) -> str:
        """生成缓存键
        
        Args:
            **kwargs: 用于生成缓存键的参数
            
        Returns:
            str: 缓存键
        """
        return str(hash(frozenset(kwargs.items())))
    
    def _get_from_cache(self, cache_key: str) -> Dict[str, Any]:
        """从缓存获取数据
        
        Args:
            cache_key: 缓存键
            
        Returns:
            Dict[str, Any]: 缓存的数据，如果不存在返回None
        """
        if cache_key in self._cache:
            self._cache_hits += 1
            return self._cache[cache_key]
        self._cache_misses += 1
        return None
    
    def _add_to_cache(self, cache_key: str, data: Dict[str, Any]):
        """添加数据到缓存
        
        Args:
            cache_key: 缓存键
            data: 要缓存的数据
        """
        if len(self._cache) >= self._cache_size:
            # 简单的LRU策略：删除第一个元素
            self._cache.pop(next(iter(self._cache)))
        self._cache[cache_key] = data
    
    @abstractmethod
    def get_data(self) -> Dict[str, Any]:
        """获取数据
        
        Returns:
            Dict[str, Any]: 包含变量名和值的字典
        """
        pass
        
    def validate_data(self, data: List[Dict[str, Any]]) -> bool:
        """验证数据是否符合规则"""
        if not self.validation_rules:
            return True

        for item in data:
            for field, rules in self.validation_rules.items():
                if field not in item:
                    raise DataSourceError(f'字段 {field} 不存在')
                
                value = item[field]
                # 验证数据类型
                if 'type' in rules:
                    expected_type = rules['type']
                    if not isinstance(value, eval(expected_type)):
                        raise DataSourceError(f'字段 {field} 类型错误，期望 {expected_type}')
                
                # 验证数值范围
                if 'range' in rules:
                    min_val, max_val = rules['range']
                    if not (min_val <= float(value) <= max_val):
                        raise DataSourceError(f'字段 {field} 值超出范围 [{min_val}, {max_val}]')
                
                # 验证字符串格式
                if 'pattern' in rules:
                    if not re.match(rules['pattern'], str(value)):
                        raise DataSourceError(f'字段 {field} 格式不符合要求')
                
                # 验证枚举值
                if 'enum' in rules:
                    if value not in rules['enum']:
                        raise DataSourceError(f'字段 {field} 值不在允许范围内')
                
                # 验证长度
                if 'length' in rules:
                    min_len, max_len = rules['length']
                    if not (min_len <= len(str(value)) <= max_len):
                        raise DataSourceError(f'字段 {field} 长度不符合要求')

        return True

    def transform_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """转换数据格式"""
        if not self.transform_rules:
            return data

        transformed_data = []
        for item in data:
            transformed_item = {}
            for target_field, rule in self.transform_rules.items():
                source_field = rule.get('source_field')
                transform_type = rule.get('type', 'direct')
                
                try:
                    if transform_type == 'direct':
                        transformed_item[target_field] = item.get(source_field)
                    elif transform_type == 'format':
                        template = rule.get('template', '{}')
                        transformed_item[target_field] = template.format(item.get(source_field))
                    elif transform_type == 'combine':
                        fields = rule.get('fields', [])
                        separator = rule.get('separator', '')
                        values = [str(item.get(f, '')) for f in fields]
                        transformed_item[target_field] = separator.join(values)
                    elif transform_type == 'calculate':
                        expression = rule.get('expression')
                        variables = {k: item.get(v) for k, v in rule.get('variables', {}).items()}
                        transformed_item[target_field] = eval(expression, {}, variables)
                    elif transform_type == 'map':
                        mapping = rule.get('mapping', {})
                        value = item.get(source_field)
                        transformed_item[target_field] = mapping.get(value, value)
                    elif transform_type == 'split':
                        separator = rule.get('separator', ',')
                        index = rule.get('index', 0)
                        value = item.get(source_field, '')
                        parts = value.split(separator)
                        transformed_item[target_field] = parts[index] if len(parts) > index else ''
                except Exception as e:
                    raise DataSourceError(f'数据转换失败: {str(e)}')
            
            transformed_data.append(transformed_item)
        
        return transformed_data
        
    def get_cache_stats(self) -> Dict[str, int]:
        """获取缓存统计信息
        
        Returns:
            Dict[str, int]: 包含缓存命中次数、未命中次数和缓存大小的字典
        """
        return {
            'hits': self._cache_hits,
            'misses': self._cache_misses,
            'size': len(self._cache)
        }

    def clear_cache(self) -> None:
        """清空缓存"""
        self._cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0

class CSVDataSource(DataSource):
    """CSV文件数据源"""
    
    def __init__(self, file_path: str, variable_mapping: Dict[str, str]):
        super().__init__()
        self.file_path = file_path
        self.variable_mapping = variable_mapping
        self._data_iterator = self._load_data()
        
    def _load_data(self) -> Iterator[Dict[str, str]]:
        """加载CSV数据"""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
            while True:
                for row in data:
                    yield {var_name: row[col_name] 
                          for var_name, col_name in self.variable_mapping.items()}
                    
    def get_data(self) -> Dict[str, Any]:
        cache_key = self._get_cache_key()
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
            
        data = next(self._data_iterator)
        self._add_to_cache(cache_key, data)
        return data

class PoolDataSource(DataSource):
    """数据池数据源"""
    
    def __init__(self, data_pool: Dict[str, list]):
        super().__init__()
        self.data_pool = data_pool
        
    def get_data(self) -> Dict[str, Any]:
        cache_key = self._get_cache_key()
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
            
        data = {var_name: random.choice(values) 
                for var_name, values in self.data_pool.items()}
        self._add_to_cache(cache_key, data)
        return data

class GeneratorDataSource(DataSource):
    """数据生成器"""
    
    def __init__(self, generator_config: Dict[str, Dict]):
        super().__init__()
        self.generator_config = generator_config
        self.faker = Faker()
        
    def get_data(self) -> Dict[str, Any]:
        data = {}
        for var_name, config in self.generator_config.items():
            generator_type = config.get('type', 'string')
            if generator_type == 'string':
                length = config.get('length', 10)
                data[var_name] = ''.join(random.choices(
                    string.ascii_letters + string.digits, k=length))
            elif generator_type == 'number':
                min_val = config.get('min', 0)
                max_val = config.get('max', 100)
                data[var_name] = random.randint(min_val, max_val)
            elif generator_type == 'faker':
                provider = config.get('provider', 'name')
                data[var_name] = getattr(self.faker, provider)()
        return data
        
class DataSourceFactory:
    """数据源工厂类"""
    
    @staticmethod
    def create_data_source(source_type: str, config: Dict) -> DataSource:
        """创建数据源实例
        
        Args:
            source_type: 数据源类型
            config: 数据源配置
            
        Returns:
            DataSource: 数据源实例
        """
        if source_type == 'csv':
            return CSVDataSource(
                file_path=config['file_path'],
                variable_mapping=config['variable_mapping']
            )
        elif source_type == 'pool':
            return PoolDataSource(data_pool=config['data_pool'])
        elif source_type == 'generator':
            return GeneratorDataSource(generator_config=config['generator_config'])
        else:
            raise ValueError(f'不支持的数据源类型: {source_type}')