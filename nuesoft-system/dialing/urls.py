#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/17 10:32
# @Author  :
# @Site    :
# @File    : urls.py
# @Software: PyCharm

from django.conf.urls import url
from views_autoping import AutoPing
from views_diamgr import DeviceDialingList, DeviceDialingJson, CreateDeviceDialing, EditDeviceDialing, delete_devicedialing, DialingTest

urlpatterns = [
    url(r'^dialing/autoping/list$', AutoPing.as_view(), name='autoping.list'),  # 自动拨测

    url(r'^dialing/devicedialing/list$', DeviceDialingList.as_view(), name='devicedialing.list'),  # 显示列表
    url(r'^dialing/devicedialing/data/$', DeviceDialingJson.as_view(), name='devicedialing.data'),  # 获取数据
    url(r'^dialing/devicedialing/add/$', CreateDeviceDialing.as_view(), name='devicedialing.add'),  # 添加
    url(r'^dialing/devicedialing/edit/(?P<pk>\d+)/$', EditDeviceDialing.as_view(), name='devicedialing.edit'),  # 编辑
    url(r'^dialing/devicedialing/delete/$', delete_devicedialing, name='devicedialing.delete'),  # 删除

    url(r'^dialing/devicedialing/dialingtest/(?P<pk>\d+)/$', DialingTest.as_view(), name='devicedialing.test'),  # 编辑
]
