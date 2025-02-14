# PerfEngine 性能测试引擎

## 目录结构

```
PerfEngine/
├── core/                   # 核心功能模块目录
│   ├── __init__.py
│   ├── datasource.py      # 数据源管理模块
│   ├── engine.py          # 测试引擎主类模块
│   ├── report.py          # 测试报告生成模块
│   ├── stats.py           # 性能数据统计模块
│   ├── strategy.py        # 测试执行策略模块
│   ├── user.py            # 测试用户行为模块
│   └── variable.py        # 变量管理模块
├── consumers.py           # WebSocket消费者模块
├── routing.py             # WebSocket路由配置
└── tasks.py               # Celery异步任务模块
```

## 模块说明

### core 目录

#### engine.py
- 性能测试引擎的核心实现
- 负责管理整个性能测试的生命周期
- 提供测试环境配置、执行控制和数据收集等功能

#### strategy.py
- 提供不同的测试执行策略实现
- 支持并发模式（固定并发用户数）
- 支持阶梯模式（逐步增加并发用户数）
- 支持错误率模式（基于错误率动态调整并发用户数）

#### user.py
- 定义性能测试中的用户行为模式
- 实现请求执行、变量管理、数据验证和错误处理
- 支持业务流程执行和重试机制

#### stats.py
- 性能测试数据收集和统计模块
- 收集请求响应时间、错误率等性能指标
- 提供系统资源使用情况监控

#### report.py
- 测试报告生成和管理模块
- 汇总测试结果和性能指标
- 生成可视化报告

#### datasource.py
- 测试数据源管理模块
- 支持多种数据源类型
- 提供数据读取和解析功能

#### variable.py
- 变量管理和处理模块
- 支持变量提取和替换
- 管理测试过程中的动态数据

### 根目录文件

#### consumers.py
- WebSocket消费者实现
- 提供实时测试数据推送
- 支持与前端的双向通信

#### routing.py
- WebSocket路由配置
- 定义WebSocket连接的URL路由规则

#### tasks.py
- Celery异步任务定义
- 实现性能测试的异步执行
- 支持测试任务的调度和管理