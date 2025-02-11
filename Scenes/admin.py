from django.contrib import admin

# Register your models here.
from .models import TestScenes, SceneToCase


@admin.register(TestScenes)
class ModelNameAdmin(admin.ModelAdmin):
    list_display = ("id", "project", "name")


@admin.register(SceneToCase)
class ModelNameAdmin(admin.ModelAdmin):
    list_display = ["id", "icase", "scene", "sort"]
