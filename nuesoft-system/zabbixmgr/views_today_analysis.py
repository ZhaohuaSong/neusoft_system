#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/27 15:32
# @Author  :
# @Site    :
# @File    : views_today_analysis.py
# @Software: PyCharm

from django.views.generic import TemplateView
from django.db.models import Q
from nowday_traffic_chartdata.nowday_chartdata import NowdayChartData
from package_chartdata.chart_data import ChartData
from views_traffic_analysis import TrafficAnalysisJson
from models import *
import time, datetime
from tabpage_data import TabPageData
import re
from constant import get_industry_park

def set_time():
    '''
    设置时间格式，如：10:00
    :return:
    '''
    datetime.datetime.now().strftime('%Y-%m-%d')

class NowdayAnalysisList(TemplateView, NowdayChartData):
    template_name = 'zabbixmgr/nowday_analysis.list.html'

    def get(self, request, *args, **kwargs):
        us = request.user.username
        industry_park =get_industry_park(us)
        context = self.get_context_data()
        pre_time = int(time.mktime(time.strptime(str(datetime.date.today()), '%Y-%m-%d')))
        last_time = int(time.time()) - ( int(time.time()) % 3600 )
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

class NowdayAnalysisJson(TrafficAnalysisJson):

    def get_url(self):
        url = self.request.path
        self.industry_id = int(re.findall('(\d+)$', url)[0])
        cg = ClientGroup.objects.filter(industry_id=self.industry_id)
        if cg:
            self.id = cg[0].id
        else:
            self.id = 1000
        # self.id = ClientGroup.objects.all()[0].id #需考虑不存在的情况
        self.table_id = 0
        self.time_interval = 1
        self.pre_time = int(time.mktime(time.strptime(str(datetime.date.today()), '%Y-%m-%d')))
        self.last_time = int(time.time()) - ( int(time.time()) % 3600 )

    def get_initial_queryset(self):
        '''
        重写数据库初始化方法
        :return:
        '''
        if self.table_flag == 0: #用户表
            self.sixday_druge = 1
            self.model = TGHistoryUint1Min
            self.group_get_itemid(self.id)
            sql = Q()
            sql |= Q(itemid=self.in_itemid)
            sql |= Q(itemid=self.out_itemid)
            return self.model.objects.filter(Q(clock__gte=self.pre_time) & Q(clock__lt=self.last_time) & sql)
        elif self.table_flag == 1: #端口表
#################################################################################
            self.model = HistoryUint
            self.sixday_druge = 1
            self.get_itemid(self.id)
            sql = Q()
            sql |= Q(itemid=self.in_itemid)
            sql |= Q(itemid=self.out_itemid)
            return self.model.objects.using('zabbixdb').filter(Q(clock__gte=self.pre_time) & Q(clock__lt=self.last_time) & sql & Q(industry_id=self.industry_id))

        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

class NowdayTabPageDataJson(TabPageData):

    def set_groupid(self):
        self.groupid = id_list[0]

class NowdayTrafficDataList(TemplateView, NowdayChartData):
    template_name = 'zabbixmgr/nowday_traffic_data.list.html'


    def get(self, request, *args, **kwargs):
        us = request.user.username
        industry_park =get_industry_park(us)
        context = self.get_context_data()
        self.user = request.user
        global outside_url
        outside_url = request.get_full_path()
        id_list = re.findall('zabbixmgr\/nowdaytrafficdata\/list\/(\d+)\/(\w+)\/(\d+)\/(\d+)\/(\d+)\/(\d+)', outside_url)[0]
        if id_list[1] != 'a': #端口不为空
            table_id = 1
            id = id_list[1]
        else: #端口为空
            id = id_list[0]
            table_id = 0
        l2 = int(time.mktime(time.strptime(str(datetime.date.today()), '%Y-%m-%d'))) + int(id_list[2])*3600
        l3 = int(time.mktime(time.strptime(str(datetime.date.today()), '%Y-%m-%d'))) + int(id_list[3])*3600
        l4 = id_list[4]
        l5 = id_list[5]
        global id_list
        id_list = [id, table_id, l2, l3, l4, l5]

        # public = PublicWays()
        # pre_time = public.localtime_to_time(id_list[2])
        # last_time = public.localtime_to_time(id_list[3])
        temp_time = l3 - l2
        temp_time /=(8*60)
        in_peak, out_peak, clo, in_avg, out_avg = self.get_data(id_list)

        context['table_id'] = table_id
        context['industry_park'] = industry_park
        context['industry_id'] = l5
        chartdata = ChartData()
        context = chartdata.context_data(context, in_peak, out_peak, clo, temp_time, id_list, in_avg, out_avg)

        return self.render_to_response(context)

class NowdayTrafficDataJson(TrafficAnalysisJson):
    def get_url(self):
        url = self.request.path
        self.industry_id = int(re.findall('(\d+)$', url)[0])
        # cg = ClientGroup.objects.filter(industry_id=self.industry_id)
        # if cg:
        #     self.id = cg[0].id
        # else:
        #     self.id = 1000
        self.id = id_list[0]
        self.table_id = id_list[1]
        self.time_interval = int(id_list[4])
        self.pre_time =  id_list[2]
        self.last_time = id_list[3]

    def get_initial_queryset(self):
        '''
        重写数据库初始化方法
        :return:
        '''
        if self.table_flag == 0: #用户表
            self.sixday_druge = 1
            self.model = TGHistoryUint1Min
            self.group_get_itemid(self.id)
            sql = Q()
            sql |= Q(itemid=self.in_itemid)
            sql |= Q(itemid=self.out_itemid)
            return self.model.objects.filter(Q(clock__gte=self.pre_time) & Q(clock__lt=self.last_time) & sql)
        elif self.table_flag == 1: #端口表
#################################################################################
            self.model = HistoryUint
            self.sixday_druge = 1
            self.get_itemid(self.id)
            sql = Q()
            sql |= Q(itemid=self.in_itemid)
            sql |= Q(itemid=self.out_itemid)
            return self.model.objects.using('zabbixdb').filter(Q(clock__gte=self.pre_time) & Q(clock__lt=self.last_time) & sql)

        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
