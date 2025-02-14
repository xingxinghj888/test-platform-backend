"""性能测试数据存储模块

提供性能测试数据的存储和管理功能，包括：
- Redis临时存储
- 数据批量写入MySQL
- 增量数据更新
- 数据分片管理
"""

from typing import Dict, List, Any, Optional
import json
import time
from datetime import datetime
import redis
from django.db import connection
from django.conf import settings

class PerformanceDataStorage:
    """性能测试数据存储管理类
    
    负责管理性能测试数据的存储和读取，包括：
    - 使用Redis进行实时数据缓存
    - 批量写入MySQL数据库
    - 提供增量数据更新
    - 管理数据分片和归档
    """
    
    def __init__(self, test_id: str):
        """初始化数据存储管理器
        
        Args:
            test_id: 测试任务ID，用于区分不同测试任务的数据
        """
        self.test_id = test_id
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        self.last_mysql_write = time.time()
        self.mysql_write_interval = 60  # 每60秒写入一次MySQL
        self.data_expire_time = 3600  # Redis数据过期时间（1小时）
        
    def store_test_data(self, data: Dict[str, Any]) -> None:
        """存储测试数据
        
        将数据存储到Redis，并在适当时机批量写入MySQL
        
        Args:
            data: 测试数据字典
        """
        # 添加时间戳
        data['timestamp'] = datetime.now().isoformat()
        
        # 存储到Redis
        key = f"perf_test:{self.test_id}:data:{int(time.time())}"
        self.redis_client.setex(
            key,
            self.data_expire_time,
            json.dumps(data)
        )
        
        # 更新最新数据的快照
        self.redis_client.set(
            f"perf_test:{self.test_id}:latest",
            json.dumps(data)
        )
        
        # 检查是否需要写入MySQL
        current_time = time.time()
        if current_time - self.last_mysql_write >= self.mysql_write_interval:
            self._batch_write_to_mysql()
            self.last_mysql_write = current_time
            
    def get_latest_data(self) -> Optional[Dict[str, Any]]:
        """获取最新的测试数据
        
        Returns:
            Dict: 最新的测试数据字典，如果没有数据返回None
        """
        data = self.redis_client.get(f"perf_test:{self.test_id}:latest")
        return json.loads(data) if data else None
        
    def get_data_range(self, start_time: float, end_time: float) -> List[Dict[str, Any]]:
        """获取指定时间范围内的测试数据
        
        Args:
            start_time: 开始时间戳
            end_time: 结束时间戳
            
        Returns:
            List[Dict]: 测试数据列表
        """
        keys = self.redis_client.keys(f"perf_test:{self.test_id}:data:*")
        data = []
        
        for key in keys:
            timestamp = float(key.split(':')[-1])
            if start_time <= timestamp <= end_time:
                value = self.redis_client.get(key)
                if value:
                    data.append(json.loads(value))
                    
        return sorted(data, key=lambda x: x['timestamp'])
        
    def _batch_write_to_mysql(self) -> None:
        """批量将数据写入MySQL数据库"""
        keys = self.redis_client.keys(f"perf_test:{self.test_id}:data:*")
        if not keys:
            return
            
        # 获取所有数据
        data_to_write = []
        for key in keys:
            value = self.redis_client.get(key)
            if value:
                data = json.loads(value)
                data_to_write.append(data)
                
        if not data_to_write:
            return
            
        # 批量写入MySQL
        with connection.cursor() as cursor:
            # 这里根据实际的数据库表结构构造INSERT语句
            sql = "INSERT INTO performance_test_data (test_id, timestamp, data) VALUES (%s, %s, %s)"
            values = [
                (self.test_id, data['timestamp'], json.dumps(data))
                for data in data_to_write
            ]
            cursor.executemany(sql, values)
            
        # 删除已写入的Redis数据
        self.redis_client.delete(*keys)
        
    def cleanup(self) -> None:
        """清理测试数据
        
        在测试结束时调用，确保所有数据都已写入MySQL
        """
        self._batch_write_to_mysql()
        # 清理Redis中的所有相关数据
        keys = self.redis_client.keys(f"perf_test:{self.test_id}:*")
        if keys:
            self.redis_client.delete(*keys)
