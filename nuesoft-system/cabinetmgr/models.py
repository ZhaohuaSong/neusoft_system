#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/17 14:24
# @Author  :
# @Site    :
# @File    : views_diamgr.py
# @Software: PyCharm
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Threshold(models.Model):
    threshold = models.IntegerField(max_length=20)
    tab_id = models.IntegerField(max_length=20)

    class Meta:
        managed = False
        db_table = 'threshold'

class EquipmentCabinet(models.Model):
    eq_name = models.CharField(max_length=64)
    power = models.IntegerField(max_length=64)

    class Meta:
        managed = False
        db_table = 'equipment_cabinet'



class OverRating(models.Model):
    device_room = models.CharField(max_length=64, blank=True, null=True) #机房名称
    box_name = models.CharField(max_length=64, blank=True, null=True) #机柜名称
    client_name = models.CharField(max_length=64, blank=True, null=True) #客户名称
    power_rating = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True) #功率阀值
    avg_power_rating = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True) #平均功率
    month = models.CharField(max_length=64, blank=True, null=True) #月份
    # on_state_date = models.DateTimeField(blank=True, null=True) #上架日期
    # power_on_date = models.DateTimeField(blank=True, null=True) #加电日期

    class Meta:
        managed = False
        db_table = 'over_rating'




class Filename(models.Model):
    file_name = models.CharField(max_length=64) #原始文件名

    class Meta:
        db_table = 'file_name'

class IDCBuilding(models.Model):
    park_id = models.IntegerField(blank=True, null=True)
    building_name = models.CharField(max_length=64, blank=True, null=True)
    building_id = models.IntegerField(max_length=20, blank=True, null=True)
    room_graph_file = models.CharField(max_length=255, blank=True, null=True)
    # park = models.ForeignKey('IndustryPark', models.DO_NOTHING, blank=True, null=True)
    # id = models.ForeignKey(BuildingRoom, models.DO_NOTHING, db_column='id', primary_key=True)

    class Meta:
        managed = False
        db_table = 'idc_building'

class BuildingRoom(models.Model):
    building_id = models.IntegerField(blank=True, null=True)
    industry_id = models.IntegerField(blank=True, null=True)
    room_name = models.CharField(max_length=64, blank=True, null=True)
    volume = models.IntegerField(blank=True, null=True)
    total_box_num = models.IntegerField(blank=True, null=True)
    # building = models.ForeignKey('IDCBuilding', models.DO_NOTHING, blank=True, null=True)
    # building = models.ManyToManyField(to="Electricbox", name="room_id")

    def __unicode__(self):
        return self.room_name

    class Meta:
        managed = False
        db_table = 'building_room'

class Electricbox(models.Model):
    room_id = models.IntegerField(max_length=20, blank=True, null=True) #机房关联id
    building_id = models.IntegerField(max_length=20, blank=True, null=True)
    industry_id = models.IntegerField(max_length=20, blank=True, null=True)
    box_id = models.IntegerField(max_length=20, blank=True, null=True) #机柜id
    device_room = models.CharField(max_length=64, blank=True, null=True) #机房名称
    box_name = models.CharField(max_length=64, blank=True, null=True) #机柜名称
    client_name = models.CharField(max_length=64, blank=True, null=True) #客户名称
    power_rating = models.DecimalField(max_digits=64, decimal_places=2, blank=True, null=True) #额定功率
    threshold_rating = models.DecimalField(max_digits=64, decimal_places=2, blank=True, null=True) #阀值功率
    on_state_date = models.DateTimeField(blank=True, null=True) #上架日期
    power_on_date = models.DateTimeField(blank=True, null=True) #加电日期
    down_power_date = models.DateTimeField(blank=True, null=True) #下电日期
    device_num = models.IntegerField(max_length=20, blank=True, null=True) #机柜内部设备数量
    device_u_num = models.IntegerField(max_length=20, blank=True, null=True) #设备占用u数
    box_type = models.IntegerField(max_length=20, blank=True, null=True) #是否已分配
    income_time = models.DateTimeField(blank=True, null=True) #机柜进场时间
    pre_income_date = models.DateTimeField(blank=True, null=True) #机柜预占时间
    # room = models.ForeignKey(BuildingRoom, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'electricbox'

