#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/9/21 12:01
# @Author  :
# @Site    :
# @File    : views_cpu_chartshow.py
# @Software: PyCharm5
# @Function:

from django.views.generic import TemplateView
from cpu_data import CpuData
import json
import re
from temporarydb import GetTableData
from models import Items, ProcessorLoadItemid, TemporaryTable, History
from ..common.datatables.views import BaseDatatableView
from constant import get_industry_park

class CpuChartshowList(TemplateView, CpuData):
    template_name = 'zabbixmgr/cpu_chart_show.html'

    url = None
    def get(self, request, *args, **kwargs):
        us = request.user.username
        industry_park =get_industry_park(us)
        url = self.request.get_full_path()
        industry_id = int(re.findall('(\d+)$', url)[0])
        self.url = request.get_full_path()
        context = self.get_context_data(**kwargs)
        context['industry_park'] = industry_park
        context['industry_id'] = industry_id
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(CpuChartshowList, self).get_context_data(**kwargs)
        self.get_cpu_data()
        context['level_1'] = json.dumps(self.cpu_data['data_1'])
        context['level_5'] = json.dumps(self.cpu_data['data_5'])
        context['level_15'] = json.dumps(self.cpu_data['data_15'])
        context['url'] = json.dumps(self.url)
        return context

class CpuList(TemplateView, GetTableData):

    template_name = 'zabbixmgr/cpu.list.html'

    level_type = None
    def get_data(self):
        '''
        重写获取数据方法
        :return:
        '''
        self.temporarytable = TemporaryTable()
        try:
            # TemporaryTable.objects.using('zabbixdb').all().delete()
            TemporaryTable.objects.all().delete()
        except:
            pass
        itemid_list = []
        for pro in ProcessorLoadItemid.objects.filter(type=self.level_type):
            itemid_list.append(pro.itemid)
        cpu_items = Items.objects.using('zabbixdb').filter(itemid__in=itemid_list)
        for cpu in cpu_items:
            self.cur_itemid = cpu.itemid
            self.cur_delay = cpu.delay
            self.temporarytable.tempid = cpu.itemid
            try: #应用名获取
                    name = cpu.name
                    key_field = cpu.key_field
                    na = re.findall('(\$+\d)', name)
                    key_field = re.findall('\[(.+)\]', key_field)[0]
                    key_field = key_field.split(',')
                    for n in na:
                        name = name.replace(n, key_field[int(n[1:])-1])
                    self.temporarytable.name = name
                        # temporary_name = name
            except:
                self.temporarytable.name = cpu.name
            self.table_router(History)
            self.temporarytable.save()
        tem = TemporaryTable.objects.all()
        for t in tem:
            h = Items.objects.using('zabbixdb').get(itemid=t.tempid).hostid.host
            temporarytable = TemporaryTable.objects.get(tempid=t.tempid)
            temporarytable.host_name = h
            temporarytable.save()

    def get(self, request, *args, **kwargs):
        url = request.get_full_path()
        self.level_type = re.findall('(\d+)\/$', url)[0]
        self.get_data()
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

class CpuJson(BaseDatatableView):
    '''
    Json 数据格式
    '''
    model = TemporaryTable
    columns = ['tempid', 'tempid', 'host_name', 'name','value','clock', 'tempid']
    order_columns = ['tempid','tempid',  'host_name', 'name','value','clock', 'tempid']

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        # return self.model.objects.using('zabbixdb').all()
        return self.model.objects.all()
