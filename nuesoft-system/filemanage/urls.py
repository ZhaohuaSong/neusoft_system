#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls import url
from views_file import FileListView
# from views_industrypark_source import IndustryParkSourceList, IndustryParkSourceJson, CreateIndustryParkSource, EditIndustryParkSource
# from views_device_room import DeviceRoomList, DeviceRoomJson

urlpatterns = [
    #文件管理中心
    url(r'^filemanage/file/list$', FileListView.as_view(), name='file.list'),  # 文件及信息显示列表

    # #一级机楼
    # url(r'^filemanage/IndustryParkSource/list$', IndustryParkSourceList.as_view(), name='IndustryParkSource.list'),  # 列表
    # url(r'^filemanage/IndustryParkSource/data/$', IndustryParkSourceJson.as_view(), name='IndustryParkSource.data'),  # 获取数据
    # url(r'^filemanage/IndustryParkSource/add$', CreateIndustryParkSource.as_view(), name='IndustryParkSource.add'), #添加
    # url(r'^filemanage/IndustryParkSource/edit/(?P<pk>\d+)/$', EditIndustryParkSource.as_view(), name='IndustryParkSource.edit'), #编辑
    #
    # #二级机房
    # url(r'^filemanage/deviceroom/list$', DeviceRoomList.as_view(), name='deviceroom.list'),  # 列表
    # url(r'^filemanage/deviceroom/data/$', DeviceRoomJson.as_view(), name='deviceroom.data'),  # 获取数据
]
