"""性能测试执行引擎核心模块"""
from typing import Dict, List, Optional
from locust import HttpUser, task, between, events
from locust.runners import MasterRunner
from locust.env import Environment
from locust.stats import stats_printer, stats_history
import time
import json
import psutil
import threading
from datetime import datetime


class PerformanceTestUser(HttpUser):
    """性能测试用户类，定义用户行为和测试场景"""
    wait_time = between(1, 3)  # 每次请求之间的等待时间
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_flows = None  # 支持多业务流
        self.current_flow_index = 0
    
    def on_start(self):
        """测试开始前的初始化操作"""
        if not self.test_flows:
            self.test_flows = []
    
    @task
    def execute_test(self):
        """执行测试场景"""
        if not self.test_flows:
            return
            
        # 轮流执行每个业务流中的请求
        current_flow = self.test_flows[self.current_flow_index]
        self.current_flow_index = (self.current_flow_index + 1) % len(self.test_flows)
        
        # 处理API请求的测试数据
        method = current_flow.get('method', 'GET')
        path = current_flow.get('path', '')
        headers = current_flow.get('headers', {})
        data = current_flow.get('data', {})
        max_retries = current_flow.get('max_retries', 3)  # 最大重试次数
        retry_delay = current_flow.get('retry_delay', 1)  # 重试间隔(秒)
        
        for retry in range(max_retries):
            with self.client.request(
                method=method,
                url=path,
                headers=headers,
                json=data if method in ['POST', 'PUT', 'PATCH'] else None,
                params=data if method == 'GET' else None,
                catch_response=True
            ) as response:
                try:
                    if response.status_code < 400:
                        response.success()
                        break
                    elif retry < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    else:
                        response.failure(f'HTTP {response.status_code} after {max_retries} retries')
                except Exception as e:
                    if retry < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    response.failure(f'{str(e)} after {max_retries} retries')


class PerformanceTestEngine:
    """性能测试执行引擎"""
    
    def __init__(self):
        self.env = None
        self.runner = None
        self.stats_printer = None
        self.test_mode = None  # 'time' or 'rounds'
        self.current_rounds = 0    # 当前执行轮次
        self.max_rounds = 0  # 最大执行轮次
        self.system_stats = {}  # 系统资源使用统计
        self._monitor_thread = None
        self._stop_monitor = False
        self._config_lock = threading.Lock()  # 配置更新锁

    def setup_test(self, host: str, test_flows: List[Dict]):
        """设置测试环境和数据"""
        # 设置测试用户类的测试数据
        PerformanceTestUser.test_flows = test_flows
        
        # 创建测试环境
        self.env = Environment(user_classes=[PerformanceTestUser])
        self.env.host = host
        
        # 创建测试运行器
        self.runner = self.env.create_local_runner()
        
        # 设置统计信息收集
        self.stats_printer = stats_printer(self.env.stats)
        self.env.stats.reset_all()
        
    def _monitor_system_resources(self):
        """监控系统资源使用情况"""
        while not self._stop_monitor:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_io_counters()
            network = psutil.net_io_counters()
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.system_stats[timestamp] = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used': memory.used,
                'memory_total': memory.total,
                'disk_read_bytes': disk.read_bytes,
                'disk_write_bytes': disk.write_bytes,
                'network_bytes_sent': network.bytes_sent,
                'network_bytes_recv': network.bytes_recv
            }
            
            time.sleep(1)
    
    def start_test(self, user_count: int, spawn_rate: int = 1, run_time: Optional[float] = None, rounds: Optional[int] = None):
        """启动性能测试
        
        Args:
            user_count: 并发用户数
            spawn_rate: 用户生成速率(每秒)
            run_time: 测试运行时间(秒)，如果不指定则按轮次运行
            iterations: 测试执行轮次，如果不指定则按时间运行
        """
        if run_time and rounds:
            raise ValueError("不能同时指定运行时间和执行轮次")
            
        if not run_time and not rounds:
            raise ValueError("必须指定运行时间或执行轮次之一")
            
        # 设置测试模式
        self.test_mode = 'time' if run_time else 'rounds'
        self.max_rounds = rounds if rounds else 0
        self.current_rounds = 0
        
        # 启动系统资源监控
        self._stop_monitor = False
        self._monitor_thread = threading.Thread(target=self._monitor_system_resources)
        self._monitor_thread.start()
        
        # 启动测试
        self.runner.start(user_count, spawn_rate=spawn_rate)
        
        # 收集测试数据
        stats_history = {}
        start_time = time.time()
        
        try:
            while True:
                # 检查是否达到结束条件
                if self.test_mode == 'time' and time.time() - start_time > run_time:
                    break
                elif self.test_mode == 'rounds' and self.current_rounds >= self.max_rounds:
                    break
                    
                # 收集当前时刻的测试数据
                current_stats = {
                    'current_rps': self.env.stats.total.current_rps,
                    'response_times': dict(self.env.stats.total.response_times),
                    'num_requests': self.env.stats.total.num_requests,
                    'num_failures': self.env.stats.total.num_failures,
                    'median_response_time': self.env.stats.total.get_current_response_time_percentile(0.5),
                    'avg_response_time': self.env.stats.total.avg_response_time,
                    'min_response_time': self.env.stats.total.min_response_time,
                    'max_response_time': self.env.stats.total.max_response_time
                }
                
                stats_history[str(int(time.time()))] = current_stats
                
                if self.test_mode == 'rounds':
                    self.current_rounds += 1
                    
                time.sleep(1)
                
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_test()
            return {'performance_stats': stats_history, 'system_stats': self.system_stats}
    
    def stop_test(self):
        """停止性能测试"""
        self.runner.stop()
        
        # 停止系统资源监控
        self._stop_monitor = True
        if self._monitor_thread:
            self._monitor_thread.join()
        
        # 生成测试报告数据
        report = {
            'total_requests': self.env.stats.total.num_requests,
            'total_failures': self.env.stats.total.num_failures,
            'average_response_time': self.env.stats.total.avg_response_time,
            'requests_per_second': self.env.stats.total.current_rps,
            'min_response_time': self.env.stats.total.min_response_time,
            'max_response_time': self.env.stats.total.max_response_time,
            'median_response_time': self.env.stats.total.get_current_response_time_percentile(0.5),
            'percentiles': {
                '50%': self.env.stats.total.get_response_time_percentile(0.5),
                '90%': self.env.stats.total.get_response_time_percentile(0.9),
                '95%': self.env.stats.total.get_response_time_percentile(0.95),
                '99%': self.env.stats.total.get_response_time_percentile(0.99)
            },
            'test_mode': self.test_mode,
            'rounds': self.current_rounds if self.test_mode == 'rounds' else None
        }
        
        return report

    def update_test_config(self, user_count: Optional[int] = None, spawn_rate: Optional[int] = None):
        """动态更新测试配置
        
        Args:
            user_count: 新的并发用户数
            spawn_rate: 新的用户生成速率
        """
        with self._config_lock:
            if user_count is not None:
                self.runner.target_user_count = user_count
                
            if spawn_rate is not None:
                self.runner.spawn_rate = spawn_rate
                
            # 根据新配置调整用户数
            if user_count is not None:
                current_count = self.runner.user_count
                if user_count > current_count:
                    self.runner.start(user_count - current_count, spawn_rate=spawn_rate or 1)
                elif user_count < current_count:
                    self.runner.stop(current_count - user_count, spawn_rate=spawn_rate or 1)