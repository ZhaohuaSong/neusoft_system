#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/27 15:32
# @Author  :
# @Site    :
# @File    : views_today_analysis.py
# @Software: PyCharm

from django.views.generic import TemplateView
from django.db.models import Q
from ..nowday_traffic_chartdata.nowday_chartdata import NowdayChartData
from ..package_chartdata.chart_data import ChartData
# from views_traffic_analysis import TrafficAnalysisJson
from ..models import *
import time, datetime
# from tabpage_data import TabPageData
import re, json
from ..constant import get_industry_park

def set_time():
    '''
    设置时间格式，如：10:00
    :return:
    '''
    datetime.datetime.now().strftime('%Y-%m-%d')

class OutTrafficChartshow(TemplateView, NowdayChartData):
    template_name = 'zabbixmgr/nowday_traffic_chartshow.list.html'

    def ipToNum(self,ip):
        # ip address transformat into binary
        ip=[int(x) for x in ip.split('.')]
        return ip[0]<<24 | ip[1]<<16 | ip[2]<<8 |ip[3]

    def get(self, request, *args, **kwargs):
        user = request.user.username
        industry_park = get_industry_park(user)
        # industry_name = industry_park.values()
        context = self.get_context_data()
        pre_time = int(time.mktime(time.strptime(str(datetime.date.today()), '%Y-%m-%d')))
        last_time = int(time.time()) - ( int(time.time()) % 3600 )
        sql = Q()
        sql_id = industry_park.keys()
        for id in sql_id:
            sql|= Q(industry_id=int(id))
        cg = ClientGroup.objects.filter(Q(client_name='出口监控') & sql).values_list('id', 'industry_id')
        global id_list
        temp_time = int(last_time) - int(pre_time)
        temp_time /=(8*60)
        context_list = []
        for i in cg:
            id_list = [i[0], 0, pre_time, last_time, 1, i[1]]
            in_peak, out_peak, clo, in_avg, out_avg = self.get_data(id_list)
            chartdata = ChartData()
            ctx = {}
            context_list.append(chartdata.context_data(ctx, in_peak, out_peak, clo, temp_time, id_list, in_avg, out_avg))
        context['chart_data'] = json.dumps(context_list)
        park_ip_list = IpLibrary.objects.filter(sql).values_list('industry_id', 'all_ip')
        ip_data = []
        for park_ip in park_ip_list:
            total_num = 0
            for ip in json.loads(park_ip[1]):
                num_list = [self.ipToNum(x) for x in ip.split('-') ]
                total_num += num_list[-1] - num_list[0] + 1

            client_ip_num = sum(list(IpAddress.objects.filter(industry_id=park_ip[0]).values_list('ip_num', flat=True)))

            usage = {}
            industry_name = industry_park[str(park_ip[0])]
            usage[industry_name] = [client_ip_num, total_num - client_ip_num] #已使用ip, 剩余ip
            ip_data.append(usage)
        context['ip_data'] = json.dumps(ip_data)

        bandwidth_data = []
        park_id_list = industry_park.keys()
        for park_id in park_id_list:
            client_bandwidth = sum(list(SheetsInterface.objects.filter(industry_id=int(park_id)).values_list('bandwidth', flat=True)))
            total_bandwidth = IndustryPark.objects.get(id=int(park_id)).bandwidth
            usage = {}
            industry_name = industry_park[park_id]
            usage[industry_name] = [client_bandwidth, total_bandwidth - client_bandwidth]
            bandwidth_data.append(usage)
        context['bandwidth_data'] = json.dumps(bandwidth_data)

        box_usage_list = []
        for park_id in park_id_list:
            building_id = list(IDCBuilding.objects.filter(park_id=park_id).values_list('building_id', flat=True))
            building_list = []
            for i in building_id:
                total_num = sum(list(DeviceRoom.objects.filter(industry_id=park_id, building_id=i).values_list('total_box', flat=True)))
                unuse_num = sum(list(DeviceRoom.objects.filter(industry_id=park_id, building_id=i).values_list('unuse_box', flat=True)))
                use_num = total_num - unuse_num
                building_name = IDCBuilding.objects.get(park_id=park_id, building_id=i).building_name
                industry_name = industry_park[park_id]
                building_list.append([ industry_name, building_name, use_num, unuse_num])

            box_usage_list.append(building_list)
        context['box_usage'] = json.dumps(box_usage_list)

        context['industry_park'] = industry_park

        return self.render_to_response(context)

