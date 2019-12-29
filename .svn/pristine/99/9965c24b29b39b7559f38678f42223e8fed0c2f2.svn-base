# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SysOrg',
            fields=[
                ('id', models.CharField(max_length=255, unique=True, serialize=False, primary_key=True)),
                ('parent_id', models.CharField(max_length=64)),
                ('parent_ids', models.CharField(max_length=200)),
                ('org_name', models.CharField(max_length=100)),
                ('org_label', models.CharField(max_length=100)),
                ('org_type', models.CharField(max_length=100, null=True, blank=True)),
                ('org_grade', models.CharField(max_length=100, null=True, blank=True)),
                ('province', models.CharField(max_length=10, null=True, blank=True)),
                ('city', models.CharField(max_length=10, null=True, blank=True)),
                ('district', models.CharField(max_length=10, null=True, blank=True)),
                ('address', models.CharField(max_length=100, null=True, blank=True)),
                ('zipcode', models.CharField(max_length=6, null=True, blank=True)),
                ('master', models.CharField(max_length=20, null=True, blank=True)),
                ('contact', models.CharField(max_length=20, null=True, blank=True)),
                ('contact_mobile', models.CharField(max_length=100, null=True, blank=True)),
                ('tel', models.CharField(max_length=100, null=True, blank=True)),
                ('fax', models.CharField(max_length=100, null=True, blank=True)),
                ('mail', models.CharField(max_length=100, null=True, blank=True)),
                ('weixin', models.CharField(max_length=100, null=True, blank=True)),
                ('create_by', models.CharField(max_length=100, null=True, blank=True)),
                ('create_date', models.DateTimeField(null=True, blank=True)),
                ('update_by', models.CharField(max_length=100, null=True, blank=True)),
                ('update_date', models.DateTimeField(null=True, blank=True)),
                ('del_flag', models.CharField(max_length=1)),
                ('salesman', models.CharField(max_length=20, null=True, blank=True)),
                ('website', models.CharField(max_length=100, null=True, blank=True)),
                ('remarks', models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={
                'db_table': 'sys_org',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SysUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('email', models.EmailField(max_length=255, verbose_name=b'Email', db_index=True)),
                ('username', models.CharField(max_length=50, db_index=True)),
                ('first_name', models.CharField(max_length=50, db_index=True)),
                ('last_name', models.CharField(max_length=50, db_index=True)),
                ('is_active', models.BooleanField(default=True, choices=[(True, '\u5728\u7528'), (False, '\u505c\u7528')])),
                ('is_admin', models.BooleanField(default=False, choices=[(True, '\u662f'), (False, '\u4e0d\u662f')])),
                ('is_superuser', models.BooleanField(default=False)),
                ('sex', models.IntegerField(default=0)),
                ('mobile', models.CharField(max_length=50, null=True, blank=True)),
                ('chat_type', models.CharField(max_length=100, null=True, blank=True)),
                ('chat_id', models.CharField(max_length=50, null=True, blank=True)),
                ('desc', models.CharField(max_length=2000, null=True, blank=True)),
                ('avatar', models.ImageField(default=b'avatar/1.jpg', upload_to=b'avatar/')),
            ],
            options={
                'db_table': 'sys_user',
            },
        ),
        migrations.CreateModel(
            name='PermissionList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('url', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'permissionlist',
            },
        ),
        migrations.CreateModel(
            name='RoleList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('permission', models.ManyToManyField(to='sysadmin.PermissionList', null=True, blank=True)),
            ],
            options={
                'db_table': 'rolelist',
            },
        ),
        migrations.CreateModel(
            name='SysArea',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category', models.CharField(max_length=20, null=True, blank=True)),
                ('code', models.CharField(max_length=12, null=True, blank=True)),
                ('super_code', models.CharField(max_length=12, null=True, blank=True)),
                ('name', models.CharField(max_length=20, null=True, blank=True)),
                ('status', models.CharField(max_length=2, null=True, blank=True)),
                ('hot', models.CharField(max_length=2, null=True, blank=True)),
                ('initial', models.CharField(max_length=10, null=True, blank=True)),
                ('longitude', models.DecimalField(null=True, max_digits=10, decimal_places=6, blank=True)),
                ('latitude', models.DecimalField(null=True, max_digits=10, decimal_places=6, blank=True)),
                ('description', models.CharField(max_length=255, null=True, blank=True)),
                ('create_by', models.CharField(max_length=20, null=True, blank=True)),
                ('update_by', models.CharField(max_length=20, null=True, blank=True)),
                ('create_time', models.DateTimeField(null=True, blank=True)),
                ('update_time', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'db_table': 'sys_area',
            },
        ),
        migrations.CreateModel(
            name='SysDict',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dict_name', models.CharField(max_length=100)),
                ('dict_id', models.CharField(max_length=100)),
                ('dict_type', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=100)),
                ('sort', models.IntegerField()),
                ('create_by', models.CharField(max_length=64, null=True, blank=True)),
                ('create_date', models.DateTimeField(null=True, blank=True)),
                ('update_by', models.CharField(max_length=64, null=True, blank=True)),
                ('update_date', models.DateTimeField(null=True, blank=True)),
                ('remarks', models.CharField(max_length=255, null=True, blank=True)),
                ('del_flag', models.CharField(max_length=1)),
            ],
            options={
                'db_table': 'sys_dict',
            },
        ),
        migrations.CreateModel(
            name='SysLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_name', models.CharField(max_length=64, null=True, verbose_name=b'\xe7\x94\xa8\xe6\x88\xb7\xe5\x90\x8d', blank=True)),
                ('user_mobile', models.CharField(max_length=64, null=True, verbose_name=b'\xe7\x94\xa8\xe6\x88\xb7\xe6\x89\x8b\xe6\x9c\xba\xe5\x8f\xb7', blank=True)),
                ('user_role_name', models.CharField(max_length=32, null=True, verbose_name=b'\xe7\x94\xa8\xe6\x88\xb7\xe8\xa7\x92\xe8\x89\xb2\xe5\x90\x8d\xe7\xa7\xb0', blank=True)),
                ('sys_org_name', models.CharField(max_length=64, null=True, verbose_name=b'\xe6\x89\x80\xe5\xb1\x9e\xe6\x9c\xba\xe6\x9e\x84', blank=True)),
                ('handle_url', models.CharField(max_length=512, null=True, verbose_name=b'\xe6\x93\x8d\xe4\xbd\x9c\xe8\xb5\x84\xe6\xba\x90url', blank=True)),
                ('handle_params', models.CharField(max_length=2000, null=True, verbose_name=b'\xe6\x93\x8d\xe4\xbd\x9c\xe5\x8f\x82\xe6\x95\xb0', blank=True)),
                ('sys_timestamp', models.CharField(max_length=32, null=True, verbose_name=b'\xe6\x93\x8d\xe4\xbd\x9c\xe6\x97\xb6\xe9\x97\xb4', blank=True)),
                ('ip_address', models.CharField(max_length=64, null=True, verbose_name=b'ip\xe5\x9c\xb0\xe5\x9d\x80', blank=True)),
            ],
            options={
                'db_table': 'sys_log',
            },
        ),
        migrations.AddField(
            model_name='sysuser',
            name='role',
            field=models.ForeignKey(blank=True, to='sysadmin.RoleList', null=True),
        ),
        migrations.AddField(
            model_name='sysuser',
            name='sys_org',
            field=models.ForeignKey(blank=True, to='sysadmin.SysOrg', null=True),
        ),
    ]
