#!/usr/bin/env python
# -*- coding: utf-8 -*-


from django.views.generic import TemplateView
from ..common.datatables.views import BaseDatatableView
from django.db.models import Q
import datetime
from temporarydb import GetTableData
from chartdatashow import ChartDataShow
from django.shortcuts import render,render_to_response
import time
import re
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from ..vanilla import CreateView
from models import *
from forms import *
import json
import os
from constant import get_industry_park

class HostList(TemplateView):
    template_name = 'zabbixmgr/host.list.html'

    def get(self, request, *args, **kwargs):
        us = request.user.username
        industry_park =get_industry_park(us)
        url = self.request.get_full_path()
        industry_id = int(re.findall('(\d+)$', url)[0])
        interface = Interface.objects.using('zabbixdb').all()
        hs_id = []
        for i in interface:
            hs_id.append(i.hostid.hostid)
        host = Hosts.objects.using('zabbixdb').all()
        name = []
        for h in host:
            if h.hostid in hs_id:
                name.append(h.host)
        nodelist = []
        i = 0
        # 从数据字典组成JSON数据给树形控件
        for n in name:
            dict_obj = {}
            dict_obj['text'] = n
            dict_obj['id'] = hs_id[i]
            dict_obj['tags'] = ['0']
            nodelist.append(dict_obj)
            i += 1

        context = self.get_context_data()
        context['request'] = request
        context['treedata'] = json.dumps(nodelist)
        context['industry_park'] = industry_park
        context['industry_id'] = industry_id
        return self.render_to_response(context)

class ApplicationJson(BaseDatatableView):
    '''
    Json 数据格式
    '''
    model = Applications
    columns = ['applicationid', 'applicationid','name','applicationid']
    order_columns = ['applicationid','applicationid','name','applicationid']

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return self.model.objects.using('zabbixdb').all()

    #GET请求入口
    def get(self, request, *args, **kwargs):
        # self.user = request.user
        return super(ApplicationJson, self).get(request, *args, **kwargs)

    def filter_queryset(self, qs):
        #搜索数据集
        hostid = self._querydict.get('id')
        # interface = Interface.objects.using('zabbixdb').all()
        # hs_id = []
        # for i in interface:
        #     hs_id.append(i.hostid.hostid)

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
        qs = qs.filter(Q(hostid=hostid))
        return qs

di = {}

class ItemsList(TemplateView, GetTableData):
    template_name = 'zabbixmgr/items.list.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        url = request.get_full_path()
        applicationid = int(re.findall('(\d+)\/$', url)[0])
        self.applicationid = applicationid
        us = request.user.username

        # if us not in di:
        #     di[us] = self.applicationid
        di[us] = self.applicationid
        host_name = Applications.objects.using('zabbixdb').get(applicationid=applicationid).hostid.host
        context['host_name'] = host_name
        return self.render_to_response(context)

class ItemsJson(GetTableData, BaseDatatableView):
    '''
    Json 数据格式
    '''
    model = Items
    columns = ['tempid', 'tempid', 'name','value','clock', 'tempid']
    order_columns = ['tempid','tempid', 'name','value','clock', 'tempid']

    def create_sql(self, v):
        value_type = [0, 1, 3]
        flags = [0, 4]
        itemid = list(ItemsApplications.objects.using('zabbixdb').filter(applicationid=v).values_list('itemid', flat=True))
        sql1 = sql2 = sql3 = Q()
        for i in value_type:
            sql1 |= Q(value_type=i)
        for i in flags:
            sql2 |= Q(flags=i)
        for i in itemid:
            sql3 |= Q(itemid=i)
        return [sql1, sql2, sql3]

    def get_initial_queryset(self):

        us_name = self.request.user.username
        v = di[us_name]
        sql = self.create_sql(v)
        sql1 = Q()
        sql1 |= Q(key_field__contains='net.if.in[ifHCInOctets')
        sql1 |= Q(key_field__contains='net.if.out[ifHCOutOctets')
        self.model = Items.objects.using('zabbixdb').filter(sql[0] & sql[1] & sql[2] & Q(state=0))
        try:
            if 'Interface' in self.model[0].name:
                self.model = Items.objects.using('zabbixdb').filter(sql[0] & sql[1] & sql[2] & Q(state=0) & sql1)
        except:
            if not self.model:
                raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return self.model

    def prepare_results(self, qs):
        data = self.get_data(qs)
        return data

class ChartShow(TemplateView, ChartDataShow):
    template_name = 'zabbixmgr/chart_show.html'
    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        self.user = request.user
        outside_url = request.get_full_path()
        # json_data = get_chart_data(url)
        typ = int(re.findall('(\d+)\/$', outside_url)[0])
        item_id = int(re.findall('(\d+)\/\d+\/', outside_url)[0])
        ip = Items.objects.using('zabbixdb').filter(itemid=item_id)[0].hostid.host
        ite = Items.objects.using('zabbixdb').filter(itemid=item_id)
        app_name = str(ite[0].name)
        if typ == 0:
            self.timer = '1小时'
        elif typ == 1:
            self.timer = '2小时'
        elif typ == 2:
            self.timer = '1天'
        self.set_url(outside_url)
        json_data = self.table_router()
        if len(json.loads(json_data['value'])) == 1: #项目数值
            con = {}
            con['user'] = self.user
            con['clock'] = json_data['clock']
            con['value'] = json.loads(json_data['value'])
            con['text_title'] = json_data['text_title']
            return render_to_response('zabbixmgr/history_record.html', con)
        else: #项目图表
            context['clock'] = json_data['clock']
            context['value'] = json.loads(json_data['value'])
            context['text_title'] = json.dumps(ip+': '+app_name)
            context['units'] = json_data['units']
            pre_url = request.get_host()
            context['outside_url'] = json.dumps(pre_url)
            context['timer'] = json.dumps(self.timer)
            context['item_id'] = item_id
            return self.render_to_response(context)
