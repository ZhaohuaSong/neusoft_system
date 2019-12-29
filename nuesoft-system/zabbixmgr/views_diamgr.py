#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/17 14:24
# @Author  :
# @Site    :
# @File    : views_diamgr.py
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
import os
from subprocess import *
from constant import get_industry_park

class DeviceDialingList(TemplateView):
    template_name = 'dialing/devicedialing.list.html'

    def get(self, request, *args, **kwargs):
        us = request.user.username
        industry_park =get_industry_park(us)
        context = self.get_context_data()
        url = self.request.get_full_path()
        industry_id = int(re.findall('(\d+)$', url)[0])
        context['industry_park'] = industry_park
        context['industry_id'] = industry_id
        return self.render_to_response(context)

class DeviceDialingJson(BaseDatatableView):
    '''
    Json 数据格式
    '''
    model = DialingIp
    columns = ['id', 'id','ip','id']
    order_columns = ['id','id','ip','id']

class CreateDeviceDialing(CreateView):
    model = DialingIp
    template_name = 'dialing/devicedialing.add.html'
    form_class = CreateDeviceDialingForm

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def form_valid(self, form):
        self.save(form)
        return HttpResponseRedirect(reverse('dialing:devicedialing.list'))

    def save(self, form):
        ip = form.cleaned_data['ip']
        DialingIp.objects.create(ip=ip)

class EditDeviceDialing(UpdateView):
    '''
    编辑视图
    '''
    form_class = EditDeviceDialingForm
    template_name = 'dialing/devicedialing.edit.html'
    model = DialingIp

    #获取当前用户参数
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = EditDeviceDialingForm(self.object, None)
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
        return HttpResponseRedirect(reverse('dialing:devicedialing.list'))

    def save(self, form):
        ip = form.cleaned_data['ip']
        user = self.object
        user.ip = ip
        user.save()

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

def delete_devicedialing(request):
    '''
    批量删除
    :param request:
    :return:
    '''
    json_data = json.loads(request.GET.get('ids'))
    list_id_del = json_data['ids']
    sql = Q()
    for id in list_id_del:
        sql = sql | Q(id=id)
    DialingIp.objects.filter(sql).delete()
    name_dict = {'code': '00', 'desc': '删除成功!'}
    return JsonResponse(name_dict)

class DialingTest(TemplateView):
    template_name = 'dialing/autoping.list.html'

    def autoping(self, ip):
        p = Popen('ping %s' % ip,
          stdout=PIPE,
          stderr=PIPE,
          shell=True
          )
        p.wait()
        out = p.stdout.read()
        l = out.split('\n')
        li = {}
        for i in range(len(l)):
            li[str(i)] = l[i].decode('gbk')
        return li

    def get(self, request, *args, **kwargs):
        us = request.user.username
        industry_park =get_industry_park(us)
        context = self.get_context_data()
        context['industry_park'] = industry_park

        url = request.get_full_path()
        id = int(re.findall('(\d+)$', url)[0])
        ip = DialingIp.objects.get(id=id).ip
        context['con'] = self.autoping(ip)
        return self.render_to_response(context)
