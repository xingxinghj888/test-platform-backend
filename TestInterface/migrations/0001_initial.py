# Generated by Django 4.2 on 2024-10-14 05:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Testproject', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestInterFace',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='接口名称', max_length=50, verbose_name='接口名称')),
                ('url', models.CharField(help_text='接口地址', max_length=200, verbose_name='接口地址')),
                ('method', models.CharField(help_text='请求方法', max_length=10, verbose_name='请求方法')),
                ('type', models.CharField(choices=[('2', '第三方接口'), ('1', '项目接口')], default='1', help_text='接口类型', max_length=10, verbose_name='接口类型')),
                ('project', models.ForeignKey(help_text='所属项目id', max_length=50, on_delete=django.db.models.deletion.CASCADE, to='Testproject.testproject', verbose_name='所属项目id')),
            ],
            options={
                'verbose_name': '接口管理表',
                'verbose_name_plural': '接口管理表',
                'db_table': 'interface',
            },
        ),
        migrations.CreateModel(
            name='InterfaceCase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='接口用例名称', max_length=50, verbose_name='接口用例名称')),
                ('headers', models.JSONField(blank=True, default=dict, help_text='请求头配置', null=True, verbose_name='请求头配置')),
                ('request', models.JSONField(blank=True, default=dict, help_text='请求参数', null=True, verbose_name='请求参数')),
                ('file', models.JSONField(blank=True, default=list, help_text='请求上传的文件参数', null=True, verbose_name='请求上传的文件参数')),
                ('setup_script', models.TextField(blank=True, default='', help_text='前置脚本', null=True, verbose_name='前置脚本')),
                ('teardown_script', models.TextField(blank=True, default='', help_text='后置脚本', null=True, verbose_name='后置脚本')),
                ('interface', models.ForeignKey(help_text='所属接口', max_length=50, on_delete=django.db.models.deletion.CASCADE, to='TestInterface.testinterface', verbose_name='所属接口')),
            ],
            options={
                'verbose_name': '接口用例管理表',
                'verbose_name_plural': '接口用例管理表',
                'db_table': 'interface_case',
            },
        ),
    ]
