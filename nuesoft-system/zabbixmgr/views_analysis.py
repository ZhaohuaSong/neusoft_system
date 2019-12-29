#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/11/29 10:34
# @Author  :
# @Site    :
# @File    : views_analysis.py
# @Software: PyCharm

from django.views.generic import TemplateView
from ..common.datatables.views import BaseDatatableView
from views_traffic_analysis import TrafficAnalysisJson
from public_ways import PublicWays
from traffic_data import GetChartData
from models import *
import json
import logging
import re
from tabpage_data import TabPageData
from package_chartdata.chart_data import ChartData
import datetime, time
from constant import get_industry_park
logger = logging.getLogger(__name__)

outside_url = None #类公用
id_list =None

def set_nowdatetime():
    public = PublicWays()
    pre, last = public.time_interval(1)
    pre_time = public.time_to_localtime(pre)
    pre_time = re.findall('(\d+)\-(\d+)\-(\d+)', pre_time)[0]
    last_time = public.time_to_localtime(last)
    last_time = re.findall('(\d+)\-(\d+)\-(\d+)', last_time)[0]
    pre_time = pre_time[0] + pre_time[1] + pre_time[2]
    last_time = last_time[0] + last_time[1] + last_time[2]
    return pre_time, last_time

class AnalysisList(TemplateView, GetChartData):
    template_name = 'zabbixmgr/analysis.list.html'

    def get(self, request, *args, **kwargs):
        us = request.user.username
        industry_park =get_industry_park(us)
        context = self.get_context_data()
        pre_time, last_time = set_nowdatetime()
        url = self.request.get_full_path()
        industry_id = int(re.findall('(\d+)$', url)[0])
        cg = ClientGroup.objects.filter(industry_id=industry_id)
        if cg:
            id = cg[0].id
        else:
            id = 1000
        global id_list

        id_list = [id, 0, pre_time, last_time, 1, industry_id]
        in_peak, out_peak, clo, in_avg, out_avg = self.get_data(id_list)

        temp_time = int(last_time) - int(pre_time)
        temp_time /=(8*60)

        chartdata = ChartData()
        context = chartdata.context_data(context, in_peak, out_peak, clo, temp_time, id_list, in_avg, out_avg)

        context['industry_park'] = industry_park
        context['industry_id'] = industry_id

        return self.render_to_response(context)

def set_interval(inter_val):
    itl = inter_val
    time_interval = None
    if itl == 1:
        time_interval = 1
    elif itl == 2:
        time_interval = 5
    elif itl == 3:
        time_interval = 60
    elif itl == 4:
        time_interval = 1440
    elif itl == 5:
        time_interval = 10

    return time_interval

class AnalysisJson(TrafficAnalysisJson):

    def get_url(self):
        url = self.request.path
        self.industry_id = int(re.findall('(\d+)$', url)[0])
        cg = ClientGroup.objects.filter(industry_id=self.industry_id)
        if cg:
            self.id = cg[0].id
        else:
            self.id = 1000
        pre_time, last_time = set_nowdatetime()
        # self.id = ClientGroup.objects.all()[0].id #需考虑不存在的情况
        self.table_id = 0
        self.time_interval = 1
        public = PublicWays()
        self.pre_time = public.localtime_to_time(pre_time)
        self.last_time = public.localtime_to_time(last_time)
        self.p_time = public.time_to_localtime(self.pre_time)
        self.l_time = public.time_to_localtime(self.last_time)

class TrafficDataList(TemplateView, GetChartData):
    template_name = 'zabbixmgr/traffic_data.list.html'

    def get(self, request, *args, **kwargs):
        us = request.user.username
        industry_park =get_industry_park(us)
        context = self.get_context_data()
        self.user = request.user
        global outside_url
        outside_url = request.get_full_path()
        id_list = re.findall('zabbixmgr\/trafficdata\/list\/(\d+)\/(\w+)\/(\d+)\/(\d+)\/(\d+)\/(\d+)', outside_url)[0]
        if id_list[1] != 'a': #端口不为空
            table_id = 1
            id = id_list[1]
        else: #端口为空
            id = id_list[0]
            table_id = 0
        l2 = id_list[2]
        l3 = id_list[3]
        l4 = id_list[4]
        l5 = id_list[5]
        global id_list
        id_list = [id, table_id, l2, l3, l4, l5]

        public = PublicWays()
        pre_time = public.localtime_to_time(id_list[2])
        last_time = public.localtime_to_time(id_list[3])
        temp_time = last_time - pre_time
        temp_time /=(8*60)
        in_peak, out_peak, clo, in_avg, out_avg = self.get_data(id_list)

        context['table_id'] = table_id
        context['industry_park'] = industry_park
        context['industry_id'] = l5
        chartdata = ChartData()
        context = chartdata.context_data(context, in_peak, out_peak, clo, temp_time, id_list, in_avg, out_avg)

        return self.render_to_response(context)

class TrafficDataJson(TrafficAnalysisJson):
    def get_url(self):
        url = self.request.path
        self.industry_id = int(re.findall('(\d+)$', url)[0])
        self.id = id_list[0]
        self.table_id = id_list[1]
        self.time_interval = int(id_list[4])
        public = PublicWays()
        self.pre_time = public.localtime_to_time(id_list[2])
        self.last_time = public.localtime_to_time(id_list[3])
        self.p_time = public.time_to_localtime(self.pre_time)
        self.l_time = public.time_to_localtime(self.last_time)

class TabPageDataJson(TabPageData):

    def set_groupid(self):
        self.groupid = id_list[0]
