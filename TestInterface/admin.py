from django.contrib import admin

# Register your models here.
from .models import TestInterFace

from .models import InterfaceCase
@admin.register(TestInterFace)
class TestInterFaceAdmin(admin.ModelAdmin):
    # 指定在admin后台展示的字段
    list_display = ("id", "project", "name", "url", "method", "type")


@admin.register(InterfaceCase)
class ModelNameAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "interface")
