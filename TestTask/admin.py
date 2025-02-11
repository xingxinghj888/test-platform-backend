from django.contrib import admin

from .models import TestTask, TestRecord, TestReport


@admin.register(TestTask)
class TestTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'project', 'name', ]


@admin.register(TestRecord)
class ModelNameAdmin(admin.ModelAdmin):
    list_display = ['id', 'task', 'env', 'pass_rate', 'all']


@admin.register(TestReport)
class ModelNameAdmin(admin.ModelAdmin):
    list_display = ['id', 'record']
