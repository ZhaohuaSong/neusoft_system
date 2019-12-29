#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/3 11:57
# @Author  :
# @Site    :
# @File    : views_clientgroup_port.py
# @Software: PyCharm

from django.views.generic import TemplateView
from models import *
from ..common.datatables.views import BaseDatatableView
from ..vanilla.model_views import CreateView, UpdateView
import json
from django.db.models import Q
from forms import *
import re
from django.http import HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse

class ClientGroupPortList(TemplateView):
    template_name = 'zabbixmgr/clientgroup_port.list.html'

    def get(self, request, *args, **kwargs):
        # networkinterfacegroup = NetworkInterfaceGroup.objects.using('zabbixdb').all()
        clientgroup = ClientGroup.objects.all()
        nodelist = []
        i = 0
        # 从数据字典组成JSON数据给树形控件
        for n in clientgroup:
            dict_obj = {}
            dict_obj['text'] = n.client_name
            dict_obj['id'] = n.id
            dict_obj['tags'] = ['0']
            nodelist.append(dict_obj)
            i += 1

        context = self.get_context_data()
        context['request'] = request
        context['treedata'] = json.dumps(nodelist)
        return self.render_to_response(context)

class ClientGroupPortJson(BaseDatatableView):
    model = SheetsInterface
    columns = ['id', 'id','port_name','ip', 'bandwidth']
    order_columns = ['id', 'id','port_name','ip', 'bandwidth']

    def filter_queryset(self, qs):
        #搜索数据集
        id = self._querydict.get('id')
        search = self._querydict.get('search[value]', None)
        col_data = self.extract_datatables_column_data()

        q = Q()

        for col_no, col in enumerate(col_data):
            if search and col['searchable']:
                q |= Q(**{'{0}__icontains'.format(self.columns[col_no].replace('.', '__')): search})
            if col['search.value']:
                qs = qs.filter(
                    **{'{0}__icontains'.format(self.columns[col_no].replace('.', '__')): col['search.value']})
        qs = qs.filter(q)

        qs = qs.filter(Q(client_id=id))
        return qs

class CreateClientGroupPort(CreateView):
    model = SheetsInterface
    template_name = 'zabbixmgr/clientgroup_port.add.html'
    form_class = CreateGroupclientPortForm

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def form_valid(self, form):
        self.save(form)
        return HttpResponseRedirect(reverse('zabbixmgr:clientgroupport.list'))

    def save(self, form):
        port_name = form.cleaned_data['port_name']
        ip = form.cleaned_data['ip']
        bandwidth = form.cleaned_data['bandwidth']
        client_name = form.cleaned_data['client_name']
        client_id = client_name.id
        host_id = Hosts.objects.using('zabbixdb').get(host=ip).hostid
        in_ite = Items.objects.using('zabbixdb').filter(Q(hostid=host_id)
                                                          & Q(key_field__contains='net.if.in[ifHCInOctets')
                                                          & Q(name__contains='Interface %s'% port_name)
                                                          & Q(flags=4))[0]
        out_ite = Items.objects.using('zabbixdb').filter(Q(hostid=host_id)
                                                      & Q(key_field__contains='net.if.out[ifHCOutOctets')
                                                      & Q(name__contains='Interface %s'% port_name)
                                                      & Q(flags=4))[0]

        SheetsInterface.objects.create(port_name=port_name,
                                      ip=ip,
                                      bandwidth=bandwidth,
                                      client_id=client_id,
                                      table_id=1,
                                      in_itemid=in_ite.itemid,
                                      out_itemid=out_ite.itemid)

class EditClientGroupPort(UpdateView):
    '''
    编辑视图
    '''
    form_class =EditClientGroupPortForm
    template_name = 'zabbixmgr/clientgroup_port.edit.html'
    model = SheetsInterface

    #获取当前用户参数
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = EditClientGroupPortForm(self.object, None)
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
        return HttpResponseRedirect(reverse('cabinetmgr:clientgroupport.list'))

    def save(self, form):
        port_name = form.cleaned_data['port_name']
        ip = form.cleaned_data['ip']
        bandwidth = form.cleaned_data['bandwidth']
        client_name = form.cleaned_data['client_name']
        client_id = client_name.id
        host_id = Hosts.objects.using('zabbixdb').get(host=ip).hostid
        in_ite = Items.objects.using('zabbixdb').filter(Q(hostid=host_id)
                                                          & Q(key_field__contains='net.if.in[ifHCInOctets')
                                                          & Q(name__contains='Interface %s'% port_name)
                                                          & Q(flags=4))[0]
        out_ite = Items.objects.using('zabbixdb').filter(Q(hostid=host_id)
                                                      & Q(key_field__contains='net.if.out[ifHCOutOctets')
                                                      & Q(name__contains='Interface %s'% port_name)
                                                      & Q(flags=4))[0]

        sht = self.object
        sht.port_name = port_name
        sht.ip = ip
        sht.bandwidth = bandwidth
        sht.client_id = client_id
        sht.table_id = 1
        sht.in_itemid = in_ite.itemid
        sht.out_itemid = out_ite.itemid
        sht.save()

def delete_clientgroup_port(request):
    '''
    批量删除
    :param request:
    :return:
    '''
    json_data = json.loads(request.GET.get('ids'))
    id_del = json_data['ids']
    if len(id_del) > 1:
        name_dict = {'code': '00', 'desc': '不可批量删除设备!'}
        return JsonResponse(name_dict)
    else :
        SheetsInterface.objects.filter(id=id_del[0]).delete()
        name_dict = {'code': '00', 'desc': '删除成功!'}
        return JsonResponse(name_dict)

