from django.contrib import admin

from Cronjob.models import CronJob


# Register your models here.
@admin.register(CronJob)
class CronJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'create_time', 'name', 'env', 'task', 'status', 'rule')
