#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/10/13 14:09
# @Author  :
# @Site    :
# @File    : views_network_device.py
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
import json
from django.db.models import Sum
import os
from subprocess import *
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
import public_id
from ..zabbixmgr.constant import get_industry_park

class NetworkDeviceList(TemplateView):
    template_name = 'cabinetmgr/network_device.list.html'

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("device_id")
        el = Electricbox.objects.get(id=pk)
        us = request.user.username
        industry_park =get_industry_park(us)
        context = self.get_context_data(**kwargs)
        context['industry_park'] = industry_park
        context["device_room"] = el.device_room
        context["box_name"] = el.box_name
        context["pk"] = int(pk)

        last_month = (datetime.date.today().replace(day=1) - datetime.timedelta(days=1)).strftime("%Y-%m")
        timeArray = time.strptime(str(last_month), "%Y-%m")
        timestamp = int(time.mktime(timeArray))
        try:
            level = HistoryPower.objects.get(industry_id=1, building_id=1,clock=timestamp, boxid=int(pk)).level
        except:
            level=1
        context['level'] = level

        url = request.get_full_path()
        deviceid = int(re.findall('(\d+)$', url)[0])
        self.deviceid = deviceid
        us = request.user.username
        public_id.rq = request
        public_id.di[us] = self.deviceid
        return self.render_to_response(context)

class NetworkDeviceJosn(BaseDatatableView):
    model = NetworkDevice
    columns = ['id',
               'id',
               'on_state_date',
               'power_on_date',
               # 'down_power_date',
               'device_num',
               'start_u_num',
               'end_u_num',
               'total_u_num',
               'device_code',
               'device_type',
               'device_status',
               'power_num',
               'device_alternating',
               'device_threshold_rt']
    order_columns = columns

    def get_json(self, response):
        data_list = response['data']
        for data in data_list:
            if isinstance(data[2], datetime.datetime):
                data[2]=data[2].strftime("%Y-%m-%d")
            if isinstance(data[3], datetime.datetime):
                data[3]=data[3].strftime("%Y-%m-%d")
            if isinstance(data[4], datetime.datetime):
                data[4]=data[4].strftime("%Y-%m-%d")
        return super(NetworkDeviceJosn, self).get_json(response)

    def get_initial_queryset(self):
        us_name = self.request.user.username
        deviceid = public_id.di[us_name]
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return self.model.objects.filter(box_id=deviceid)

class CreateNetworkDevice(CreateView):
    model = NetworkDevice
    template_name = 'cabinetmgr/network_device.add.html'
    form_class = CreateNetworkDeviceForm

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def form_valid(self, form):
        self.save(form)
        us_name = self.request.user.username
        box_id = public_id.di[us_name]
        return HttpResponseRedirect('/cabinetmgr/networkdevice/list/' + str(box_id))

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def update_table_electricbox(self, form):
        '''
        更新表electricbox
        :return:
        '''
        us_name = self.request.user.username
        box_id = public_id.di[us_name]
        if Electricbox.objects.get(industry_id=1, building_id=1, id=box_id).on_state_date == None:
            on_state_date = form.cleaned_data['on_state_date']
            power_on_date = form.cleaned_data['power_on_date']
            device_num = form.cleaned_data['device_num']
            start_u_num = form.cleaned_data['start_u_num']
            end_u_num = form.cleaned_data['end_u_num']
            total_u_num = end_u_num - start_u_num + 1
            box_type = 40
            Electricbox.objects.filter(id=box_id).update(on_state_date=on_state_date,
                                                         power_on_date=power_on_date,
                                                         device_num=device_num,
                                                         device_u_num=total_u_num,
                                                         box_type=box_type)
        else:
            device_num = form.cleaned_data['device_num']
            start_u_num = form.cleaned_data['start_u_num']
            end_u_num = form.cleaned_data['end_u_num']
            total_u_num = end_u_num - start_u_num + 1
            el = Electricbox.objects.get(industry_id=1, building_id=1,id=box_id)
            Electricbox.objects.filter(industry_id=1, building_id=1,id=box_id).update(device_num=device_num+el.device_num,device_u_num=el.device_u_num+total_u_num)

    def save(self, form):
        us_name = self.request.user.username
        box_id = public_id.di[us_name]
        on_state_date = form.cleaned_data['on_state_date']
        power_on_date = form.cleaned_data['power_on_date']
        start_u_num = form.cleaned_data['start_u_num']
        end_u_num = form.cleaned_data['end_u_num']
        total_u_num = end_u_num - start_u_num + 1
        device_code = form.cleaned_data['device_code']
        device_type = form.cleaned_data['device_type']
        device_status = str(form.cleaned_data['device_status'].box_type)
        power_num = str(form.cleaned_data['power_num'].box_type)
        device_alternating = form.cleaned_data['device_alternating']
        device_threshold_rt = form.cleaned_data['device_threshold_rt']
        device_num = form.cleaned_data['device_num']
        NetworkDevice.objects.create(box_id=box_id,
                                     room_id=1,#有误
                                     building_id=1,
                                     industry_id=1,
                                     on_state_date=on_state_date,
                                   power_on_date=power_on_date,
                                   start_u_num=start_u_num,
                                   end_u_num=end_u_num,
                                   total_u_num=total_u_num,
                                   device_code=device_code,
                                   device_type=device_type,
                                   device_status=device_status,
                                   power_num=power_num,
                                   device_alternating=device_alternating,
                                   device_threshold_rt=device_threshold_rt,
                                   device_num=device_num)

        self.update_table_electricbox(form)

