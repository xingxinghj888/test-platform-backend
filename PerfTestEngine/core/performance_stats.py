import time
import statistics
from collections import defaultdict
from typing import Dict, List, Optional, Union

class PerformanceStatsCollector:
    """性能测试数据收集器
    用于收集和统计性能测试过程中的各项指标，包括响应时间、错误率、系统资源使用等。
    支持数据分片存储和聚合分析。
    """
    def __init__(self, shard_key: str = 'default', aggregation_period: str = '1s'):
        self.start_time = time.time()
        self.total_requests = 0
        self.failed_requests = 0
        self.response_times: List[float] = []
        self.errors: Dict[str, Dict] = defaultdict(lambda: {'count': 0, 'data': []})
        self.current_users = 0
        self.rps_data: List[float] = []
        self.cpu_usage: List[float] = []
        self.memory_usage: List[float] = []
        self.network_io: List[float] = []
        self._last_request_time = time.time()
        self._request_count_window: List[float] = []
        self._window_size = 10  # 10秒滑动窗口
        self.shard_key = shard_key
        self.aggregation_period = aggregation_period

    def record_request(self, response_time: float, is_success: bool,
                      error_type: Optional[str] = None, error_data: Optional[Dict] = None) -> None:
        """记录请求数据
        Args:
            response_time: 响应时间（毫秒）
            is_success: 是否成功
            error_type: 错误类型（如果失败）
            error_data: 错误详细信息（如果失败）
        """
        self.total_requests += 1
        current_time = time.time()
        
        # 更新RPS计算窗口
        self._request_count_window.append(current_time)
        while self._request_count_window and \
              current_time - self._request_count_window[0] > self._window_size:
            self._request_count_window.pop(0)
        
        if is_success:
            self.response_times.append(response_time)
        else:
            self.failed_requests += 1
            if error_type:
                self.errors[error_type]['count'] += 1
                if error_data:
                    self.errors[error_type]['data'].append(error_data)

    def update_concurrent_users(self, count: int) -> None:
        """更新当前并发用户数"""
        self.current_users = count

    def record_system_metrics(self, cpu: float, memory: float) -> None:
        """记录系统资源使用情况
        Args:
            cpu: CPU使用率（百分比）
            memory: 内存使用率（百分比）
        """
        self.cpu_usage.append(cpu)
        self.memory_usage.append(memory)

    def get_current_rps(self) -> float:
        """获取当前每秒请求数（RPS）"""
        if not self._request_count_window:
            return 0.0
        window_duration = time.time() - self._request_count_window[0]
        if window_duration <= 0:
            return 0.0
        return len(self._request_count_window) / min(window_duration, self._window_size)

    def get_statistics(self) -> Dict[str, Union[float, int, Dict]]:
        """获取性能测试统计数据"""
        stats = {
            "total_requests": self.total_requests,
            "failed_requests": self.failed_requests,
            "current_users": self.current_users,
            "current_rps": self.get_current_rps(),
            "error_types": dict(self.errors),
            "duration": time.time() - self.start_time
        }

        # 响应时间统计
        if self.response_times:
            stats["response_time"] = {
                "min": min(self.response_times),
                "max": max(self.response_times),
                "avg": statistics.mean(self.response_times),
                "median": statistics.median(self.response_times),
                "p95": statistics.quantiles(self.response_times, n=20)[18],  # 95th percentile
                "p99": statistics.quantiles(self.response_times, n=100)[98]  # 99th percentile
            }

        # 系统资源使用统计
        if self.cpu_usage:
            stats["system_metrics"] = {
                "cpu": {
                    "current": self.cpu_usage[-1],
                    "avg": statistics.mean(self.cpu_usage)
                },
                "memory": {
                    "current": self.memory_usage[-1],
                    "avg": statistics.mean(self.memory_usage)
                }
            }

        return stats

    def reset(self) -> None:
        """重置所有统计数据"""
        self.__init__()