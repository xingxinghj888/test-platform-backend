from django.contrib import admin
from .models import PerformanceTestPlan, PerformanceConfig, PerformancePreset, PerformanceReport

@admin.register(PerformanceTestPlan)
class PerformanceTestPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'creator', 'created_time', 'status']
    list_filter = ['status', 'created_time']
    search_fields = ['name', 'description']

@admin.register(PerformanceConfig)
class PerformanceConfigAdmin(admin.ModelAdmin):
    list_display = ['plan', 'vus', 'duration', 'host', 'endpoint']
    list_filter = ['request_method']
    search_fields = ['host', 'endpoint']

@admin.register(PerformancePreset)
class PerformancePresetAdmin(admin.ModelAdmin):
    list_display = ['name', 'creator', 'created_time']
    list_filter = ['created_time']
    search_fields = ['name', 'description']

@admin.register(PerformanceReport)
class PerformanceReportAdmin(admin.ModelAdmin):
    list_display = ['plan', 'start_time', 'end_time']
    list_filter = ['start_time']
    search_fields = ['plan__name']