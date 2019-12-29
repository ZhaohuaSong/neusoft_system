#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from storage import ImageStorage
import base64

# Create your models here.

class FilePathName(models.Model):
    """
     ===============================================================================
     function：    文件链接设置Model
     developer:
     add-time      2017/1/11
     ===============================================================================
    """
    file_path_name = models.FileField(upload_to="uploadfiles/", storage=ImageStorage()) #文件路径
    file_standard_name = models.CharField(max_length=64) #标准文件名
    class Meta:
        db_table = 'file_path_name'

class FileUpload(models.Model):
    """
     ===============================================================================
     function：    文件链接设置Model
     developer:
     add-time      2017/1/11
     ===============================================================================
    """
    # file_path_name = models.FileField(upload_to="uploadfiles/", storage=ImageStorage()) #文件路径
    file_standard_name = models.CharField(max_length=64) #标准文件名
    class Meta:
        db_table = 'file_upload'

class Filename(models.Model):
    """
     ===============================================================================
     function：    原始文件名
     developer:
     add-time      2017/1/11
     ===============================================================================
    """
    file_name = models.CharField(max_length=64) #原始文件名

    class Meta:
        db_table = 'file_name'

class IndustryPark(models.Model):
    building = models.CharField(max_length=64, blank=True, null=True) #机楼
    type = models.CharField(max_length=64, blank=True, null=True) #类型
    attribute = models.CharField(max_length=64, blank=True, null=True) #属性
    electric_cap = models.IntegerField(max_length=64, blank=True, null=True) #外电容量（KVA)
    power = models.IntegerField(max_length=64, blank=True, null=True) #使用功率
    usage_power = models.DecimalField(max_digits=64, decimal_places=2, blank=True, null=True) #外电使用率
    total_box = models.IntegerField(max_length=64, blank=True, null=True) #总计划建设机架数
    built = models.IntegerField(max_length=64, blank=True, null=True) #已建设机架数
    activate = models.IntegerField(max_length=64, blank=True, null=True) #已使用机架数
    unactivate = models.IntegerField(max_length=64, blank=True, null=True) #剩余机架数
    usage_box = models.DecimalField(max_digits=64, decimal_places=2, blank=True, null=True) #机架使用率
    remark = models.CharField(max_length=64, blank=True, null=True) #备注

    class Meta:
        managed = False
        db_table = 'industry_park'

class DeviceRoom(models.Model):
    room = models.CharField(max_length=64, blank=True, null=True) #机房
    major = models.CharField(max_length=64, blank=True, null=True) #专业
    total_box = models.IntegerField(blank=True, null=True) #机架总数
    activate_box = models.IntegerField(blank=True, null=True) #已装机架数
    unactivate_box = models.IntegerField(blank=True, null=True) #预占机架数
    unuse_box = models.IntegerField(blank=True, null=True) #可预占机架数
    room_usage = models.DecimalField(max_digits=64, decimal_places=4, blank=True, null=True) #机房利用率
    check_box_power = models.IntegerField(blank=True, null=True) #验收机柜功率
    design_box_power = models.IntegerField(blank=True, null=True) #设计负载功率
    sign_box_power = models.IntegerField(blank=True, null=True) #签约负载功率
    destribute_box_power = models.IntegerField(blank=True, null=True) #分配负载功率
    sign_box_power_usage = models.DecimalField(max_digits=64, decimal_places=4, blank=True, null=True) #签约功率使用率

    class Meta:
        managed = False
        db_table = 'device_room'

# class Electricbox(models.Model):
#     device_room = models.CharField(max_length=64, blank=True, null=True) #机房名称
#     box_name = models.CharField(max_length=64, blank=True, null=True) #机柜名称
#     client_name = models.CharField(max_length=64, blank=True, null=True) #客户名称
#     power_rating = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True) #功率阀值
#     on_state_date = models.DateTimeField(blank=True, null=True) #上架日期
#     power_on_date = models.DateTimeField(blank=True, null=True) #加电日期
#
#     class Meta:
#         managed = False
#         db_table = 'electricbox'
