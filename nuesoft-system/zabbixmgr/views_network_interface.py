#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/9/14 14:49
# @Author  :
# @Site    :
# @File    : views_network_interface.py
# @Software: PyCharm5
# @Function:

from django.views.generic import TemplateView
from models import *
from ..common.datatables.views import BaseDatatableView
from ..vanilla.model_views import CreateView
import json
from django.db.models import Q
from forms import CreateNetworkInterfaceForm
import re
from django.http import HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse
from constant import get_industry_park

class NetworkInterfaceList(TemplateView):
    template_name = 'zabbixmgr/network_interface.list.html'

    def get(self, request, *args, **kwargs):

        us = request.user.username
        industry_park =get_industry_park(us)
        url = self.request.get_full_path()
        industry_id = int(re.findall('(\d+)$', url)[0])
        # networkinterfacegroup = NetworkInterfaceGroup.objects.using('zabbixdb').all()
        networkinterfacegroup = NetworkInterfaceGroup.objects.all()
        nodelist = []
        i = 0
        # 从数据字典组成JSON数据给树形控件
        for n in networkinterfacegroup:
            dict_obj = {}
            dict_obj['text'] = n.group_name
            dict_obj['id'] = n.id
            dict_obj['tags'] = ['0']
            nodelist.append(dict_obj)
            i += 1

        context = self.get_context_data()
        context['request'] = request
        context['treedata'] = json.dumps(nodelist)
        context['industry_park'] = industry_park
        context['industry_id'] = industry_id
        return self.render_to_response(context)

class NetworkInterfaceJson(BaseDatatableView):
    '''
    Josn data
    '''
    model = NetworkInterface
    columns = ['id', 'id','role_name','ip', 'inter_name']
    order_columns = ['id', 'id','role_name','ip', 'inter_name']

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        # return self.model.objects.using('zabbixdb').all()
        return self.model.objects.all()

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

        #1、在用户列表中屏蔽掉自己
        qs = qs.filter(Q(type=id))
        return qs

def set_allnetworkinterface_db(request):
    '''
    更新网络端口
    :return:
    '''
    # AllNetworkInterface.objects.all().delete()
    list_ip = []
    list_host = []
    list_host_id = []
    q = Q()
    # q |= Q(ip = '188.1.184.1')
    # q |= Q(ip = '188.1.184.2')
    # q |= Q(ip = '188.1.184.3')
    # q |= Q(ip = '188.1.184.4')
    for i in Interface.objects.using('zabbixdb').filter(q):
        if i.hostid.status == 0:
            list_ip.append(i.ip)
            list_host_id.append(i.hostid.hostid)
            list_host.append(i.hostid.host)
    for i in range(len(list_ip)):
        all_interface = Items.objects.using('zabbixdb').filter(Q(hostid=list_host_id[i]) & Q(key_field__contains='net.if.in[ifHCInOctets') & Q(flags=4))
        outgoing_interface = Items.objects.using('zabbixdb').filter(Q(hostid=list_host_id[i]) & Q(key_field__contains='net.if.out[ifHCOutOctets') & Q(flags=4))
        j = 0
        for al in all_interface:
            inter = ''
            # if re.findall('\w+\s(\w+\d+\/\d+\/\d+).*', al.name):
            #     inter = re.findall('\w+\s(\w+\d+\/\d+\/\d+).*', al.name)
            # else:
            #     inter = re.findall('\w+\s(Eth\-Trunk\d+).*', al.name)
            if re.findall('\w+\s(XGigabitEthernet\d+\/\d+\/\d+).*', al.name):
                inter = re.findall('\w+\s(XGigabitEthernet\d+\/\d+\/\d+).*', al.name)
            elif re.findall('\w+\s(GigabitEthernet\d+\/\d+\/\d+).*', al.name):
                inter = re.findall('\w+\s(GigabitEthernet\d+\/\d+\/\d+).*', al.name)
            else :
                continue
            pack = 'host: ' + list_host[i] + ', ip: ' + list_ip[i] + ', port: ' + inter[0]
            AllNetworkInterface.objects.create(name=pack, hostid=list_host_id[i], interface_name=inter[0], in_itemid=al.itemid, out_itemid=outgoing_interface[j].itemid)
            j += 1
            #

    # for nt in NetworkInterface.objects.all():
    #     try:
    #         AllNetworkInterface.objects.get(Q(name=nt.name))
    #     except:
    #         NetworkInterface.objects.get(name=nt.name).delete()
    return HttpResponseRedirect(reverse('zabbixmgr:networkinterface.add'))

class CreateNetworkInterface(CreateView):
    model = NetworkInterface
    template_name = 'zabbixmgr/network_interface.add.html'
    form_class = CreateNetworkInterfaceForm

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def form_valid(self, form):
        self.save(form)
        return HttpResponseRedirect(reverse('zabbixmgr:networkinterface.list'))

    def save(self, form):
        all_network_name = form.cleaned_data['name']
        name = all_network_name.name
        role_name = re.findall('host\: (.+)\, ip', name)[0]
        ip = re.findall('ip\: (.+)\,', name)[0]
        interface_name = all_network_name.interface_name
        type = form.cleaned_data['group_name'].id

        # NetworkInterface.objects.using('zabbixdb').create(role_name=role_name,
        NetworkInterface.objects.create(role_name=role_name,
                                                          ip=ip, inter_name=interface_name,
                                                          type=type,
                                                          name=all_network_name.name,
                                                          in_itemid=all_network_name.in_itemid,
                                                          out_itemid=all_network_name.out_itemid)

def delete_networkinterface(request):
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
    NetworkInterface.objects.filter(sql).delete()
    name_dict = {'code': '00', 'desc': '删除成功!'}
    return JsonResponse(name_dict)
