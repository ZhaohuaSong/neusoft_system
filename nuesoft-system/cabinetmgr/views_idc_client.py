#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/11/6 17:24
# @Author  :
# @Site    :
# @File    : views_clientinterfacemgr.py
# @Software: PyCharm

from django.views.generic import TemplateView
from ..common.datatables.views import BaseDatatableView
from models import *
from forms import *
from django.http import HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse
from ..vanilla.model_views import *
import json
from ..zabbixmgr.constant import get_industry_park

class IDCClientList(TemplateView):
    template_name = 'cabinetmgr/idc_client.list.html'

    def get(self, request, *args, **kwargs):
        url = self.request.get_full_path()
        industry_id = int(re.findall('(\d+)$', url)[0])
        us = request.user.username
        industry_park =get_industry_park(us)
        context = self.get_context_data(**kwargs)

        context['industry_id'] = industry_id
        context['industry_park'] = industry_park
        return self.render_to_response(context)
    # crk = ContractRack.objects.all()[0]
    # import time
    # timeArray = time.strptime(str(crk.power_up_time), "%Y-%m-%d %H:%M:%S")
    # otherStyleTime = time.strftime("%Y-%m-%d", timeArray)
    # print otherStyleTime

class IDCClientJson(BaseDatatableView):
    model = ElectricboxClient
    columns = ['id', 'id','client_name','id']
    order_columns = ['id','id','client_name','id']



    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        url = self.request.path
        industry_id = int(re.findall('(\d+)$', url)[0])
        return self.model.objects.filter(industry_id=industry_id)

class CreateIDCClient(CreateView):

    form_class = CreateIDCClientForm
    template_name = 'cabinetmgr/idc_client.add.html'

    def get(self, request, *args, **kwargs):
        url = self.request.get_full_path()
        industry_id = int(re.findall('(\d+)$', url)[0])
        us = request.user.username
        industry_park =get_industry_park(us)
        form = self.get_form()
        context = self.get_context_data(form=form)
        context['industry_id'] = industry_id
        context['industry_park'] = industry_park
        return self.render_to_response(context)

    #数据验证通过后执行
    def form_valid(self, form):
        self.save(form)
        url = self.request.path
        industry_id = int(re.findall('(\d+)$', url)[0])
        return HttpResponseRedirect('/cabinetmgr/idcclient/list/'  + str(industry_id))

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = self.get_form(data=request.POST, files=request.FILES)
        url = self.request.path
        industry_id = int(re.findall('(\d+)$', url)[0])
        form.get_industry_id(industry_id)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    #保存
    def save(self, form):
        url = self.request.path
        industry_id = int(re.findall('(\d+)$', url)[0])
        clientgroup = ElectricboxClient()
        client_name = form.cleaned_data['client_name']
        clientgroup.client_name = client_name
        clientgroup.industry_id = industry_id
        clientgroup.save()

class EditIDCClient(UpdateView):
    '''
    编辑视图
    '''
    form_class = EditIDCClientForm
    template_name = 'cabinetmgr/idcclient.edit.html'
    model = ElectricboxClient
    industry_id = None

    #获取当前用户参数
    def get(self, request, *args, **kwargs):
        url = self.request.get_full_path()
        self.industry_id = int(re.findall('(\d+)$', url)[0])
        us = request.user.username
        industry_park =get_industry_park(us)


        self.object = self.get_object()
        form = EditIDCClientForm(self.object, None)
        context = self.get_context_data(form=form)
        context['industry_id'] = self.industry_id
        context['industry_park'] = industry_park
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form(data=request.POST, files=request.FILES)
        form.set_user(self.object)
        form.get_industry_id(self.industry_id)

        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    # 数据验证通过后执行
    def form_valid(self, form):
        self.save(form)
        url = self.request.get_full_path()
        self.industry_id = int(re.findall('(\d+)$', url)[0])
        return HttpResponseRedirect('/cabinetmgr/idcclient/list/'  + str(self.industry_id))

    def save(self, form):
        client_name = form.cleaned_data['client_name']

        user = self.object
        user.client_name = client_name
        user.save()

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

def delete_idc_client(request):
    json_data = json.loads(request.GET.get('ids'))
    id_del = json_data['ids']
    for i in id_del:
        if IpAddress.objects.filter(client_id=i).exists() or Electricbox.objects.filter(client_name=str(i)).exists():
            name_dict = {'code': '00', 'desc': '回退失败!'}
            return JsonResponse(name_dict)
    sql = Q()
    for i in id_del:
        sql |= Q(id=i)
    ElectricboxClient.objects.filter(sql).values_list('id', flat=True)
    name_dict = {'code': '00', 'desc': '回退成功!'}
    return JsonResponse(name_dict)