# class NowdayAnalysisJson(TrafficAnalysisJson):
#
#     def get_url(self):
#         self.id = ClientGroup.objects.all()[0].id #需考虑不存在的情况
#         self.table_id = 0
#         self.time_interval = 1
#         self.pre_time = int(time.mktime(time.strptime(str(datetime.date.today()), '%Y-%m-%d')))
#         self.last_time = int(time.time()) - ( int(time.time()) % 3600 )
#
#     def get_initial_queryset(self):
#         '''
#         重写数据库初始化方法
#         :return:
#         '''
#         if self.table_flag == 0: #用户表
#             self.sixday_druge = 1
#             self.model = TGHistoryUint1Min
#             self.group_get_itemid(self.id)
#             sql = Q()
#             sql |= Q(itemid=self.in_itemid)
#             sql |= Q(itemid=self.out_itemid)
#             return self.model.objects.filter(Q(clock__gte=self.pre_time) & Q(clock__lt=self.last_time) & sql)
#         elif self.table_flag == 1: #端口表
# #################################################################################
#             self.model = HistoryUint
#             self.sixday_druge = 1
#             self.get_itemid(self.id)
#             sql = Q()
#             sql |= Q(itemid=self.in_itemid)
#             sql |= Q(itemid=self.out_itemid)
#             return self.model.objects.using('zabbixdb').filter(Q(clock__gte=self.pre_time) & Q(clock__lt=self.last_time) & sql)
#
#         if not self.model:
#             raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
#
# class NowdayTabPageDataJson(TabPageData):
#
#     def set_groupid(self):
#         self.groupid = id_list[0]
#
# class NowdayTrafficDataList(TemplateView, NowdayChartData):
#     template_name = 'zabbixmgr/nowday_traffic_data.list.html'
#
#
#     def get(self, request, *args, **kwargs):
#         context = self.get_context_data()
#         self.user = request.user
#         global outside_url
#         outside_url = request.get_full_path()
#         id_list = re.findall('zabbixmgr\/nowdaytrafficdata\/list\/(\d+)\/(\w+)\/(\d+)\/(\d+)\/(\d+)', outside_url)[0]
#         if id_list[1] != 'a': #端口不为空
#             table_id = 1
#             id = id_list[1]
#         else: #端口为空
#             id = id_list[0]
#             table_id = 0
#         l2 = int(time.mktime(time.strptime(str(datetime.date.today()), '%Y-%m-%d'))) + int(id_list[2])*3600
#         l3 = int(time.mktime(time.strptime(str(datetime.date.today()), '%Y-%m-%d'))) + int(id_list[3])*3600
#         l4 = id_list[4]
#         global id_list
#         id_list = [id, table_id, l2, l3, l4]
#
#         # public = PublicWays()
#         # pre_time = public.localtime_to_time(id_list[2])
#         # last_time = public.localtime_to_time(id_list[3])
#         temp_time = l3 - l2
#         temp_time /=(8*60)
#         in_peak, out_peak, clo = self.get_data(id_list)
#
#         context['table_id'] = table_id
#         chartdata = ChartData()
#         context = chartdata.context_data(context, in_peak, out_peak, clo, temp_time, id_list)
#
#         return self.render_to_response(context)
#
# class NowdayTrafficDataJson(TrafficAnalysisJson):
#     def get_url(self):
#         self.id = id_list[0]
#         self.table_id = id_list[1]
#         self.time_interval = int(id_list[4])
#         self.pre_time =  id_list[2]
#         self.last_time = id_list[3]
#
#     def get_initial_queryset(self):
#         '''
#         重写数据库初始化方法
#         :return:
#         '''
#         if self.table_flag == 0: #用户表
#             self.sixday_druge = 1
#             self.model = TGHistoryUint1Min
#             self.group_get_itemid(self.id)
#             sql = Q()
#             sql |= Q(itemid=self.in_itemid)
#             sql |= Q(itemid=self.out_itemid)
#             return self.model.objects.filter(Q(clock__gte=self.pre_time) & Q(clock__lt=self.last_time) & sql)
#         elif self.table_flag == 1: #端口表
# #################################################################################
#             self.model = HistoryUint
#             self.sixday_druge = 1
#             self.get_itemid(self.id)
#             sql = Q()
#             sql |= Q(itemid=self.in_itemid)
#             sql |= Q(itemid=self.out_itemid)
#             return self.model.objects.using('zabbixdb').filter(Q(clock__gte=self.pre_time) & Q(clock__lt=self.last_time) & sql)
#
#         if not self.model:
#             raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
