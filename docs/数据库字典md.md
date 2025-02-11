# 一、ER关系图

![ER关系图2.0](D:\课件\py测开VIP课件\MD课件\ER关系图2.0.png)



# 二、数据库字典

## 性能测试模块

#### 1、压测计划表（pt_plan）

| 字段名 | 类型 | 空 | 默认 | 注释 |
|--------|------|-----|------|------|
| id | int | 否 | | 自增长主键ID |
| name | varchar | 否 | | 计划名称 |
| description | text | 是 | NULL | 计划描述 |
| project | ForeignKey | 否 | | 所属项目 |
| create_time | datetime | 是 | CURRENT_TIMESTAMP | 创建时间 |
| update_time | datetime | 是 | CURRENT_TIMESTAMP | 更新时间 |

#### 2、压测配置表（pt_config）

| 字段名 | 类型 | 空 | 默认 | 注释 |
|--------|------|-----|------|------|
| id | int | 否 | | 自增长主键ID |
| plan | ForeignKey | 否 | | 关联的压测计划 |
| control_mode | varchar | 否 | | 控制模式：single/central |
| test_mode | varchar | 否 | | 压测模式：concurrent/step/error_rate |
| duration | int | 是 | NULL | 持续时长(秒) |
| rounds | int | 是 | NULL | 轮次 |
| concurrent_users | int | 是 | NULL | 并发用户数 |
| step_users | int | 是 | NULL | 阶梯模式每阶梯用户数 |
| step_time | int | 是 | NULL | 阶梯模式每阶梯持续时间 |
| error_threshold | float | 是 | NULL | 错误率模式阈值 |
| create_time | datetime | 是 | CURRENT_TIMESTAMP | 创建时间 |
| update_time | datetime | 是 | CURRENT_TIMESTAMP | 更新时间 |

#### 3、压测场景关联表（pt_scene_rel）

| 字段名 | 类型 | 空 | 默认 | 注释 |
|--------|------|-----|------|------|
| id | int | 否 | | 自增长主键ID |
| plan | ForeignKey | 否 | | 压测计划 |
| scene | ForeignKey | 否 | | 业务流 |
| create_time | datetime | 是 | CURRENT_TIMESTAMP | 创建时间 |

#### 4、预设配置表（pt_preset_config）

| 字段名 | 类型 | 空 | 默认 | 注释 |
|--------|------|-----|------|------|
| id | int | 否 | | 自增长主键ID |
| name | varchar | 否 | | 配置名称 |
| description | text | 是 | NULL | 配置描述 |
| config_type | varchar | 否 | | 配置类型：concurrent/step/error_rate |
| config_data | json | 否 | | 配置详细数据 |
| project | ForeignKey | 否 | | 所属项目 |
| create_time | datetime | 是 | CURRENT_TIMESTAMP | 创建时间 |
| update_time | datetime | 是 | CURRENT_TIMESTAMP | 更新时间 |

#### 5、压测报告表（pt_report）

| 字段名 | 类型 | 空 | 默认 | 注释 |
|--------|------|-----|------|------|
| id | int | 否 | | 自增长主键ID |
| plan | ForeignKey | 否 | | 压测计划 |
| start_time | datetime | 是 | NULL | 开始时间 |
| end_time | datetime | 是 | NULL | 结束时间 |
| status | varchar | 是 | NULL | 执行状态 |
| summary | json | 是 | NULL | 汇总数据 |
| details | json | 是 | NULL | 详细数据 |
| create_time | datetime | 是 | CURRENT_TIMESTAMP | 创建时间 |

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
| id                    | int        | 否   |      | 自增长主键ID     |
| project               | ForeignKey | 否   |      | 关联项目         |
| global_variable       | json       | 是   | {}   | 全局变量         |
| debug_global_variable | json       | 是   | {}   | 调试模式全局变量 |
| db                    | json       | 是   | {}   | 数据库配置       |
| host                  | varchar    | 是   |      | 测试环境host地址 |
| headers               | json       | 是   | {}   | 全局请求头配置   |
| global_func           | textField  | 是   |      | 全局工具函数文件 |
| name                  | varchar    | 否   |      | 测试环境名称     |

#### 4、测试文件管理表(TestFile)

| 字段 | 类型 | 空   | 默认 | 注释               |
| ---- | ---- | ---- | ---- | ------------------ |
| id   | int  | 否   |      | 自增长主键ID       |
| file | file | 否   |      | 文件               |
| info | json | 是   | []   | 文件保存的数据信息 |



#### 5、项目接口表(Interfae)

| 字段    | 类型       | 空   | 默认 | 注释                           |
| :------ | :--------- | :--- | ---- | ------------------------------ |
| id      | int        | 否   |      | 自增长主键ID                   |
| project | ForeignKey | 否   |      | 关联项目                       |
| name    | varchar    | 否   |      | 接口名称                       |
| url     | varchar    | 否   |      | 接口地址                       |
| method  | varchar    | 否   |      | 请求方法                       |
| type    | varchar    | 否   | 1    | 接口类型(项目接口、第三方接口) |

