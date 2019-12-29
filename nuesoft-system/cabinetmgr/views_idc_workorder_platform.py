#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/10/25 15:51
# @Author  :
# @Site    :
# @File    : views_idc_workorder_platform.py
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
from ..zabbixmgr.constant import get_industry_park
import public_id

class IDCWorkorderPlatformList(TemplateView):
    template_name = 'cabinetmgr/idc_workorder_platform.list.html'

    def get(self, request, *args, **kwargs):
        user = request.user.username
        industry_park = get_industry_park(user)
        context = self.get_context_data()
        url = self.request.path
        industry_id = int(re.findall('(\d+)$', url)[0])
        context['industry_id'] = industry_id
        context['industry_park'] = industry_park
        return self.render_to_response(context)

class IDCWorkorderPlatformJson(BaseDatatableView):
    model = IDCWorkorderPlatform

    columns = ['id',
               'id',
               'workorder_name',
               'client_name',
               'operate_ip',
               'operate_elbox',
               'operate_device',
               'operate_interface',
               'create_time',
               'operate_record',
               'submit',
               'workorder_status'
               ]
    order_columns = columns

    def get_initial_queryset(self):
        url = self.request.path
        industry_id = int(re.findall('(\d+)$', url)[0])
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        username = self.request.user.username
        return self.model.objects.filter(industry_id=industry_id, create_user=username)

    def get_json(self, response):
        data_list = response['data']
        for data in data_list:
            if isinstance(data[8], datetime.datetime):
                data[8]=data[8].strftime("%Y-%m-%d")
        return super(IDCWorkorderPlatformJson, self).get_json(response)

class CreateIDCWorkorderPlatform(CreateView):
    model = IDCWorkorderPlatform
    template_name = 'cabinetmgr/idc_workorder_platform.add.html'
    form_class = IDCWorkorderPlatformForm

    def get(self, request, *args, **kwargs):
        # public_id.rq = request
        form = self.get_form()
        url = self.request.path
        industry_id = int(re.findall('(\d+)$', url)[0])
        elc = ElectricboxClient.objects.filter(industry_id=industry_id)
        client_list = []
        for el in elc:
            client_list.append([el.id, el.client_name])
        context = self.get_context_data(form=form)
        user = request.user.username
        industry_park = get_industry_park(user)
        context['industry_park'] = industry_park
        context['client'] = client_list

        return self.render_to_response(context)

    def form_valid(self, form):
        self.save(form)
        url = self.request.path
        industry_id = int(re.findall('(\d+)$', url)[0])
        return HttpResponseRedirect('/cabinetmgr/idcworkorderplatform/list/'+str(industry_id))

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def save(self, form):
        workorder_name = form.cleaned_data['workorder_name']
        client_name = form.cleaned_data['client_name']
        operate_ip = form.cleaned_data['operate_ip']
        operate_elbox = form.cleaned_data['operate_elbox']
        operate_device = form.cleaned_data['operate_device']
        operate_interface = form.cleaned_data['operate_interface']
        if operate_ip is None:
            operate_ip = 0
        else:
            operate_ip = 1
        if operate_elbox is None:
            operate_elbox = 0
        else:
            operate_elbox = 1
        if operate_device is None:
            operate_device = 0
        else:
            operate_device = 1
        if operate_interface is None:
            operate_interface = 0
        else:
            operate_interface = 1
        operate_record = form.cleaned_data['operate_record']
        user_name = self.request.user.username
        url = self.request.path
        industry_id = int(re.findall('(\d+)$', url)[0])

        IDCWorkorderPlatform.objects.create(
                                     industry_id=industry_id,
                                     workorder_name=workorder_name,
                                   client_name=client_name,
                                   operate_ip=operate_ip,
                                   operate_elbox=operate_elbox,
                                    operate_device=operate_device,
                                    operate_interface=operate_interface,
                                   workorder_status=0,
                                   operate_record=operate_record,
                                    create_time=datetime.datetime.now(),
                                    create_user=user_name,
                                    submit=0)

def idc_workorder_delete(request):
    json_data = json.loads(request.GET.get('ids'))
    id_del = json_data['ids']
    sql = Q()
    for i in id_del:
        sql |= Q(id=i)
    IDCWorkorderPlatform.objects.filter(sql).delete()
    name_dict = {'code': '00', 'desc': '删除成功!'}
    return JsonResponse(name_dict)

def configer_workorder(request):
    '''
    提交工单
    :param request:
    :return:
    '''
    url = request.get_full_path()
    id_list = re.findall('(\d+)\/(\d+)$', url)[0]
    id = int(id_list[0])
    iwp = IDCWorkorderPlatform.objects.get(id=int(id))
    operate_ip = iwp.operate_ip
    operate_elbox = iwp.operate_elbox
    operate_device = iwp.operate_device
    operate_interface = iwp.operate_interface
    if operate_ip == 3:
        operate_ip = 1
    if operate_elbox == 3:
        operate_elbox = 1
    if operate_device == 3:
        operate_device = 1
    if operate_interface == 3:
        operate_interface = 1
    IDCWorkorderPlatform.objects.filter(id=int(id)).update(operate_ip=operate_ip,
                                                           operate_elbox=operate_elbox,
                                                           operate_device=operate_device,
                                                           operate_interface=operate_interface,
                                                           submit=1,
                                                           workorder_status=0)
    return HttpResponseRedirect('/cabinetmgr/idcworkorderplatform/list/'+str(id_list[1]))
