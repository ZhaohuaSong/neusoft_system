#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/9/7 15:32
# @Author  :
# @Site    :
# @File    : views_threshold.py
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

class ThresholdList(TemplateView):
    template_name = 'cabinetmgr/threshold.list.html'

class ThresholdJson(BaseDatatableView):
    '''
    Json 数据格式
    '''
    model = Threshold
    columns = ['id', 'id', 'threshold']
    order_columns = ['id','id', 'threshold']

class CreateThreshold(CreateView):
    model = Threshold
    template_name = 'cabinetmgr/threshold.add.html'
    form_class = CreateThresholdForm

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def form_valid(self, form):
        self.save(form)
        return HttpResponseRedirect(reverse('cabinetmgr:threshold.list'))

    def save(self, form):
        threshold = form.cleaned_data['threshold']
        tab_id = Threshold.objects.all().reverse()[0].tab_id
        Threshold.objects.create(threshold=threshold,tab_id=tab_id+1)

class EditThreshold(UpdateView):
    '''
    编辑视图
    '''
    form_class = EditThresholdForm
    template_name = 'cabinetmgr/threshold.edit.html'
    model = Threshold

    #获取当前用户参数
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = EditThresholdForm(self.object, None)
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
        return HttpResponseRedirect(reverse('cabinetmgr:threshold.list'))

    def save(self, form):
        threshold = form.cleaned_data['threshold']
        user = self.object
        user.threshold = threshold
        user.save()

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

def delete_threshold(request):
    '''
    批量删除
    :param request:
    :return:
    '''
    json_data = json.loads(request.GET.get('ids'))
    list_id_del = json_data['ids']
    if len(list_id_del) == 1:
        id = Threshold.objects.all().reverse()[0].id
        if id == list_id_del[0]:
            Threshold.objects.filter(id=id).delete()
            name_dict = {'code': '00', 'desc': '删除成功!'}
            return JsonResponse(name_dict)
    else:
        name_dict = {'code': '00', 'desc': '只能删除最后一个!'}
        return JsonResponse(name_dict)
