#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/10/2 12:30
# @Author  :
# @Site    :
# @File    : industrypark_source_views.py
# @Software: PyCharm

from django.views.generic import TemplateView
from ..common.datatables.views import BaseDatatableView
from django.db.models import Q
import datetime
from django.shortcuts import render,render_to_response
import time
import re
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from ..vanilla import CreateView, UpdateView
from models import *
from forms import *
from django.db.models import F
import json
import os
from subprocess import *

class DeviceRoomList(TemplateView):
    template_name = 'filemanage/device_room.list.html'

class DeviceRoomJson(BaseDatatableView):
    '''
    Json 数据格式
    '''
    model = DeviceRoom
    columns = ['id',
               'id',
               'room',
               'major',
               'total_box',
               'activate_box',
               'unactivate_box',
               'unuse_box',
               'room_usage',
               'check_box_power',
               'design_box_power',
               'sign_box_power',
               'destribute_box_power',
               'sign_box_power_usage']
    order_columns = columns

