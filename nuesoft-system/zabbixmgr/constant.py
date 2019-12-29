#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/11/16 16:48
# @Author  :
# @Site    :
# @File    : constant.py
# @Software: PyCharm

from ..cabinetmgr.models import IndustryPark
from ..sysadmin.models import SysUser

ONEDAY = 3600*24 #second
SIZE = 1024
ONEMIN = 1
FIVEMIN = 2
ONEHOUR = 3
ADAY = 4
#多端口
ONEMIN_INTERVAL = 1
FIVEMIN_INTERVAL = 5
ONEHOUR_INTERVAL = 12
ONEDAY_INTERVAL = 24

#单端口
SGL_ONEMIN_INTERVAL = 1
SGL_FIVEMIN_INTERVAL = 5
SGL_ONEHOUR_INTERVAL = 60
SGL_ONEDAY_INTERVAL = 1440

def get_industry_park(user):
    industry_id = SysUser.objects.get(username=user).industry_id
    if industry_id != 0:
        indus = list(IndustryPark.objects.filter(id=industry_id).values_list('id', 'park'))
    else:
        indus = list(IndustryPark.objects.all().values_list('id', 'park'))
    industry_dict = {}
    for i in indus:
        industry_dict[str(i[0])] = i[1]
    return industry_dict