class HistoryPower(models.Model):
    boxid = models.IntegerField(max_length=20, blank=True, null=True)
    room_id = models.IntegerField(max_length=20, blank=True, null=True) #机房关联id
    building_id = models.IntegerField(blank=True, null=True)
    industry_id = models.IntegerField(blank=True, null=True)
    value = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    level = models.IntegerField(max_length=64, blank=True, null=True)
    clock = models.IntegerField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'history_power'

class IndustryPark(models.Model):
    park = models.CharField(max_length=64, blank=True, null=True) #机楼
    type = models.CharField(max_length=64, blank=True, null=True) #类型
    attribute = models.CharField(max_length=64, blank=True, null=True) #属性
    electric_cap = models.IntegerField(max_length=64, blank=True, null=True) #外电容量（KVA)
    power = models.IntegerField(max_length=64, blank=True, null=True) #使用功率
    usage_power = models.DecimalField(max_digits=64, decimal_places=2, blank=True, null=True) #外电使用率
    total_box = models.IntegerField(max_length=64, blank=True, null=True) #总计划建设机架数
    built = models.IntegerField(max_length=64, blank=True, null=True) #已建设机架数
    activate = models.IntegerField(max_length=64, blank=True, null=True) #已使用机架数
    unactivate = models.IntegerField(max_length=64, blank=True, null=True) #剩余机架数
    usage_box = models.DecimalField(max_digits=64, decimal_places=4, blank=True, null=True) #机架使用率
    remark = models.CharField(max_length=64, blank=True, null=True) #备注
    industry_id = models.IntegerField(max_length=64, blank=True, null=True) #园区id
    bandwidth = models.IntegerField(max_length=64, blank=True, null=True) #带宽
    # id = models.ForeignKey(IDCBuilding, models.DO_NOTHING, db_column='id', primary_key=True)

    def __unicode__(self):
        return self.park

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
    room_id = models.IntegerField(max_length=20, blank=True, null=True) #id
    building_id = models.IntegerField(blank=True, null=True)
    industry_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'device_room'

class SelectBox(models.Model):
    type_id = models.IntegerField(max_length=20, blank=True, null=True) #id
    box_type = models.CharField(max_length=64, blank=True, null=True) #机柜状态

    def __unicode__(self):
        return self.box_type

    class Meta:
        managed = False
        db_table = 'select_box'

class QRIDCRoom(models.Model):
    room_name = models.CharField(max_length=64, blank=True, null=True) #机房名称

    def __unicode__(self):
        return self.room_name

    class Meta:
        managed = False
        db_table = 'qridc_room'

