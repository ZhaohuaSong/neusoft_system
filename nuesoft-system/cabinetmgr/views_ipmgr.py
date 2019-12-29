#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    :
# @Author  : ljh
# @Site    :
# @File    : views_ipmgr.py
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

class IPmgrList(TemplateView):
    template_name = 'cabinetmgr/ipmgr.list.html'

    def get(self, request, *args, **kwargs):
        url = self.request.get_full_path()
        industry_id = int(re.findall('(\d+)$', url)[0])
        us = request.user.username
        industry_park =get_industry_park(us)
        context = self.get_context_data(**kwargs)

        context['industry_id'] = industry_id
        context['industry_park'] = industry_park
        return self.render_to_response(context)

class IPmgrJson(BaseDatatableView):
    model = IpLibrary
    columns = ['id', 'id','all_ip','industry_id']
    order_columns = ['id','id','all_ip','industry_id']

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        url = self.request.path
        industry_id = int(re.findall('(\d+)$', url)[0])
        return self.model.objects.filter(industry_id=industry_id)

    def prepare_results(self, qs):
            data = []
            all_ip = json.loads(qs[0].all_ip)
            industry_id = qs[0].industry_id
            industry = IndustryPark.objects.get(id=industry_id).park
            for i in range(len(all_ip)):
                data.append([i, i, all_ip[i], industry])
            return data

class IPmgrCreate(CreateView):
    form_class = CreateIPmgrForm
    template_name = 'cabinetmgr/ipmgr.add.html'

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
        return HttpResponseRedirect('/cabinetmgr/ipmgr/list/'  + str(industry_id))

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
        iplibrary = IpLibrary()
        industry_ip = form.cleaned_data['industry_ip']
        handle = form.cleaned_data['handle']

        instance = Split([industry_ip]) #must be list
        upload_ip_list = instance.getIpList() #is num list
        ip_library = json.loads(IpLibrary.objects.get(industry_id=industry_id).all_ip)
        local_ip = Split(ip_library)
        local_ip_list = local_ip.getIpList()
        if int(handle) == 1 and IpLibrary.objects.filter(industry_id=industry_id).exists():
            ip_list = upload_ip_list + local_ip_list
            ip_list.sort()
            ip_list = local_ip.ipListToPack(ip_list)

            IpLibrary.objects.filter(industry_id=industry_id).update(all_ip=json.dumps(ip_list))
        elif int(handle) == 1 and not IpLibrary.objects.filter(industry_id=industry_id).exists():
            iplibrary.all_ip = json.dumps(industry_ip)
            iplibrary.industry_id = industry_id
            iplibrary.save()

        elif int(handle) == 0:
            ip_list = list(set(local_ip_list) - set(upload_ip_list))
            ip_list.sort()
            ip_list = local_ip.ipListToPack(ip_list)
            IpLibrary.objects.filter(industry_id=industry_id).update(all_ip=json.dumps(ip_list))
