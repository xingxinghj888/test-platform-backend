"""
URL configuration for apiTestPlatform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import static
from django.contrib import admin
from django.urls import path, re_path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from rest_framework import routers

from BugManage.views import BugManageView
from Cronjob.views import CronJobView
from Performance.views import PerformanceTestPlanViewSet, PerformanceConfigViewSet
from TestTask.views import TestTaskView, TestRecordView, TestReportView
from apiTestPlatform import settings
from users.views import LoginView, RefreshView
from TestInterface.views import TestInterFaceView, InterFaceCaseView
from Testproject.views import TestProjectView, TestEnvView, TestFileView
from Scenes.views import TestScenesView, SceneToCaseView, UpdateSceneCaseOrder

# 1.先导入drf的路由模块和自定义的视图集
# 创建一个简单的路由对象
router = routers.SimpleRouter()

urlpatterns = [
    path('admin/', admin.site.urls),
    # 复制到路由匹配路径中

#     # 生产环境配置静态文件服务的URL模式
# re_path(r'static/(?P<path>.*)$', static.serve(),
#         {'document_root': settings.STATIC_ROOT}, name='static'),

    # 登录接口的访问路径，使用的视图函数是drf自带的视图类
    # path('api/users/login/', TokenObtainPairView.as_view(), name='login'),
    # 修改为访问我们自定义的视图类
    path('api/users/login/', LoginView.as_view(), name='login'),
    # 刷新token
    path('api/users/token/refresh/', RefreshView.as_view(), name='token_refresh'),
    # 校验token是否有效
    path('api/users/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    # 修改测试流程中的用例步骤顺序
    path('api/testFlow/icases/order/', UpdateSceneCaseOrder.as_view(), name='update_order'),
    # 运行单条测试用例
    path('api/TestInterFace/cases/run/', InterFaceCaseView.as_view({
        # 这里配置的是执行业务流的处理函数，写错拉，要改
        "post": "run_cases"
    }), name='run_cases'),
    # 运行测试业务流的路由
    path('api/testFlow/scenes/run/', TestScenesView.as_view({
        "post": "run_scene"
    }), name='run_scene'),
    # 运行测试任务
    path('api/testTask/tasks/run/', TestTaskView.as_view({
        "post": "run_task"
    }), name='run_task'),
    ]

# 注册性能测试相关路由
router.register('api/v1/performance/plans', PerformanceTestPlanViewSet)
router.register('api/v1/performance/configs', PerformanceConfigViewSet)
# 注册项目管理的路由
router.register('api/testPro/projects', TestProjectView)
# 注册测试环境管理的路由
router.register('api/testPro/envs', TestEnvView)
# 注册测试文件管理的路由
router.register('api/testPro/files', TestFileView)
# 接口管理的路由
router.register('api/TestInterFace/interfaces', TestInterFaceView)
# 注册接口用例管理的路由
router.register('api/TestInterFace/cases', InterFaceCaseView)
# 注册业务流管理的路由
router.register('api/testFlow/scenes', TestScenesView)
# 注册业务流中用例执行步骤的路由
router.register('api/testFlow/icases', SceneToCaseView)
# 注册测试任务管理的路由
router.register('api/testTask/tasks', TestTaskView)
# 注册测试运行记录的路由
router.register('api/testTask/records', TestRecordView)
# 注册测试报告的路由
router.register('api/testTask/report', TestReportView)
# 注册定时任务的路由
router.register('api/crontab/cronjob', CronJobView)
# bug管理路由
router.register('api/bug/bugs', BugManageView)

"""
该函数将router.urls中的路由模式添加到urlpatterns中，用于构建Django项目的路由配置。urlpatterns是一个列表，
其中每个元素都是一个指向特定视图函数的路由模式。通过将router.urls添加到urlpatterns中，可以动态地为项目添加更多的路由模式，
而无需手动编写每个模式。这在大型项目中非常有用，因为它们通常具有许多不同的视图函数和相应的路由模式。通过使用router.urls，
可以更轻松地管理这些模式，并且可以更轻松地扩展项目以添加更多功能。
"""
urlpatterns += router.urls