#### 6、接口用例表（InterCase）

| 字段            | 类型       | 空   | 默认 | 注释               |
| :-------------- | :--------- | :--- | ---- | ------------------ |
| id              | int        | 否   |      | 自增长主键ID       |
| title           | varchar    | 否   |      | 用例名称           |
| interface       | ForeignKey | 否   |      | 所属接口           |
| headers         | json       | 是   | {}   | 请求头配置         |
| request         | json       | 是   | {}   | 请求参数           |
| file            | json       | 是   | []   | 请求上传文件的参数 |
| setup_script    | TextField  | 是   |      | 前置脚本           |
| teardown_script | TextField  | 是   |      | 后置断言脚本       |

#### 7、业务流测试表（TestScene）

| 字段    | 类型       | 空   | 默认 | 注释         |
| :------ | :--------- | :--- | ---- | ------------ |
| id      | int        | 否   |      | 自增长主键ID |
| project | ForeignKey | 否   |      | 关联项目     |
| name    | varchar    | 否   |      | 业务流名称   |

#### 8、业务流和接口用例的中间表(SceneToCase)

| 字段  | 类型       | 空   | 默认 | 注释                   |
| :---- | :--------- | :--- | ---- | ---------------------- |
| id    | int        | 否   |      | 自增长主键ID           |
| icase | ForeignKey | 否   |      | 接口用例               |
| scene | ForeignKey | 否   |      | 业务流                 |
| sort  | int        | 是   |      | 业务流中的用例执行顺序 |

#### 9、测试任务表(TestTask)

| 字段    | 类型            | 空   | 默认 | 注释           |
| :------ | :-------------- | :--- | ---- | -------------- |
| id      | int             | 否   |      | 自增长主键ID   |
| project | ForeignKey      | 否   |      | 所属项目       |
| name    | String          | 否   |      | 任务名称       |
| scene   | ManyToManyField | 是   |      | 包含的测试业务 |

#### 10、运行记录表(TestRecord)

| 字段        | 类型       | 空   | 默认 | 注释           |
| :---------- | :--------- | :--- | ---- | -------------- |
| id          | int        | 否   |      | 自增长主键ID   |
| task        | ForeignKey | 否   |      | 执行的测试任务 |
| all         | int        | 是   | 0    | 用例总数       |
| success     | int        | 是   | 0    | 成功用例数     |
| fail        | int        | 是   | 0    | 失败用例数     |
| error       | int        | 是   | 0    | 错误用例数     |
| pass_rate   | varchar    | 是   | '0'  | 通过率         |
| tester      | varchar    | 是   |      | 执行者         |
| env         | ForeignKey | 否   |      | 测试环境       |
| statue      | varchar    | 否   |      | 执行状态       |
| create_time | DataTime   | 否   |      | 执行时间       |

#### 11、测试报告(TestReport)

| 字段   | 类型          | 空   | 默认 | 注释         |
| :----- | :------------ | :--- | ---- | ------------ |
| id     | int           | 否   |      | 自增长主键ID |
| info   | JSONField     | 是   |      | 报告数据     |
| record | OneToOneField | 是   |      | 测试记录     |

#### 12、定时任务表(CronJob)

| 字段        | 类型       | 空   | 默认      | 注释             |
| :---------- | :--------- | :--- | --------- | ---------------- |
| id          | int        | 否   |           | 自增长主键ID     |
| project     | ForeignKey | 否   |           | 所属项目         |
| create_time | DataTime   | 否   |           | 创建时间         |
| name        | varchar    | 否   |           | 定时任务名称     |
| rule        | varchar    | 否   | * * * * * | 定时执行规则     |
| status      | Boolean    | 否   | flase     | 是否启用         |
| env         | ForeignKey | 否   |           | 执行使用测试环境 |
| task        | ForeignKey | 否   |           | 执行的测试任务   |

#### 13、bug表（Bug）

| 字段        | 类型       | 空   | 默认 | 注释         |
| :---------- | :--------- | :--- | ---- | ------------ |
| id          | int        | 否   |      | 自增长主键ID |
| interface   | ForeignKey | 否   |      | 接口         |
| create_time | datatime   | 否   |      | 提交时间     |
| desc        | varchar    | 是   |      | bug描述      |
| info        | Json       | 是   |      | bug详细信息  |
| status      | varchar    | 否   |      | bug状态      |
| user        | varchar    | 是   |      | 提交者       |

#### 14、bug处理记录表(BugHandle)

| 字段        | 类型       | 空   | 默认 | 注释         |
| :---------- | :--------- | :--- | ---- | ------------ |
| id          | int        | 否   |      | 自增长主键ID |
| bug         | ForeignKey | 否   |      | bug          |
| create_time | datatime   | 否   |      | 提交时间     |
| handle      | TextField  | 是   |      | 处理操作     |
| update_user | varchar    | 是   |      | 处理用户     |