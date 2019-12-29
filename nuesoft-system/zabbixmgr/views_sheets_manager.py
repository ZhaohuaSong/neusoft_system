#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/10/25 12:03
# @Author  :
# @Site    :
# @File    : views_sheets_manager.py
# @Software: PyCharm

from django.views.generic import TemplateView
from ..common.datatables.views import BaseDatatableView
from models import *
import time
import datetime
from django.db.models import Q

from sheets_manager import CreateSheetsManager
from interval_datas import CreateIntervalDatas

ONEDAY = 3600*24 #second

from apscheduler.scheduler import Scheduler
sched = Scheduler()

@sched.interval_schedule(hours=2, start_date='2016-8-15 00:00')
def scheduler_task():
    pt = int(time.mktime(time.strptime(str(datetime.date.today()), '%Y-%m-%d'))) - 86400
    lt = int(time.mktime(time.strptime(str(datetime.date.today()), '%Y-%m-%d')))
    if not GHistoryUint1Min.objects.filter(Q(clock__gte=pt) & Q(clock__lt=lt)).exists():
        time.sleep(300)
        cr = CreateIntervalDatas()
        cr.context_data()
    else:
        print 'exists'

# sched.start()
# cr = CreateIntervalDatas()
# cr.context_data()

# itemid = [39619,39620,39733,39653,39655,39783,39681,39707,39734,39654,39656,39784,39682,39708]
# sql = Q()
# for i in itemid:
#     sql |= Q(itemid=i)
# in_triffac = TrendsUint.objects.using('zabbixdb').filter(sql & Q(clock__gte=1554825600) & Q(clock__lt=1554912000)).values_list('value_avg', flat=True)
# print sum(in_triffac)

from nowday_temp_data.temp_data import CreateTempDatas
@sched.interval_schedule(minutes=15, start_date='2016-8-15 00:15')
def scheduler_task2():
    # time.sleep(600)
    cn = CreateTempDatas()
    cn.context_data()
    #删除大于一年的数据
    from django.db.models import Min, Max
    max_data = GHistoryUint1Day.objects.all().aggregate(Max('clock'))
    min_data = GHistoryUint1Day.objects.all().aggregate(Min('clock'))
    day_num = (max_data['clock__max'] - min_data['clock__min'])/86400
    if day_num > 365:
        GHistoryUint1Min.objects.filter(clock__lt=min_data['clock_min']).delete()
    else:
        print 'not enough'

from views_network_cost import *
@sched.interval_schedule(minutes=15, start_date='2016-8-15 00:15')
def scheduler_task3():
    last_month_first_day = (datetime.date.today().replace(day=1) - datetime.timedelta(1)).replace(day=1)
    if not NetworkCost.objects.filter(cost_month=last_month_first_day).exists():
        time.sleep(500)
        # n = NetworkCount()
        # n.get_5min_data()

sched.start()

from onehour_interval_datas import CreateOnehourIntervalDatas
# c = CreateOnehourIntervalDatas()
# c.context_data()

from client_history_datas import CreateClientHistoryDatas

# c = CreateClientHistoryDatas()
# c.context_data()

class SheetsManagerList(TemplateView):
    template_name = 'zabbixmgr/sheets_manager.list.html'

    # in_list = list(SheetsInterface.objects.all().values_list('in_itemid', flat=True))
    # out_list = list(SheetsInterface.objects.all().values_list('out_itemid', flat=True))
    # li = in_list + out_list
    # sql = Q()
    # for i in li:
    #     sql |= Q(itemid=i)
    #
    # l = []
    #
    # li = li[180:216]
    # for j in range(len(li)):
    #     c = 1514217600
    #     v = 6397972736
    #     for i in range(1440):
    #         print i
    #         temp = HistoryUint(itemid=li[j], clock=c, value=v, ns=i)
    #         c += 60
    #         v -= 1000000
    #         l.append(temp)
    # HistoryUint.objects.using('zabbixdb').bulk_create(l)
from onehour_interval_datas import *
class SheetsManagerJason(BaseDatatableView):
    # s = datetime.datetime.now()
    # cr = CreateIntervalDatas()
    # cr.context_data()
    # e = datetime.datetime.now()
    # print e-s

    #获取添加客户之前的数据
    # s = datetime.datetime.now()
    # cr = CreateOnehourIntervalDatas()
    # cr.context_data()
    # e = datetime.datetime.now()
    # print e-s


    model = SheetsManager
    columns = ['sheetid',
               'sheetid',
               'update_time',
               'client',
               'out_val',
               'in_val',
               'total_val',
               'out_peak_rate',
               'out_average_rate',
               'in_peak_rate',
               'in_average_rate',
               'total_peak_rate',
               'total_average_rate',
               'average_usage',
               'peak_usage']
    order_columns = columns
    def get_json(self, response):
        data_list = response['data']
        for data in data_list:
            if isinstance(data[2], datetime.datetime):
                data[2]=data[2].strftime("%m月%d日")
        return super(SheetsManagerJason, self).get_json(response)
