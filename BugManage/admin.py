from django.contrib import admin
from .models import BugManage, BugHandle


# Register your models here.
@admin.register(BugManage)
class ModelNameAdmin(admin.ModelAdmin):
    list_display = ['create_time', 'interface', 'desc', 'status', 'user']


@admin.register(BugHandle)
class ModelNameAdmin(admin.ModelAdmin):
    list_display = ['bug', 'create_time', 'handle', 'update_user']
