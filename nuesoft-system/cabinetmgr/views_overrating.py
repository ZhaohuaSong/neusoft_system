#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/9/12 11:23
# @Author  :
# @Site    :
# @File    : views_overrating.py
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


value_list = []

class OverRatingList(TemplateView):
    template_name = 'cabinetmgr/overrating.list.html'
    def get_context_data(self, **kwargs):

        context = super(OverRatingList, self).get_context_data(**kwargs)
        power_list = ['安全范围值', '超阀值', '超额定值']
        nodelist = []
        no = []
        i = 1
        for l in power_list:
            dict_obj = {}
            dict_obj['text'] = l
            dict_obj['id'] = i
            dict_obj['tags'] = ['0']
            nodelist.append(dict_obj)
            no.append(l)
            i += 1
        url = self.request.get_full_path()
        industry_id = int(re.findall('(\d+)$', url)[0])
        context['no'] = no
        context['treedata'] = json.dumps(nodelist)
        context['client_id'] = json.dumps(list(ElectricboxClient.objects.filter(industry_id=industry_id).values_list('id', flat=True)))
        context['client_name'] = json.dumps(list(ElectricboxClient.objects.filter(industry_id=industry_id).values_list('client_name', flat=True)))
        building_id = list(IDCBuilding.objects.filter(park_id=int(industry_id)).values_list('building_id', flat=True))
        building_name = list(IDCBuilding.objects.filter(park_id=int(industry_id)).values_list('building_name', flat=True))
        context['building_id'] = json.dumps(building_id)
        context['building_name'] = json.dumps(building_name)
        building_room_dict = {}
        for bd in building_id:
            building_room_dict[str(bd)] = list(BuildingRoom.objects.filter(industry_id=industry_id, building_id=bd).values_list('id', 'room_name'))
        context['building_room_dict'] = json.dumps(building_room_dict)
        return context

    def get(self, request, *args, **kwargs):
        us = request.user.username
        industry_park =get_industry_park(us)
        context = self.get_context_data(**kwargs)
        url = self.request.get_full_path()
        industry_id = int(re.findall('(\d+)$', url)[0])
        context['industry_id'] = industry_id
        context['industry_park'] = industry_park
        return self.render_to_response(context)

class OverRatingJson(BaseDatatableView):
    '''
    Json 数据格式
    '''
    model = HistoryPower
    columns = ['id', 'id', 'device_room', 'box_name', 'client_name', 'threshold_rating', 'power_rating', 'avg_power_rating', 'month']
    order_columns = ['id', 'id', 'device_room', 'box_name', 'client_name', 'threshold_rating', 'power_rating', 'avg_power_rating', 'month']

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        url = self.request.path
        industry_id = int(re.findall('(\d+)$', url)[0])
        return self.model.objects.filter(industry_id=industry_id)

    def get_json(self, response):
        data_list = response['data']
        for data in data_list:
            if ',' not in data[4]:
                try:
                    data[4]=ElectricboxClient.objects.get(id=data[4]).client_name
                except:
                    pass
            else:
                data[4]='多客户'
        return super(OverRatingJson, self).get_json(response)

    def filter_queryset(self, qs):
        #搜索数据集
        url = self.request.path
        industry_id = int(re.findall('(\d+)', url)[0])
        self.pre_industry_id = industry_id
        id = self._querydict.get('id', 0)
        global value_list
        search = self._querydict.get('search[value]', None)
        print search

        if search:
            value = search
            value_list = value.split()

        if not value_list:
            sh = str(datetime.datetime.now().year) + '-' + str(datetime.datetime.now().month)
            electricbox_id = []
            self.pre_building_id = None
        else:
            if value_list[1] == 'client' and value_list[2] != 'room':
                sh = value_list[0]
                room_id = value_list[2]
                building_id = value_list[3]
                electricbox_id = list(Electricbox.objects.filter(industry_id=industry_id, building_id=building_id, room_id=room_id).values_list('id', flat=True))
                self.pre_building_id = building_id
            elif value_list[1] == 'client' and value_list[2] == 'room':
                sh = value_list[0]
                building_id = value_list[3]
                electricbox_id = list(Electricbox.objects.filter(industry_id=industry_id, building_id=building_id).values_list('id', flat=True))
                self.pre_building_id = building_id
            else:
                sh = value_list[0]
                client_id = value_list[1]
                building_id = value_list[3]
                electricbox_id = list(Electricbox.objects.filter(industry_id=industry_id, building_id=building_id, client_name=client_id).values_list('id', flat=True))
                self.pre_building_id = building_id
        sql = Q()
        for el_id in electricbox_id:
            sql |= Q(boxid=el_id)

        timeArray = time.strptime(sh, "%Y-%m")
        timeStamp = int(time.mktime(timeArray))

        q = Q()
        q |= Q(**{'{0}__icontains'.format('clock'.replace('.', '__')): timeStamp})
        qs = qs.filter(Q(level=id) & q & sql & Q(industry_id=industry_id))
        return qs

    def prepare_results(self, qs):
        data = []
        el = Electricbox.objects.filter(industry_id=self.pre_industry_id ,building_id=self.pre_building_id)
        for item in qs:
            timeArray = time.localtime(item.clock)
            otherStyleTime = time.strftime("%Y-%m", timeArray)
            data.append([item.boxid,
                         item.boxid,
                         el.get(id=item.boxid).device_room,
                         el.get(id=item.boxid).box_name,
                         el.get(id=item.boxid).client_name,
                         el.get(id=item.boxid).threshold_rating,
                         el.get(id=item.boxid).power_rating,
                         item.value,
                         otherStyleTime])
        return data
