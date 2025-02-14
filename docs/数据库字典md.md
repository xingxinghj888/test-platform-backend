# 一、ER关系图



# 二、数据库字典

## 性能测试模块

#### 1、性能测试计划表（performance_test_plan）

| 字段名 | 类型 | 空 | 默认 | 注释 |
|--------|------|-----|------|------|
| id | int | 否 | | 自增长主键ID |
| name | varchar(100) | 否 | | 计划名称 |
| description | text | 是 | NULL | 计划描述 |
| project | ForeignKey | 否 | | 所属项目 |
| creator | ForeignKey | 否 | | 创建人 |
| scenes | ManyToManyField | 是 | | 关联业务流 |
| created_time | datetime | 否 | timezone.now | 创建时间 |
| updated_time | datetime | 否 | auto_now | 更新时间 |
| status | varchar(20) | 否 | pending | 执行状态：pending/running/completed/failed |

#### 2、性能测试配置表（performance_config）

| 字段名 | 类型 | 空 | 默认 | 注释 |
|--------|------|-----|------|------|
| id | int | 否 | | 自增长主键ID |
| plan | ForeignKey | 否 | | 所属计划 |
| control_mode | varchar(20) | 否 | single | 控制模式：single/central/distributed |
| test_mode | varchar(20) | 否 | concurrent | 压测模式：concurrent/step/error_rate/adaptive |
| vus | int | 否 | | 并发用户数 |
| duration | int | 否 | | 持续时间(秒) |
| ramp_up | int | 否 | 0 | 加压时间(秒) |
| step_users | int | 是 | NULL | 阶梯模式每阶梯用户数 |
| step_time | int | 是 | NULL | 阶梯模式每阶梯持续时间 |
| error_threshold | float | 是 | NULL | 错误率模式阈值 |
| adaptive_target | json | 是 | NULL | 自适应模式目标参数 |
| env | ForeignKey | 否 | | 测试环境 |
| protocol | varchar(20) | 否 | http | 协议类型：http/websocket/grpc/tcp/udp |
| data_source_type | varchar(20) | 否 | none | 数据源类型：none/csv/pool/generator/database/api |
| data_config | json | 是 | {} | 数据配置 |
| data_cache_ttl | int | 否 | 3600 | 数据缓存时间(秒) |
| node_count | int | 否 | 1 | 执行节点数 |
| node_distribution | json | 是 | {} | 节点分布配置 |
| load_balance_strategy | varchar(20) | 否 | round_robin | 负载均衡策略：round_robin/weight/dynamic |
| execution_config | json | 否 | {} | 执行配置 |

#### 3、性能指标表（performance_metrics）

| 字段名 | 类型 | 空 | 默认 | 注释 |
|--------|------|-----|------|------|
| id | int | 否 | | 自增长主键ID |
| plan | ForeignKey | 否 | | 所属计划 |
| timestamp | bigint | 否 | | 时间戳 |
| metrics_data | json | 否 | | 性能指标数据 |
| shard_key | varchar(50) | 否 | | 数据分片键 |
| aggregation_period | varchar(20) | 是 | NULL | 聚合周期 |
| created_time | datetime | 否 | auto_now_add | 创建时间 |

#### 4、错误记录表（performance_error）

| 字段名 | 类型 | 空 | 默认 | 注释 |
|--------|------|-----|------|------|
| id | int | 否 | | 自增长主键ID |
| plan | ForeignKey | 否 | | 所属计划 |
| timestamp | bigint | 否 | | 时间戳 |
| error_data | json | 否 | | 错误详情 |
| count | int | 否 | 1 | 出现次数 |
| created_time | datetime | 否 | auto_now_add | 创建时间 |

#### 5、预设配置表（performance_preset）

| 字段名 | 类型 | 空 | 默认 | 注释 |
|--------|------|-----|------|------|
| id | int | 否 | | 自增长主键ID |
| name | varchar(100) | 否 | | 预设名称 |
| description | text | 是 | NULL | 预设描述 |
| project | ForeignKey | 否 | | 所属项目 |
| creator | ForeignKey | 否 | | 创建人 |
| created_time | datetime | 否 | timezone.now | 创建时间 |
| config_type | varchar(20) | 否 | | 配置类型：concurrent/step/error_rate/adaptive |
| config_data | json | 否 | | 配置详细数据 |

#### 6、性能测试报告表（performance_report）

| 字段名 | 类型 | 空 | 默认 | 注释 |
|--------|------|-----|------|------|
| id | int | 否 | | 自增长主键ID |
| plan | ForeignKey | 否 | | 所属计划 |
| summary | json | 否 | | 测试结果汇总 |
| performance_score | float | 是 | NULL | 性能评分 |
| created_time | datetime | 否 | auto_now_add | 创建时间 |

## 功能模块

#### 1、用户表(Users)

| 字段         | 类型      | 空   | 默认 | 注释                      |
| :----------- | :-------- | :--- | ---- | ------------------------- |
| id           | int       | 否   |      | 自增长主键ID              |
| username     | varchar   | 否   |      | 用户名                    |
| email        | varchar   | 否   |      | 邮箱                      |
| password     | varchar   | 否   |      | 密码                      |
| is_active    | int       | 是   | 0    | 用户禁用状态: 0正常 1禁用 |
| created_time | timestamp | 是   |      | 添加时间                  |
| updated_time | timestamp | 是   |      | 修改时间                  |

#### 2、项目表(TestProject)

| 字段        | 类型      | 空   | 默认 | 注释         |
| :---------- | :-------- | :--- | ---- | ------------ |
| id          | int       | 否   |      | 自增长主键ID |
| name        | varchar   | 否   |      | 项目名称     |
| leader      | varchar   | 否   |      | 项目负责人   |
| create_time | timestamp | 是   |      | 添加时间     |

#### 3、测试环境表（TestEnv）

| 字段                  | 类型       | 空   | 默认 | 注释             |
| :-------------------- | :--------- | :--- | ---- | ---------------- |