class NetworkDevice(models.Model):
    box_id = models.IntegerField(blank=True, null=True)
    room_id = models.IntegerField(max_length=20, blank=True, null=True) #机房关联id
    building_id = models.IntegerField(blank=True, null=True)
    industry_id = models.IntegerField(blank=True, null=True)
    on_state_date = models.DateTimeField(blank=True, null=True)
    power_on_date = models.DateTimeField(blank=True, null=True)
    down_power_date = models.DateTimeField(blank=True, null=True)
    device_num = models.IntegerField(blank=True, null=True)
    start_u_num = models.IntegerField(blank=True, null=True)
    end_u_num = models.IntegerField(blank=True, null=True)
    total_u_num = models.IntegerField(blank=True, null=True)
    device_code = models.CharField(max_length=64, blank=True, null=True)
    device_type = models.CharField(max_length=64, blank=True, null=True)
    device_status = models.CharField(max_length=64, blank=True, null=True)
    power_num = models.CharField(max_length=64, blank=True, null=True)
    device_alternating = models.CharField(max_length=64, blank=True, null=True)
    device_threshold_rt = models.DecimalField(max_digits=64, decimal_places=4, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'network_device'

class NetworkDeviceWorkorder(models.Model):
    box_id = models.IntegerField(blank=True, null=True)
    room_id = models.IntegerField(max_length=20, blank=True, null=True) #机房关联id
    building_id = models.IntegerField(blank=True, null=True)
    industry_id = models.IntegerField(blank=True, null=True)
    on_state_date = models.DateTimeField(blank=True, null=True)
    power_on_date = models.DateTimeField(blank=True, null=True)
    down_power_date = models.DateTimeField(blank=True, null=True)
    device_num = models.IntegerField(blank=True, null=True)
    start_u_num = models.IntegerField(blank=True, null=True)
    end_u_num = models.IntegerField(blank=True, null=True)
    total_u_num = models.IntegerField(blank=True, null=True)
    device_code = models.CharField(max_length=64, blank=True, null=True)
    device_type = models.CharField(max_length=64, blank=True, null=True)
    device_status = models.CharField(max_length=64, blank=True, null=True)
    power_num = models.CharField(max_length=64, blank=True, null=True)
    device_alternating = models.CharField(max_length=64, blank=True, null=True)
    device_threshold_rt = models.DecimalField(max_digits=64, decimal_places=4, blank=True, null=True)
    handle_id = models.IntegerField(max_length=20, blank=True, null=True) #添加或删除
    workorder_id = models.IntegerField(max_length=20, blank=True, null=True) #工单id
    client_name = models.CharField(max_length=64, blank=True, null=True) #客户名称

    class Meta:
        managed = False
        db_table = 'network_device_workorder'

class IDCWorkorderPlatform(models.Model):
    industry_id = models.IntegerField(blank=True, null=True)
    workorder_name = models.CharField(max_length=64, blank=True, null=True)
    client_name = models.CharField(max_length=64, blank=True, null=True)
    operate_ip = models.IntegerField(blank=True, null=True)
    operate_record = models.TextField(blank=True, null=True)
    operate_elbox = models.IntegerField(blank=True, null=True)
    operate_device = models.IntegerField(blank=True, null=True)
    operate_interface = models.IntegerField(blank=True, null=True)
    ip_vertify = models.IntegerField(max_length=20, blank=True, null=True)
    elbox_vertify = models.IntegerField(max_length=20, blank=True, null=True)
    device_vertify = models.IntegerField(max_length=20, blank=True, null=True)
    port_vertify = models.IntegerField(max_length=20, blank=True, null=True)
    vertify_status = models.IntegerField(max_length=20, blank=True, null=True)
    submit = models.IntegerField(blank=True, null=True)
    workorder_status = models.IntegerField(blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    create_user = models.CharField(max_length=64, blank=True, null=True)
    auditor = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'idc_workorder_platform'

class IpLibrary(models.Model):
    using_ip_num = models.IntegerField(blank=True, null=True)
    unuse_ip_num = models.IntegerField(blank=True, null=True)
    all_ip = models.TextField(blank=True, null=True)
    industry_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ip_library'

class IpClient(models.Model):
    client_name = models.CharField(max_length=64, blank=True, null=True)
    industry_id = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return self.client_name

    class Meta:
        managed = False
        db_table = 'ip_client'

class IpAddress(models.Model):
    ip_addr = models.TextField(max_length=500,blank=True, null=True)
    client_id = models.IntegerField(blank=True, null=True)
    industry_id = models.IntegerField(blank=True, null=True)
    ip_num = models.IntegerField(blank=True, null=True)
    # ip_set = models.IntegerField(blank=True, null=True)
    # workorder_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ip_address'

class IpAddressList(models.Model):
    ip_addr = models.CharField(max_length=64, blank=True, null=True)
    client_id = models.IntegerField(blank=True, null=True)
    industry_id = models.IntegerField(blank=True, null=True)
    ip_num = models.IntegerField(blank=True, null=True)
    ip_set = models.IntegerField(blank=True, null=True)
    mask = models.IntegerField(blank=True, null=True)
    workorder_id = models.IntegerField(blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ip_address_list'

class IpAddressMask(models.Model):
    ip_addr = models.TextField(max_length=500,blank=True, null=True)
    client_id = models.IntegerField(blank=True, null=True)
    industry_id = models.IntegerField(blank=True, null=True)
    mask = models.IntegerField(blank=True, null=True)
    # ip_set = models.IntegerField(blank=True, null=True)
    # workorder_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ip_address_mask'

class ElectricboxWorkorder(models.Model):
    room_id = models.IntegerField(max_length=20, blank=True, null=True) #机房关联id
    building_id = models.IntegerField(blank=True, null=True)
    industry_id = models.IntegerField(blank=True, null=True)
    box_id = models.IntegerField(max_length=20, blank=True, null=True) #机柜id
    device_room = models.CharField(max_length=64, blank=True, null=True) #机房名称
    box_name = models.CharField(max_length=64, blank=True, null=True) #机柜名称
    client_name = models.CharField(max_length=64, blank=True, null=True) #客户名称
    power_rating = models.DecimalField(max_digits=64, decimal_places=2, blank=True, null=True) #额定功率
    threshold_rating = models.DecimalField(max_digits=64, decimal_places=2, blank=True, null=True) #阀值功率
    on_state_date = models.DateTimeField(blank=True, null=True) #上架日期
    power_on_date = models.DateTimeField(blank=True, null=True) #加电日期
    down_power_date = models.DateTimeField(blank=True, null=True) #下电日期
    device_num = models.IntegerField(max_length=20, blank=True, null=True) #机柜内部设备数量
    device_u_num = models.IntegerField(max_length=20, blank=True, null=True) #设备占用u数
    box_type = models.IntegerField(max_length=20, blank=True, null=True) #是否已分配
    # room = models.ForeignKey(BuildingRoom, models.DO_NOTHING, blank=True, null=True)
    handle_id = models.IntegerField(max_length=20, blank=True, null=True) #添加或删除
    workorder_id = models.IntegerField(max_length=20, blank=True, null=True) #工单id


    class Meta:
        managed = False
        db_table = 'electricbox_workorder'

class ElectricboxClient(models.Model):
    client_name = models.CharField(max_length=64)
    # sheetsinterface = models.ManyToManyField(SheetsInterface, blank=True)
    industry_id = models.IntegerField(blank=True, null=True)
    table_id = models.IntegerField(max_length=20)
    tailer_id = models.CharField(max_length=20)
    type_id = models.IntegerField(max_length=20)

    def __unicode__(self):
        return self.client_name
    class Meta:
        db_table = 'electricbox_client'

class ListData(models.Model):
    ip_list = models.TextField(blank=True, null=True)
    class Meta:
        db_table = 'list_data'

class IpInsertModel(models.Model):
    network_name = models.CharField(max_length=32, blank=True, null=True)
    unit_name = models.CharField(max_length=32, blank=True, null=True)
    unit_type = models.CharField(max_length=32, blank=True, null=True)
    bussiness_license_num = models.CharField(max_length=32, blank=True, null=True)
    unit_property = models.CharField(max_length=32, blank=True, null=True)
    provinces = models.CharField(max_length=64, blank=True, null=True)
    city = models.CharField(max_length=64, blank=True, null=True)
    county = models.CharField(max_length=64, blank=True, null=True)
    administrative_level = models.CharField(max_length=64, blank=True, null=True)
    profession = models.CharField(max_length=64, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    customer_name = models.CharField(max_length=64, blank=True, null=True)
    customer_phone = models.CharField(max_length=64, blank=True, null=True)
    customer_email = models.CharField(max_length=64, blank=True, null=True)
    physical_gateway = models.CharField(max_length=64, blank=True, null=True)
    usage_mode = models.CharField(max_length=64, blank=True, null=True)
    use_time = models.DateTimeField(blank=True, null=True)
    gateway_ip_addr = models.CharField(max_length=64, blank=True, null=True)
    bussiness_type = models.CharField(max_length=64, blank=True, null=True)
    usage_status = models.CharField(max_length=64, blank=True, null=True)
    supervisor_status = models.CharField(max_length=64, blank=True, null=True)
    machine_room = models.CharField(max_length=64, blank=True, null=True)
    device_name = models.CharField(max_length=64, blank=True, null=True)
    loopbak_addr = models.CharField(max_length=64, blank=True, null=True)
    access_port_msg = models.CharField(max_length=64, blank=True, null=True)
    in_charge_department = models.CharField(max_length=64, blank=True, null=True)
    in_charge_person = models.CharField(max_length=64, blank=True, null=True)
    in_charge_phone = models.CharField(max_length=64, blank=True, null=True)
    in_charge_email = models.CharField(max_length=64, blank=True, null=True)
    remark = models.CharField(max_length=64, blank=True, null=True)
    subnet_mask = models.IntegerField(blank=True, null=True)
    collector = models.CharField(max_length=64, blank=True, null=True)
    industry_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ip_insert_model'

class IpBackupModel(models.Model):
    begin_ip = models.CharField(max_length=32, blank=True, null=True)
    end_ip = models.CharField(max_length=32, blank=True, null=True)
    unit_name = models.CharField(max_length=32, blank=True, null=True)
    unit_type = models.CharField(max_length=32, blank=True, null=True)
    bussiness_license_num = models.CharField(max_length=32, blank=True, null=True)
    unit_property = models.CharField(max_length=32, blank=True, null=True)
    provinces = models.CharField(max_length=64, blank=True, null=True)
    city = models.CharField(max_length=64, blank=True, null=True)
    county = models.CharField(max_length=64, blank=True, null=True)
    administrative_level = models.CharField(max_length=64, blank=True, null=True)
    profession = models.CharField(max_length=64, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    customer_name = models.CharField(max_length=64, blank=True, null=True)
    customer_phone = models.CharField(max_length=64, blank=True, null=True)
    customer_email = models.CharField(max_length=64, blank=True, null=True)
    physical_gateway = models.CharField(max_length=64, blank=True, null=True)
    usage_mode = models.CharField(max_length=64, blank=True, null=True)
    use_time = models.DateTimeField(blank=True, null=True)
    use_way = models.CharField(max_length=64, blank=True, null=True)
    report_unit = models.CharField(max_length=64, blank=True, null=True)
    source_unit = models.CharField(max_length=64, blank=True, null=True)
    redistribution_unit = models.CharField(max_length=64, blank=True, null=True)
    record_representation = models.CharField(max_length=64, blank=True, null=True)
    gateway_ip_addr = models.CharField(max_length=64, blank=True, null=True)
    source_record = models.CharField(max_length=64, blank=True, null=True)
    relate_num = models.CharField(max_length=64, blank=True, null=True)
    collector = models.CharField(max_length=64, blank=True, null=True)
    industry_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ip_backup_model'

class VertifyRecord(models.Model):
    workorder_id = models.IntegerField(blank=True, null=True)  # 工单ID
    user = models.CharField(max_length=100, blank=True, null=True)  # 用户名
    content = models.CharField(max_length=255, blank=True, null=True)  # 审核详情
    result = models.IntegerField(blank=True, null=True)  # 审核结果
    create_time = models.DateTimeField(blank=True, null=True)  # 审核时间
    industry_id = models.IntegerField(blank=True, null=True)
    operate_type = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vertify_record'

class InterfaceWorkorder(models.Model):
    ip = models.CharField(max_length=32, blank=True, null=True)
    interface = models.CharField(max_length=32, blank=True, null=True) #端口IDCWorkorder
    bandwidth = models.IntegerField(max_length=20, blank=True, null=True) #带宽
    handle_id = models.IntegerField(max_length=20, blank=True, null=True) #添加或删除
    workorder_id = models.IntegerField(max_length=20, blank=True, null=True) #工单id
    industry_id = models.IntegerField(blank=True, null=True)
    client_id = models.IntegerField(blank=True, null=True)
    in_itemid = models.IntegerField(blank=True, null=True)
    out_itemid = models.IntegerField(blank=True, null=True)
    table_id = models.IntegerField(blank=True, null=True)
    sheets_interface_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'interface_workorder'

class InterfaceBandwidth(models.Model):
    ip = models.CharField(max_length=32, blank=True, null=True)
    interface = models.CharField(max_length=32, blank=True, null=True) #端口IDCWorkorder
    bandwidth = models.IntegerField(max_length=20, blank=True, null=True) #带宽
    industry_id = models.IntegerField(blank=True, null=True)
    client_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'interface_bandwidth'

class ContractRack(models.Model):
    building = models.CharField(max_length=20)
    room = models.CharField(max_length=20)
    col = models.CharField(max_length=20)
    rack_pos = models.IntegerField()
    rack_power = models.FloatField()
    rack_status = models.CharField(max_length=10)
    power_up_time = models.DateTimeField(blank=True, null=True)
    power_down_time = models.DateTimeField(blank=True, null=True)
    # contract = models.ForeignKey('ContractContract', models.DO_NOTHING, blank=True, null=True)
    # mothercontract = models.ForeignKey('ContractMothercontract', models.DO_NOTHING, blank=True, null=True)
    power_up_secondarytime = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contract_rack'
        unique_together = (('building', 'room', 'col', 'rack_pos'),)
