# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-10-22 20:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TestFileParam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(blank=True, max_length=64, null=True)),
                ('type', models.CharField(blank=True, max_length=10, null=True)),
                ('ip_addr', models.CharField(blank=True, max_length=1024, null=True)),
                ('param', models.CharField(blank=True, max_length=1024, null=True)),
                ('ways_name', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'db_table': 'test_file_param',
                'managed': False,
            },
        ),
    ]
