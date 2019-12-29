#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/17 10:32
# @Author  :
# @Site    :
# @File    : urls.py
# @Software: PyCharm

from django.conf.urls import url
from views_threshold import ThresholdList, ThresholdJson, CreateThreshold, EditThreshold, delete_threshold
from views_electricbox import ElectricboxList, ElectricboxJson, CreateElectricbox, EditElectricbox, electricbox_batches_delete, electribox_add
from views_overrating import OverRatingList, OverRatingJson
from views_file import UpLoadFileConfig
from views_industrypark_source import IndustryParkSourceList, IndustryParkSourceJson, CreateIndustryParkSource, EditIndustryParkSource
from views_device_room import DeviceRoomList, DeviceRoomJson, EditDeviceRoom
from views_graph import GraphListView
from views_network_device import NetworkDeviceList, NetworkDeviceJosn, CreateNetworkDevice, EditNetworkDevice, networkdevice_batches_delete
from views_idc_buildingmgr import IDCBuildingmgrList, IDCBuildingmgrJson
from views_idc_workorder_platform import IDCWorkorderPlatformList, IDCWorkorderPlatformJson, CreateIDCWorkorderPlatform, configer_workorder, idc_workorder_delete
from views_ip_workorder import *
from views_electricbox_input import electribox_input
from views_ip_insert_model import *
from views_electricbox_workorder import *
from views_idc_workorder_verify import *
from views_network_device_workorder import *
from views_ip_backup_model import *
from views_interface_workorder import *
from views_idc_client import *
from views_ip_insert_model_msg import *
from views_ip_backup_model_msg import *
from views_industrypark import *
from views_ipmgr import *


