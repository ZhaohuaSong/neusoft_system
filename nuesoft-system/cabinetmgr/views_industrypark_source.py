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

class IndustryParkSourceList(TemplateView):
    template_name = 'cabinetmgr/industrypark_source.list.html'

    def get(self, request, *args, **kwargs):
        us = request.user.username
        industry_park =get_industry_park(us)
        url = self.request.get_full_path()
        industry_id = int(re.findall('(\d+)$', url)[0])
        if IndustryPark.objects.get(industry_id=industry_id).usage_box > 0.8:
            bg_color = 'FF0000'
        else:
            bg_color = '#FFFFFF'
        context = self.get_context_data(**kwargs)
        context['bg_color'] = bg_color


        context['industry_id'] = industry_id
        context['industry_park'] = industry_park
        return self.render_to_response(context)

class IndustryParkSourceJson(BaseDatatableView):
    '''
    Json 数据格式
    '''
    model = IndustryPark
    columns = ['id', 'id', 'park', 'type', 'attribute', 'electric_cap', 'power', 'usage_power', 'total_box', 'built', 'activate', 'unactivate', 'usage_box']
    order_columns = columns

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        url = self.request.path
        industry_id = int(re.findall('(\d+)$', url)[0])
        return self.model.objects.filter(industry_id=industry_id)

class CreateIndustryParkSource(CreateView):

    form_class = CreateIndustryParkSourceForm
    template_name = 'cabinetmgr/industrypark_source.add.html'

    #数据验证通过后执行
    def form_valid(self, form):
        self.save(form)
        return HttpResponseRedirect(reverse('cabinetmgr:industryparksource.list'))

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    #保存
    def save(self, form):
        industry_park = IndustryPark()
        park = form.cleaned_data['park']
        type = form.cleaned_data['type']
        attribute = form.cleaned_data['attribute']
        electric_cap = form.cleaned_data['electric_cap']
        power = form.cleaned_data['power']
        # usage_power = power/electric_cap
        # unactivate = industry_park.built - industry_park.activate
        total_box = form.cleaned_data['total_box']
        industry_park.building = park
        industry_park.type = type

        industry_park.attribute = attribute
        industry_park.electric_cap = electric_cap
        industry_park.power = power
        # industry_park.usage_power = usage_power
        # industry_park.unactivate = unactivate
        industry_park.total_box = total_box
        industry_park.save()

class EditIndustryParkSource(UpdateView):
    '''
    编辑视图
    '''
    form_class = EditIndustryParkSourceForm
    template_name = 'cabinetmgr/industrypark_source.edit.html'
    model = IndustryPark

    #获取当前用户参数
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = EditIndustryParkSourceForm(self.object, None)
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form(data=request.POST, files=request.FILES)
        form.set_user(self.object)

        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    #数据验证通过后执行
    def form_valid(self, form):
        self.save(form)
        return HttpResponseRedirect(reverse('cabinetmgr:industryparksource.list'))

    def save(self, form):
        park = form.cleaned_data['park']
        type = form.cleaned_data['type']
        attribute = form.cleaned_data['attribute']
        electric_cap = form.cleaned_data['electric_cap']
        power = form.cleaned_data['power']
        total_box = form.cleaned_data['total_box']

        industry_park = self.object
        industry_park.building = park
        industry_park.type = type
        industry_park.attribute = attribute
        industry_park.electric_cap = electric_cap
        industry_park.power = power
        industry_park.total_box = total_box

        industry_park.save()

def delete_industryparksource(request):
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
    # for id in list_id_del:
    #     sql1 |= Q(type = id)
    # if NetworkInterface.objects.filter(sql1):
    #     name_dict = {'code': '00', 'desc': '不可删除!'}
    # else:
    #     NetworkInterfaceGroup.objects.filter(sql).delete()
    #     name_dict = {'code': '00', 'desc': '删除成功!'}
    IndustryPark.objects.filter(sql).delete()
    name_dict = {'code': '00', 'desc': '删除成功!'}
    return JsonResponse(name_dict)
