"""性能测试WebSocket路由配置模块

配置WebSocket路由，将不同的URL模式映射到对应的消费者。
"""

from django.urls import re_path
from .consumers import PerformanceTestConsumer

websocket_urlpatterns = [
    re_path(r'ws/perf_test/(?P<plan_id>\d+)/$', PerformanceTestConsumer.as_asgi()),
]