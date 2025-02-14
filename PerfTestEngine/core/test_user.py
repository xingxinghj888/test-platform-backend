"""性能测试用户模块

提供性能测试中的用户行为模式实现，包括：
- 请求发送
- 数据处理
- 变量管理
- 断言验证
"""

from typing import Dict, List, Any, Optional
from locust import User, task, between
import requests
import json
from jsonpath import jsonpath
import re
from .test_variable import VariableManager

class PerformanceTestUser(User):
    """性能测试用户类
    
    实现性能测试中的用户行为，包括：
    - 执行测试流程
    - 发送HTTP请求
    - 处理响应数据
    - 管理变量
    - 执行断言
    """
    
    abstract = True
    test_flows: List[Dict] = []
    global_variables: Dict[str, Any] = {}
    
    def __init__(self, *args, **kwargs):
        """初始化测试用户"""
        super().__init__(*args, **kwargs)
        self.variable_manager = VariableManager()
        self.session = requests.Session()
        
        # 初始化环境变量
        for name, value in self.global_variables.items():
            self.variable_manager.set_env_variable(name, value)
    
    @task
    def execute_test_flows(self):
        """执行测试流程"""
        for flow in self.test_flows:
            try:
                self._execute_flow(flow)
            except Exception as e:
                self.environment.events.request_failure.fire(
                    request_type=flow.get('name', 'unknown'),
                    name=str(e),
                    response_time=0,
                    exception=e
                )
            finally:
                # 清理临时变量
                self.variable_manager.clear_temp_variables()
    
    def _execute_flow(self, flow: Dict):
        """执行单个测试流程
        
        Args:
            flow: 测试流程配置
        """
        # 执行前置脚本
        if 'setup_script' in flow:
            self._execute_script(flow['setup_script'])
            
        # 发送请求
        response = self._send_request(flow)
        
        # 执行后置脚本
        if 'teardown_script' in flow:
            self._execute_script(flow['teardown_script'], response)
    
    def _send_request(self, flow: Dict) -> requests.Response:
        """发送HTTP请求
        
        Args:
            flow: 测试流程配置
            
        Returns:
            requests.Response: 请求响应对象
        """
        request_data = self._prepare_request_data(flow)
        start_time = self.environment.runner.time()
        
        try:
            response = self.session.request(**request_data)
            self.environment.events.request_success.fire(
                request_type=request_data['method'],
                name=flow.get('name', request_data['url']),
                response_time=int((self.environment.runner.time() - start_time) * 1000),
                response_length=len(response.content)
            )
            return response
        except Exception as e:
            self.environment.events.request_failure.fire(
                request_type=request_data['method'],
                name=flow.get('name', request_data['url']),
                response_time=int((self.environment.runner.time() - start_time) * 1000),
                exception=e
            )
            raise
    
    def _prepare_request_data(self, flow: Dict) -> Dict:
        """准备请求数据
        
        Args:
            flow: 测试流程配置
            
        Returns:
            Dict: 请求参数字典
        """
        # 解析变量引用
        interface = self.variable_manager.parse_variable_references(flow.get('interface', {}))
        headers = self.variable_manager.parse_variable_references(flow.get('headers', {}))
        request = self.variable_manager.parse_variable_references(flow.get('request', {}))
        
        # 组装请求数据
        request_data = {
            'url': interface.get('url'),
            'method': interface.get('method'),
            'headers': headers
        }
        request_data.update(request)
        
        # 处理URL
        if not request_data['url'].startswith(('http://', 'https://')):
            request_data['url'] = self.host + request_data['url']
            
        return request_data
    
    def _execute_script(self, script: str, response: Optional[requests.Response] = None):
        """执行脚本
        
        Args:
            script: 脚本内容
            response: 可选，请求响应对象
        """
        # 定义脚本中可用的工具函数
        def set_env_var(name: str, value: Any):
            self.variable_manager.set_env_variable(name, value)
            
        def set_temp_var(name: str, value: Any):
            self.variable_manager.set_temp_variable(name, value)
            
        def get_var(name: str) -> Any:
            return self.variable_manager.get_variable(name)
            
        def extract_by_jsonpath(obj: Any, path: str) -> Any:
            result = jsonpath(obj, path)
            return result[0] if result else None
            
        def extract_by_regex(text: str, pattern: str) -> Optional[str]:
            match = re.search(pattern, text)
            return match.group(1) if match else None
            
        # 执行脚本
        try:
            exec(script, {
                'response': response,
                'set_env_var': set_env_var,
                'set_temp_var': set_temp_var,
                'get_var': get_var,
                'extract_by_jsonpath': extract_by_jsonpath,
                'extract_by_regex': extract_by_regex
            })
        except Exception as e:
            raise RuntimeError(f'脚本执行错误: {str(e)}')