class EditNetworkDevice(UpdateView):
    form_class = EditNetworkDeviceForm
    template_name = 'cabinetmgr/network_device.edit.html'
    model = NetworkDevice

    #获取当前用户参数
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = EditNetworkDeviceForm(self.object, None)
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
        us_name = self.request.user.username
        box_id = public_id.di[us_name]
        return HttpResponseRedirect('/cabinetmgr/networkdevice/list/' + str(box_id))

    def save(self, form):
        on_state_date = form.cleaned_data['on_state_date']
        power_on_date = form.cleaned_data['power_on_date']
        start_u_num = form.cleaned_data['start_u_num']
        end_u_num = form.cleaned_data['end_u_num']
        total_u_num = end_u_num - start_u_num + 1
        device_code = form.cleaned_data['device_code']
        device_type = form.cleaned_data['device_type']
        device_status = str(form.cleaned_data['device_status'].box_type)
        power_num = str(form.cleaned_data['power_num'].box_type)
        device_alternating = form.cleaned_data['device_alternating']
        device_threshold_rt = form.cleaned_data['device_threshold_rt']
        device_num = form.cleaned_data['device_num']

        user = self.object
        user.on_state_date = on_state_date
        user.power_on_date = power_on_date
        user.start_u_num = start_u_num
        user.end_u_num = end_u_num
        user.total_u_num = total_u_num
        user.device_code = device_code
        user.device_code = device_code
        user.device_type = device_type
        user.device_status = device_status
        user.power_num = power_num
        user.device_alternating = device_alternating
        user.device_threshold_rt = device_threshold_rt
        user.device_num = device_num
        user.save()

        us_name = self.request.user.username
        box_id = public_id.di[us_name]
        device_num = form.cleaned_data['device_num']
        start_u_num = form.cleaned_data['start_u_num']
        end_u_num = form.cleaned_data['end_u_num']
        total_u_num = end_u_num - start_u_num + 1
        el = Electricbox.objects.get(id=box_id)
        Electricbox.objects.filter(id=box_id).update(device_num=device_num+el.device_num,device_u_num=el.device_u_num+total_u_num)

def networkdevice_batches_delete(request):
    '''
    不允许批量删除
    :param request:
    :return:
    '''
    json_data = json.loads(request.GET.get('ids'))
    id_del = json_data['ids']
    if len(id_del) > 1:
        name_dict = {'code': '00', 'desc': '不可批量删除设备!'}
        return JsonResponse(name_dict)
    else:
        ndv = NetworkDevice.objects.get(id=id_del[0])
        con_id = ndv.box_id
        device_num = ndv.device_num
        total_u_num = ndv.total_u_num
        el = Electricbox.objects.get(id=con_id)
        if el.device_num-device_num == 0:
            Electricbox.objects.filter(id=con_id).update(down_power_date=datetime.datetime.now(),
                                                         device_num=el.device_num-device_num,
                                                         device_u_num=el.device_u_num-total_u_num)
        else:
            Electricbox.objects.filter(id=con_id).update(
                                                         device_num=el.device_num-device_num,
                                                         device_u_num=el.device_u_num-total_u_num)
        NetworkDevice.objects.filter(id=id_del[0]).delete()
        name_dict = {'code': '00', 'desc': '删除成功!'}
        return JsonResponse(name_dict)
