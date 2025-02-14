"""性能测试WebSocket消费者模块

提供性能测试数据的实时推送功能，包括：
- 测试进度推送
- 性能指标推送
- 错误信息推送
"""

from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async
from Performance.models import PerformanceTestPlan
from .core import PerformanceTestEngine

class PerformanceTestConsumer(AsyncWebsocketConsumer):
    """性能测试数据推送消费者
    
    负责将性能测试的实时数据推送给前端，包括：
    - 测试执行状态
    - 性能指标数据
    - 错误信息
    """
    
    async def connect(self):
        """建立WebSocket连接"""
        # 获取测试计划ID
        self.plan_id = self.scope['url_route']['kwargs']['plan_id']
        self.room_group_name = f'perf_test_{self.plan_id}'
        
        # 加入房间组
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
    async def disconnect(self, close_code):
        """断开WebSocket连接"""
        # 离开房间组
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
    async def receive(self, text_data):
        """接收前端消息"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'get_stats':
                # 获取性能测试数据
                stats = await self._get_test_stats()
                await self.send(text_data=json.dumps({
                    'type': 'test_stats',
                    'data': stats
                }))
            elif message_type == 'stop_test':
                # 停止性能测试
                await self._stop_test()
                await self.send(text_data=json.dumps({
                    'type': 'test_stopped',
                    'data': {'success': True}
                }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'data': {'message': str(e)}
            }))
            
    async def test_stats(self, event):
        """推送测试数据"""
        await self.send(text_data=json.dumps({
            'type': 'test_stats',
            'data': event['data']
        }))
        
    async def test_error(self, event):
        """推送错误信息"""
        await self.send(text_data=json.dumps({
            'type': 'test_error',
            'data': event['data']
        }))
        
    @sync_to_async
    def _get_test_stats(self):
        """获取测试统计数据"""
        try:
            plan = PerformanceTestPlan.objects.get(id=self.plan_id)
            engine = PerformanceTestEngine()
            
            # 获取测试数据
            test_stats = engine.get_test_stats()
            system_stats = engine.get_system_stats()
            
            return {
                'test_stats': test_stats,
                'system_stats': system_stats,
                'status': plan.status
            }
        except Exception as e:
            return {
                'error': str(e)
            }
            
    @sync_to_async
    def _stop_test(self):
        """停止性能测试"""
        try:
            plan = PerformanceTestPlan.objects.get(id=self.plan_id)
            engine = PerformanceTestEngine()
            engine.stop_test()
            
            # 更新测试计划状态
            plan.status = 'stopped'
            plan.save()
            
            return True
        except Exception as e:
            return False