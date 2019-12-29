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
from ..zabbixmgr.constant import get_industry_park

class DeviceRoomList(TemplateView):
    template_name = 'cabinetmgr/device_room_rate.list.html'

    def get(self, request, *args, **kwargs):
        us = request.user.username
        url = self.request.get_full_path()
        industry_id = int(re.findall('(\d+)$', url)[0])
        industry_park =get_industry_park(us)
        context = self.get_context_data(**kwargs)

        nodelist = []
        building = IDCBuilding.objects.filter(park_id=int(industry_id))
        for bd in building:
            nodes = {}
            nodes['text'] = bd.building_name
            nodes['nodes'] = [{'text': '安全范围', 'id': bd.building_id, 'tags': 1},
                              {'text': '超阀值', 'id': bd.building_id, 'tags': 2},
                              {'text': '超额定值', 'id': bd.building_id, 'tags': 3}]
            nodelist.append(nodes)
        context['treedata'] = json.dumps(nodelist)

        url = self.request.get_full_path()
        industry_id = int(re.findall('(\d+)$', url)[0])
        context['industry_id'] = industry_id
        context['industry_park'] = industry_park
        return self.render_to_response(context)

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

    def filter_queryset(self, qs):
        #搜索数据集
        building_id = int(self._querydict.get('id', 0))
        tags = int(self._querydict.get('tags', 0))
        url = self.request.get_full_path()
        industry_id = int(re.findall('(\d+)$', url)[0])
        if tags == 1:
            return super(DeviceRoomJson, self).filter_queryset(qs).filter(sign_box_power_usage__lt=0.8, industry_id=industry_id, building_id=building_id)
        elif tags == 2:
            return super(DeviceRoomJson, self).filter_queryset(qs).filter(Q(sign_box_power_usage__gte=0.8) & Q(sign_box_power_usage__lt=1) & Q(industry_id=industry_id) & Q(building_id=building_id))
        elif tags == 3:
            return super(DeviceRoomJson, self).filter_queryset(qs).filter(Q(sign_box_power_usage__gte=1) & Q(industry_id=industry_id) & Q(building_id=building_id))
        else:
            return super(DeviceRoomJson, self).filter_queryset(qs).filter(Q(industry_id=industry_id))


    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        building_id = int(self._querydict.get('id', 0))
        url = self.request.get_full_path()
        industry_id = int(re.findall('(\d+)$', url)[0])
        return self.model.objects.filter(industry_id=industry_id, building_id=building_id)

class EditDeviceRoom(UpdateView):
    '''
    编辑视图
    '''
    form_class = EditDeviceRoomForm
    template_name = 'cabinetmgr/device_room.edit.html'
    model = DeviceRoom

    #获取当前用户参数
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = EditDeviceRoomForm(self.object, None)
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form(data=request.POST, files=request.FILES)
        form.set_user(self.object)

        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    # 数据验证通过后执行
    def form_valid(self, form):
        self.save(form)
        return HttpResponseRedirect(reverse('cabinetmgr:electricbox.list'))

    def save(self, form):
        check_box_power = form.cleaned_data['check_box_power']
        design_box_power = form.cleaned_data['design_box_power']
        sign_box_power = form.cleaned_data['sign_box_power']

        user = self.object
        user.check_box_power = check_box_power
        user.design_box_power = design_box_power
        user.sign_box_power = sign_box_power
        user.sign_box_power_usage = float(user.destribute_box_power)/float(sign_box_power)
        user.save()

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return self.render_to_response(context)
