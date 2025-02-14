"""性能测试报告生成模块

提供测试报告的生成和格式化功能，包括：
- 实时数据统计和增量更新
- 大规模数据批量处理
- 测试结果统计和分析
- 性能指标评估
- 错误信息汇总
- 报告格式化输出
"""

from typing import Dict, List, Optional
from datetime import datetime
from .data_storage import PerformanceDataStorage

class ReportGenerator:
    """测试报告生成器"""
    
    def __init__(self, test_id: str):
        """初始化报告生成器
        
        Args:
            test_id: 测试任务ID
        """
        self.test_id = test_id
        self.start_time = None
        self.end_time = None
        self.test_stats = {}
        self.system_stats = {}
        self.error_stats = {}
        self.data_storage = PerformanceDataStorage(test_id)
        
    def start_test(self):
        """记录测试开始时间"""
        self.start_time = datetime.now()
        
    def end_test(self):
        """记录测试结束时间"""
        self.end_time = datetime.now()
        
    def update_test_stats(self, stats: Dict):
        """更新测试统计数据
        
        Args:
            stats: 测试统计数据
        """
        self.test_stats.update(stats)
        # 存储测试数据
        self.data_storage.store_test_data({
            'type': 'test_stats',
            'data': stats
        })
        
    def update_system_stats(self, stats: Dict):
        """更新系统资源统计数据
        
        Args:
            stats: 系统资源统计数据
        """
        self.system_stats.update(stats)
        # 存储系统资源数据
        self.data_storage.store_test_data({
            'type': 'system_stats',
            'data': stats
        })
        
    def update_error_stats(self, errors: List[Dict]):
        """更新错误统计数据
        
        Args:
            errors: 错误信息列表
        """
        for error in errors:
            error_key = f"{error['error_type']}_{error['name']}"
            if error_key not in self.error_stats:
                self.error_stats[error_key] = {
                    'error_type': error['error_type'],
                    'name': error['name'],
                    'count': 0,
                    'examples': []
                }
            self.error_stats[error_key]['count'] += 1
            if len(self.error_stats[error_key]['examples']) < 5:
                self.error_stats[error_key]['examples'].append({
                    'request': error.get('request_data'),
                    'response': error.get('response_data'),
                    'message': error.get('error_message')
                })
                
    def generate_summary(self) -> Dict:
        """生成测试总结
        
        Returns:
            Dict: 测试总结数据
        """
        if not self.start_time or not self.end_time:
            raise ValueError('测试时间未记录')
            
        duration = (self.end_time - self.start_time).total_seconds()
        total_requests = self.test_stats.get('num_requests', 0)
        total_failures = self.test_stats.get('num_failures', 0)
        
        return {
            'test_info': {
                'start_time': self.start_time.isoformat(),
                'end_time': self.end_time.isoformat(),
                'duration': duration,
                'concurrent_users': self.test_stats.get('user_count', 0)
            },
            'request_stats': {
                'total_requests': total_requests,
                'total_failures': total_failures,
                'success_rate': (total_requests - total_failures) / total_requests if total_requests > 0 else 0,
                'error_rate': total_failures / total_requests if total_requests > 0 else 0,
                'average_rps': total_requests / duration if duration > 0 else 0,
                'current_rps': self.test_stats.get('current_rps', 0)
            },
            'response_time': {
                'average': self.test_stats.get('avg_response_time', 0),
                'median': self.test_stats.get('median_response_time', 0),
                'p90': self.test_stats.get('percentile_90', 0),
                'p95': self.test_stats.get('percentile_95', 0),
                'p99': self.test_stats.get('percentile_99', 0),
                'min': self.test_stats.get('min_response_time', 0),
                'max': self.test_stats.get('max_response_time', 0)
            },
            'error_summary': {
                'total_errors': sum(error['count'] for error in self.error_stats.values()),
                'error_types': len(self.error_stats),
                'error_details': self.error_stats
            },
            'system_stats': self.system_stats
        }
        
    def generate_report(self) -> Dict:
        """生成完整测试报告
        
        Returns:
            Dict: 完整的测试报告数据
        """
        # 获取增量数据
        if self.start_time and self.end_time:
            start_timestamp = self.start_time.timestamp()
            end_timestamp = self.end_time.timestamp()
            incremental_data = self.data_storage.get_data_range(start_timestamp, end_timestamp)
            
            # 处理增量数据
            for data in incremental_data:
                if data['type'] == 'test_stats':
                    self.test_stats.update(data['data'])
                elif data['type'] == 'system_stats':
                    self.system_stats.update(data['data'])
        
        # 生成报告摘要
        summary = self.generate_summary()
        summary.update({
            'detailed_stats': {
                'test_stats': self.test_stats,
                'system_stats': self.system_stats,
                'errors': list(self.error_stats.values())
            }
        })
        
        # 清理存储的数据
        self.data_storage.cleanup()
        
        return {'summary': summary}