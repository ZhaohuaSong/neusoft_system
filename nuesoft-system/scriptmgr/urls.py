#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls import url
from views import scriptManager, CreateParamView

urlpatterns = [
    #脚本管理
    url(r'^scriptmgr/script/list$', scriptManager.as_view(), name='script.list'),  # 文件及信息显示列表
    url(r'^scriptmgr/script/add$', CreateParamView.as_view(), name='script.add'),  # 添加参数
]