urlpatterns = [
    #工单客户管理
    url(r'^cabinetmgr/idcclient/list/\d+$', IDCClientList.as_view(), name='idcclient.list'),  # 客户列表
    url(r'^cabinetmgr/idcclient/data/(?P<industry_id>\d+)$', IDCClientJson.as_view(), name='idcclient.data'),  # 获取数据
    url(r'^cabinetmgr/idcclient/list/add/\d+$', CreateIDCClient.as_view(), name='idcclient.add'),  # 添加
    url(r'^cabinetmgr/idcclient/list/edit/(?P<pk>\d+)/(?P<industry_id>\d+)$', EditIDCClient.as_view(), name='idcclient.edit'),  # 编辑
    url(r'^cabinetmgr/idcclient/delete/$', delete_idc_client, name='idcclient.delete'),  # 删除

    #园区ip管理
    url(r'^cabinetmgr/ipmgr/list/\d+$', IPmgrList.as_view(), name='ipmgr.list'),  # 客户列表
    url(r'^cabinetmgr/ipmgr/data/(?P<industry_id>\d+)$', IPmgrJson.as_view(), name='ipmgr.data'),  # 获取数据
    url(r'^cabinetmgr/ipmgr/list/add/\d+$', IPmgrCreate.as_view(), name='ipmgr.add'),  # 添加

    #机柜管理
    url(r'^cabinetmgr/electricbox/list/\d+$', ElectricboxList.as_view(), name='electricbox.list'),  # 机柜列表
    url(r'^cabinetmgr/electricbox/data/(?P<industry_id>\d+)$', ElectricboxJson.as_view(), name='electricbox.data'),  # 获取数据
    url(r'^cabinetmgr/electricbox/list/add/\d+$', electribox_add, name='electricbox.add'),  # 添加
    url(r'^cabinetmgr/electricbox/edit/(?P<pk>\d+)/$', EditElectricbox.as_view(), name='electricbox.edit'),  # 编辑
    url(r'^cabinetmgr/electricbox/delete/$', electricbox_batches_delete, name='electricbox.delete'),  # 删除

    #超阀值机柜列表
    url(r'^cabinetmgr/overrating/list/\d+$', OverRatingList.as_view(), name='overrating.list'),  # 超阀值机柜列表
    url(r'^cabinetmgr/overrating/data/(?P<industry_id>\d+)$', OverRatingJson.as_view(), name='overrating.data'),  # 获取数据

    #阀值管理
    url(r'^cabinetmgr/threshold/list$', ThresholdList.as_view(), name='threshold.list'),  # 阀值列表
    url(r'^cabinetmgr/threshold/data/$', ThresholdJson.as_view(), name='threshold.data'),  # 获取数据
    url(r'^cabinetmgr/threshold/add/$', CreateThreshold.as_view(), name='threshold.add'),  # 添加
    url(r'^cabinetmgr/threshold/edit/(?P<pk>\d+)/$', EditThreshold.as_view(), name='threshold.edit'),  # 编辑
    url(r'^cabinetmgr/threshold/delete/$', delete_threshold, name='threshold.delete'),  # 删除
    #
    # url(r'^dialing/devicedialing/dialingtest/(?P<pk>\d+)/$', DialingTest.as_view(), name='devicedialing.test'),  # 编辑
    url(r'^cabinetmgr/file/upload/\d+', UpLoadFileConfig, name='file.upload'),  # 文件上传

    #园区信息
    url(r'^cabinetmgr/industryparksource/list/\d+$', IndustryParkSourceList.as_view(), name='industryparksource.list'),  # 列表
    url(r'^cabinetmgr/industryparksource/data/(?P<industry_id>\d+)$', IndustryParkSourceJson.as_view(), name='industryparksource.data'),  # 获取数据
    url(r'^cabinetmgr/industryparksource/add$', CreateIndustryParkSource.as_view(), name='industryparksource.add'), #添加
    url(r'^cabinetmgr/industryparksource/list/edit/(?P<pk>\d+)/$', EditIndustryParkSource.as_view(), name='industryparksource.edit'), #编辑

    #园区管理
    url(r'^cabinetmgr/industrypark/list$', IndustryParkList.as_view(), name='industrypark.list'),  # 列表
    url(r'^cabinetmgr/industrypark/data$', IndustryParkJson.as_view(), name='industrypark.data'),  # 获取数据
    url(r'^cabinetmgr/industrypark/add$', CreateIndustryPark.as_view(), name='industrypark.add'), #添加
    url(r'^cabinetmgr/industrypark/edit/(?P<pk>\d+)/$', EditIndustryPark.as_view(), name='industrypark.edit'), #编辑
    url(r'^cabinetmgr/industrypark/delete/$', delete_industryparksource, name='industrypark.delete'),  # 删除

    #机楼管理
    # url(r'^cabinetmgr/idc_buildingmgr/list/$', IDCBuildingmgrList.as_view(), name='idcbuildingmgr.list'),  # 列表
    # url(r'^cabinetmgr/idc_buildingmgr/data/$', IDCBuildingmgrJson.as_view(), name='idcbuildingmgr.data'),  # 获取数据
    url(r'^cabinetmgr/industrybuilding/list$', IndustryBuildingList.as_view(), name='industrybuilding.list'),  # 列表
    url(r'^cabinetmgr/industrybuilding/data$', IndustryBuildingJson.as_view(), name='industrybuilding.data'),  # 获取数据
    url(r'^cabinetmgr/industrybuilding/add$', CreateIndustryBuilding.as_view(), name='industrybuilding.add'), #添加
    url(r'^cabinetmgr/industrybuilding/edit/(?P<pk>\d+)/$', EditIndustryBuilding.as_view(), name='industrybuilding.edit'), #编辑

    #机房平面图
    url(r'^cabinetmgr/roomgraphfile/add/\d+/$', room_graph_file, name='roomgraphfile.add'), #批量导入、回收ip

    #机房管理
    url(r'^cabinetmgr/industryroom/add$', idc_room_add, name='industryroom.add'), #批量导入机房

    #二级机房
    url(r'^cabinetmgr/deviceroom/list/\d+$', DeviceRoomList.as_view(), name='deviceroom.list'),  # 列表
    url(r'^cabinetmgr/deviceroom/data/(?P<industry_id>\d+)$', DeviceRoomJson.as_view(), name='deviceroom.data'),  # 获取数据
    url(r'^cabinetmgr/deviceroom/edit/(?P<pk>\d+)/$', EditDeviceRoom.as_view(), name='deviceroom.edit'), #编辑

    #机房平面图
    url(r'^cabinetmgr/graph/list/\d+$', GraphListView.as_view(), name='graph.list'),  # 平面图

    #机柜内部空间详情
    url(r'^cabinetmgr/networkdevice/list/(?P<device_id>\d+)$', NetworkDeviceList.as_view(), name='networkdevice.list'),  # 列表
    url(r'^cabinetmgr/networkdevice/data/$', NetworkDeviceJosn.as_view(), name='networkdevice.data'),  # 获取数据
    url(r'^cabinetmgr/networkdevice/list/add/$', CreateNetworkDevice.as_view(), name='networkdevice.add'), #添加
    url(r'^cabinetmgr/networkdevice/list/edit/(?P<pk>\d+)/$', EditNetworkDevice.as_view(), name='networkdevice.edit'), #编辑
    url(r'^cabinetmgr/networkdevice/list/delete/$', networkdevice_batches_delete, name='networkdevice.delete'),  # 删除

    #idc工单创建
    url(r'^cabinetmgr/idcworkorderplatform/list/(?P<industry_id>\d+)$', IDCWorkorderPlatformList.as_view(), name='idcworkorderplatform.list'),  # 列表
    url(r'^cabinetmgr/idcworkorderplatform/data/(?P<industry_id>\d+)$', IDCWorkorderPlatformJson.as_view(), name='idcworkorderplatform.data'),  # 获取数据
    url(r'^cabinetmgr/idcworkorderplatform/list/add/(?P<industry_id>\d+)$', CreateIDCWorkorderPlatform.as_view(), name='idcworkorderplatform.add'), #添加
    url(r'^cabinetmgr/idcworkorderplatform/delete/$', idc_workorder_delete, name='idcworkorderplatform.delete'),  # 删除

    #ip分配
    # url(r'^cabinetmgr/ipworkorder/mgr$', IpDistribute.as_view(), name='ipworkorder.mgr'),  # 初次添加或回收ip
    # url(r'^cabinetmgr/ipworkorder/mgr/\d+/$', IpDistribute.as_view(), name='ipworkorder.again'),  # 二次或多次添加或回收ip

    #批量导入机柜
    url(r'^cabinetmgr/electricboxinput/mgr$', electribox_input, name='electricboxinput.mgr'),

    #确认结单
    url(r'^cabinetmgr/configerworkorder/cfg/\d+/\d+$', configer_workorder, name='configerworkorder.cfg'), #确认结单

    #ip工单操作列表
    url(r'^cabinetmgr/ipdistribute/list/\d+/\d+$', IpDistributeList.as_view(), name='ipdistribute.list'),  # 列表
    url(r'^cabinetmgr/ipdistribute/data/(?P<industry_id>\d+)$', IpDistributeJson.as_view(), name='ipdistribute.data'),  # 获取数据
    url(r'^cabinetmgr/ipdistribute/list/add/\d+$', ip_workorder_add, name='ipdistribute.add'), #批量导入、回收ip
    url(r'^cabinetmgr/ipdistribute/list/delete/$', delete_workorder_ip, name='ipdistribute.delete'),  # 回退
    url(r'^cabinetmgr/ipdistribute/retry/\d+/\d+$', ip_retry_botton, name='ipdistribute.retry'),  # 重试

    #ip导入模板
    url(r'^cabinetmgr/iplist/list/\d+$', IpList.as_view(), name='iplist.list'),  # 列表
    url(r'^cabinetmgr/iplist/data/(?P<industry_id>\d+)$', IpListJson.as_view(), name='iplist.data'),  # 获取数据

    #ip备案模板
    url(r'^cabinetmgr/ipbackuplist/list/\d+$', IpBackupList.as_view(), name='ipbackuplist.list'),  # 列表
    url(r'^cabinetmgr/ipbackuplist/data/(?P<industry_id>\d+)$', IpBackupListJson.as_view(), name='ipbackuplist.data'),  # 获取数据

    #机柜工单操作列表
    url(r'^cabinetmgr/electricboxdistribute/list/\d+/\d+$', ElectricboxDistributeList.as_view(), name='electricboxdistribute.list'),  # 列表
    url(r'^cabinetmgr/electricboxdistribute/data/(?P<industry_id>\d+)$', ElectricboxDistributeJson.as_view(), name='electricboxdistribute.data'),  # 获取数据
    url(r'^cabinetmgr/electricboxdistribute/list/edit/(?P<pk>\d+)/$', EditElectricboxWorkorder.as_view(), name='electricboxdistribute.edit'), #编辑
    url(r'^cabinetmgr/electricboxdistribute/list/add/\d+$', electribox_workorder, name='electricboxdistribute.add'), #批量导入、回收机柜
    url(r'^cabinetmgr/electricboxdistribute/list/delete/$', delete_workorder_electricbox, name='electricboxdistribute.delete'),  # 回退
    url(r'^cabinetmgr/electricboxdistribute/retry/\d+/\d+$', elbox_retry_botton, name='electricboxdistribute.retry'),  # 重试

    #设备工单操作列表
    url(r'^cabinetmgr/networkdevicedistribute/list/\d+/\d+$', NetworkDeviceDistributeList.as_view(), name='networkdevicedistribute.list'),  # 列表
    url(r'^cabinetmgr/networkdevicedistribute/data/(?P<industry_id>\d+)$', NeworkDeviceDistributeJson.as_view(), name='networkdevicedistribute.data'),  # 获取数据
    url(r'^cabinetmgr/networkdevicedistribute/list/edit/(?P<pk>\d+)/$', EditNeworkDeviceDistribute.as_view(), name='networkdevicedistribute.edit'), #编辑
    url(r'^cabinetmgr/networkdevicedistribute/list/add/\d+$', network_device_workorder, name='networkdevicedistribute.add'), #批量导入、回收设备
    url(r'^cabinetmgr/networkdevicedistribute/list/delete/$', delete_workorder_networkdevice, name='networkdevicedistribute.delete'),  # 回退
    url(r'^cabinetmgr/networkdevicedistribute/retry/\d+/\d+$', device_retry_botton, name='networkdevicedistribute.retry'),  # 重试

    #端口操作工单操作列表
    url(r'^cabinetmgr/interfacedistribute/list/\d+/\d+$', InterfaceDistributeList.as_view(), name='interfacedistribute.list'),  # 列表
    url(r'^cabinetmgr/interfacedistribute/data/(?P<pk>\d+)$', InterfaceDistributeJson.as_view(), name='interfacedistribute.data'),  # 获取数据
    url(r'^cabinetmgr/interfacedistribute/list/add/\d+/\d+$', interface_workorder_handle, name='interfacedistribute.add'), #批量导入、回收端口
    url(r'^cabinetmgr/interfacedistribute/list/delete/$', delete_workorder_interface, name='interfacedistribute.delete'),  # 回退
    url(r'^cabinetmgr/interfacedistribute/retry/\d+/\d+$', interface_retry_botton, name='interfacedistribute.retry'),  # 重试

    #idc工单审核
    url(r'^cabinetmgr/idcworkordervertify/list/\d+$', IDCWorkorderVerifyList.as_view(), name='idcworkordervertify.list'),  # 列表
    url(r'^cabinetmgr/idcworkordervertify/data/(?P<industry_id>\d+)$', IDCWorkorderVerifyJson.as_view(), name='idcworkordervertify.data'),  # 获取数据

    #ip审核与驳回
    url(r'^cabinetmgr/ipvertify/list/\d+/\d+$', IpVertifyList.as_view(), name='ipvertify.list'),  # 列表
    url(r'^cabinetmgr/ipvertify/data/(?P<workorder_id>\d+)/(?P<industry_id>\d+)$', IpVertifyJson.as_view(), name='ipvertify.data'),  # 获取数据
    url(r'^cabinetmgr/ipvertify/\d+/\d+$', config_vertify, name='ipvertify.ver'), #批量导入、回收ip
    url(r'^cabinetmgr/ipdistribute/list/delete/(?P<industry_id>\d+)$', delete_workorder_ip, name='ipdistribute.delete'),  # 回退

    #审核记录
    url(r'^cabinetmgr/vertifyrecord/list/(?P<workorder_id>\d+)/(?P<operate_type>\d+)/(?P<industry_id>\d+)$', VertifyRecordList.as_view(), name='vertifyrecord.list'),  # 列表
    url(r'^cabinetmgr/vertifyrecord/data/(?P<workorder_id>\d+)/(?P<operate_type>\d+)/(?P<industry_id>\d+)$', VertifyRecordJson.as_view(), name='vertifyrecord.data'),  # 获取数据

    #机柜审核与驳回
    url(r'^cabinetmgr/electricboxvertify/list/\d+/\d+$', ElectricboxVertifyList.as_view(), name='electricboxvertify.list'),  # 列表
    url(r'^cabinetmgr/electricboxvertify/data/(?P<workorder_id>\d+)/(?P<industry_id>\d+)$', ElectricboxVertifyJson.as_view(), name='electricboxvertify.data'),  # 获取数据
    url(r'^cabinetmgr/electricboxvertify/\d+/\d+$', config_vertify, name='electricboxvertify.ver'), #批量导入、回收机柜
    url(r'^cabinetmgr/electricboxvertify/list/delete/$', delete_workorder_ip, name='electricboxvertify.delete'),  # 回退

    #设备审核与驳回
    url(r'^cabinetmgr/networkdevicevertify/list/\d+/\d+$', NetworkDeviceVertifyList.as_view(), name='networkdevicevertify.list'),  # 列表
    url(r'^cabinetmgr/networkdevicevertify/data/(?P<workorder_id>\d+)/(?P<industry_id>\d+)$', NetworkDeviceVertifyJson.as_view(), name='networkdevicevertify.data'),  # 获取数据
    url(r'^cabinetmgr/networkdevicevertify/\d+/\d+$', config_vertify, name='networkdevicevertify.ver'), #批量导入、回收设备
    url(r'^cabinetmgr/networkdevicevertify/list/delete/$', delete_workorder_ip, name='networkdevicevertify.delete'),  # 回退

    #网络端口审核与驳回
    url(r'^cabinetmgr/interfacevertify/list/\d+/\d+$', InterfaceVertifyList.as_view(), name='interfacevertify.list'),  # 列表
    url(r'^cabinetmgr/interfacevertify/data/(?P<workorder_id>\d+)/(?P<industry_id>\d+)$', InterfaceVertifyJson.as_view(), name='interfacevertify.data'),  # 获取数据
    url(r'^cabinetmgr/interfacevertify/\d+/\d+$', config_vertify, name='interfacevertify.ver'), #批量导入、回收设备

    #ip导入模板信息
    url(r'^cabinetmgr/ipinsertmodelmsg/list/\d+$', IpInsertModelMSGList.as_view(), name='ipinsertmodelmsg.list'),  # 列表
    url(r'^cabinetmgr/ipinsertmodelmsg/data/(?P<workorder_id>\d+)$', IpInsertModelMSGJson.as_view(), name='ipinsertmodelmsg.data'),  # 获取数据
    url(r'^cabinetmgr/ipinsertmodelmsg/list/add/$', insert_model_msg, name='ipinsertmodelmsg.add'),  # 添加
    url(r'^cabinetmgr/ipinsertmodelmsg/list/delete/$', delete_IpInsertModelMSG, name='ipinsertmodelmsg.delete'),  # 删除

    #ip备案模板信息
    url(r'^cabinetmgr/ipbackupmodelmsg/list/\d+$', IpBackupModelMSGList.as_view(), name='ipbackupmodelmsg.list'),  # 列表
    url(r'^cabinetmgr/ipbackupmodelmsg/data/(?P<industry_id>\d+)$', IpBackupModelMSGJson.as_view(), name='ipbackupmodelmsg.data'),  # 获取数据
    url(r'^cabinetmgr/ipbackupmodelmsg/list/add/$', backup_model_msg, name='ipbackupmodelmsg.add'),  # 添加
    url(r'^cabinetmgr/ipbackupmodelmsg/list/delete/$', delete_ipbackupmode, name='ipbackupmodelmsg.delete'),  # 删除

]
