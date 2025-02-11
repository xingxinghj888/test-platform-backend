from django.contrib import admin

# Register your models here.
from .models import TestProject, TestEnv, TestFile


@admin.register(TestProject)
class TestProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "leader")


@admin.register(TestEnv)
class TestEnvAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "project", "host")


@admin.register(TestFile)
class TestFileAdmin(admin.ModelAdmin):
    list_display = ("id", "file", "info")
