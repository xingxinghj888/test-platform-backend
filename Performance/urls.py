from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PerformanceTestPlanViewSet, PerformanceConfigViewSet, PerformanceReportViewSet

router = DefaultRouter()
router.register(r'plans', PerformanceTestPlanViewSet)
router.register(r'configs', PerformanceConfigViewSet)
router.register(r'reports', PerformanceReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
]