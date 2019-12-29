#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/9/13 14:16
# @Author  :
# @Site    :
# @File    : views_network_interface_group.py
# @Software: PyCharm5
# @Function:

from django.views.generic import TemplateView
from ..common.datatables.views import BaseDatatableView
from ..vanilla import CreateView, UpdateView
from django.core.exceptions import ImproperlyConfigured
from models import *
from forms import *
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
import json
from constant import get_industry_park

class NetworkInterfaceGroupList(TemplateView):
    template_name = 'zabbixmgr/network_interface_group.list.html'

    def get(self, request, *args, **kwargs):
        us = request.user.username
        industry_park =get_industry_park(us)
        url = self.request.get_full_path()
        industry_id = int(re.findall('(\d+)$', url)[0])
        context = self.get_context_data()
        context['industry_park'] = industry_park
        context['industry_id'] = industry_id
        return self.render_to_response(context)

class NetworkInterfaceGroupJson(BaseDatatableView):
    '''
    Json 数据格式
    '''
    model = NetworkInterfaceGroup
    columns = ['id', 'id','group_name','id']
    order_columns = ['id','id','group_name','id']

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        # return self.model.objects.using('zabbixdb').all()
        return self.model.objects.all()

class CreateNetworkInterfaceGroup(CreateView):

    form_class = CreateNetworkInterfaceGroupForm
    template_name = 'zabbixmgr/networkinterfacegroup.add.html'

    #数据验证通过后执行
    def form_valid(self, form):
        self.save(form)
        return HttpResponseRedirect(reverse('zabbixmgr:networkinterfacegroup.list'))

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    #保存
    def save(self, form):
        networkinterfacegroup = NetworkInterfaceGroup()
        name = form.cleaned_data['name']
        networkinterfacegroup.group_name = name
        networkinterfacegroup.save()

class EditNetworkInterfaceGroup(UpdateView):
    '''
    编辑视图
    '''
    form_class = EditNetworkInterfaceGroupForm
    template_name = 'zabbixmgr/network_interface_group.edit.html'
    model = NetworkInterfaceGroup

    #获取当前用户参数
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = EditNetworkInterfaceGroupForm(self.object, None)
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
        return HttpResponseRedirect(reverse('zabbixmgr:networkinterfacegroup.list'))

    def save(self, form):
        name = form.cleaned_data['name']

        networkinterfacegroup = self.object
        networkinterfacegroup.name = name
        networkinterfacegroup.save()

def delete_networkinterfacegroup(request):
    '''
    批量删除
    :param request:
    :return:
    '''
    json_data = json.loads(request.GET.get('ids'))
    list_id_del = json_data['ids']
    sql = sql1 = Q()
    for id in list_id_del:
        sql = sql | Q(id=id)
    for id in list_id_del:
        sql1 |= Q(type = id)
    if NetworkInterface.objects.filter(sql1):
        name_dict = {'code': '00', 'desc': '不可删除!'}
    else:
        NetworkInterfaceGroup.objects.filter(sql).delete()
        name_dict = {'code': '00', 'desc': '删除成功!'}
    return JsonResponse(name_dict)
