import json
from channels.generic.websocket import AsyncWebsocketConsumer

class PerformanceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 获取性能测试任务ID
        self.task_id = self.scope['url_route']['kwargs']['task_id']
        self.room_group_name = f'performance_test_{self.task_id}'

        # 将channel加入到组中
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # 从组中移除channel
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # 处理从客户端接收到的消息
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # 将消息广播到组中的所有channel
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'performance_message',
                'message': message
            }
        )

    async def performance_message(self, event):
        message = event['message']

        # 发送消息到WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def performance_update(self, event):
        # 发送性能测试数据更新
        await self.send(text_data=json.dumps({
            'type': 'performance_update',
            'data': event['data']
        }))

    async def error_update(self, event):
        # 发送错误统计更新
        await self.send(text_data=json.dumps({
            'type': 'error_update',
            'data': event['data']
        }))

    async def resource_update(self, event):
        # 发送系统资源监控数据更新
        await self.send(text_data=json.dumps({
            'type': 'resource_update',
            'data': event['data']
        }))