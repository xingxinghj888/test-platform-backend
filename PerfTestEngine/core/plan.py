"""性能测试计划处理模块

提供测试计划的数据处理和管理功能，包括：
- 测试计划解析
- 测试流程管理
- 变量处理
- 数据验证
"""

from typing import Dict, List, Optional
from collections import OrderedDict

class TestPlan:
    """测试计划类
    
    负责解析和管理测试计划数据，包括：
    - 测试流程配置
    - 变量配置
    - 验证规则配置
    """
    
    def __init__(self, plan_data: Dict):
        """初始化测试计划
        
        Args:
            plan_data: 测试计划配置数据
        """
        self.name = plan_data.get('name', 'Default Plan')
        self.description = plan_data.get('description', '')
        self.variables = plan_data.get('variables', {})
        self.flows = self._parse_flows(plan_data.get('flows', []))
        
    def _parse_flows(self, flows_data: List[Dict]) -> List[Dict]:
        """解析测试流程配置
        
        Args:
            flows_data: 原始流程配置数据
            
        Returns:
            解析后的流程配置列表
        """
        parsed_flows = []
        for flow in flows_data:
            parsed_flow = {
                'name': flow.get('name', ''),
                'weight': flow.get('weight', 1),
                'think_time': flow.get('think_time', 0),
                'setup_script': flow.get('setup_script', ''),
                'teardown_script': flow.get('teardown_script', ''),
                'requests': self._parse_requests(flow.get('requests', [])),
                'variables': flow.get('variables', {})
            }
            parsed_flows.append(parsed_flow)
        return parsed_flows
    
    def _parse_requests(self, requests_data: List[Dict]) -> List[Dict]:
        """解析请求配置
        
        支持两种数据格式：
        1. 性能测试原生格式
        2. 接口用例格式
        
        Args:
            requests_data: 原始请求配置数据
            
        Returns:
            解析后的请求配置列表
        """
        parsed_requests = []
        for req in requests_data:
            # 判断是否为接口用例格式
            if 'interface' in req:
                interface = req['interface']
                parsed_req = {
                    'name': req.get('title', ''),
                    'url': interface.get('url', ''),
                    'method': interface.get('method', 'GET'),
                    'headers': req.get('headers', {}),
                    'request': req.get('request', {}),
                    'files': req.get('file', {}),
                    'timeout': req.get('timeout', 30),
                    'allow_redirects': req.get('allow_redirects', True),
                    'verify': req.get('verify', True),
                    'setup_script': req.get('setup_script', ''),
                    'teardown_script': req.get('teardown_script', ''),
                    'extract': req.get('extract', {}),
                    'validate': req.get('validate', [])
                }
            else:
                # 原生性能测试格式
                parsed_req = {
                    'name': req.get('name', ''),
                    'url': req.get('url', ''),
                    'method': req.get('method', 'GET'),
                    'headers': req.get('headers', {}),
                    'params': req.get('params', {}),
                    'data': req.get('data', {}),
                    'json': req.get('json', {}),
                    'files': req.get('files', {}),
                    'timeout': req.get('timeout', 30),
                    'allow_redirects': req.get('allow_redirects', True),
                    'verify': req.get('verify', True),
                    'setup_script': req.get('setup_script', ''),
                    'teardown_script': req.get('teardown_script', ''),
                    'extract': req.get('extract', {}),
                    'validate': req.get('validate', [])
                }
            parsed_requests.append(parsed_req)
        return parsed_requests
    
    def get_flow_by_name(self, name: str) -> Optional[Dict]:
        """根据名称获取流程配置
        
        Args:
            name: 流程名称
            
        Returns:
            流程配置字典，未找到返回None
        """
        for flow in self.flows:
            if flow['name'] == name:
                return flow
        return None
    
    def get_all_variables(self) -> Dict:
        """获取所有变量配置
        
        Returns:
            包含全局变量和所有流程变量的字典
        """
        all_vars = self.variables.copy()
        for flow in self.flows:
            all_vars.update(flow.get('variables', {}))
        return all_vars