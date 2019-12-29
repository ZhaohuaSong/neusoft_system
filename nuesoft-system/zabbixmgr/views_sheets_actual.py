#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/11/2 15:30
# @Author  :
# @Site    :
# @File    : views_sheets_actual.py
# @Software: PyCharm

from django.views.generic import TemplateView
from ..common.datatables.views_network import BaseDatatableView
from models import *
import time
import datetime
from django.db.models import Q
import re

SIZE = 1024
ONEDAY = 3600*24

ONEMIN_INTERVAL = 1
FIVEMIN_INTERVAL = 5
ONEHOUR_INTERVAL = 12
ONEDAY_INTERVAL = 24

class SheetsActualList(TemplateView):
    template_name = 'zabbixmgr/sheets_actual.list.html'

class SheetsActualJson(BaseDatatableView):
    model = HistoryUint
    client = []
    total_average = 0
    columns = ['itemid', 'itemid']
    order_columns = columns
    id_list = [148655, 148917]
    pre_time = 1528041600
    last_time = 1528128000

    def get_itemid(self):
        '''
        获取所有网络端口流量进出itemid
        :return:
        '''
        self.interface = SheetsInterface.objects.all()
        client = []
        self.incoming_interface_list = []
        self.outgoing_interface_list = []
        for inter in self.interface:
            self.incoming_interface_list.append(inter.in_itemid)
            self.outgoing_interface_list.append(inter.out_itemid)
            self.client.append(inter.client)
        all_inter = self.incoming_interface_list + self.outgoing_interface_list
        self.total_records = len(self.incoming_interface_list) +1
        self.total_display_records = self.total_records
        sql = Q()
        for i in all_inter:
            sql |= Q(itemid=i)

        sql |= Q(itemid=148655)
        sql |= Q(itemid=148917)
        t = int(time.time()) - 3600*24*6
        quset = HistoryUint.objects.using('zabbixdb').filter(Q(clock__gte=t) & sql)
        return quset

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        sql = Q()
        sql |= Q(itemid=self.id_list[0])
        sql |= Q(itemid=self.id_list[1])
        return self.model.objects.using('zabbixdb').filter(Q(clock__gte=self.pre_time) & Q(clock__lte=self.last_time) & sql)

    def paging(self, qs):
        '''
        重写分页方法
        :param qs:
        :return:
        '''
        if self.pre_camel_case_notation:
            self.limit = min(int(self._querydict.get('iDisplayLength', 10)), self.max_display_length)
            start = int(self._querydict.get('iDisplayStart', 0))
        else:
            self.limit = min(int(self._querydict.get('length', 10)), self.max_display_length)
            self.start = int(self._querydict.get('start', 0))

        if self.limit == -1:
            return qs
        self.offset = self.start + self.limit

    def prepare_results(self, qs):
        '''
        重写数据打包方法
        :param qs:
        :return:
        '''
        data = []
        in_val = 0
        out_val = 0
        in_val_rate = 0
        out_val_rate = 0
        out_peak_rate = 0
        in_peak_rate = 0
        s = datetime.datetime.now()

        self.start *= ONEMIN_INTERVAL
        self.offset *= ONEMIN_INTERVAL
        in_list = list(qs.filter(itemid=self.id_list[0])[self.start:self.offset].values_list('value', flat=True))
        out_list = list(qs.filter(itemid=self.id_list[1])[self.start:self.offset].values_list('value', flat=True))
        for i in range(len(in_list)/ONEMIN_INTERVAL):
            for j in range(ONEMIN_INTERVAL):
                in_val += in_list[j]*60
                out_val += out_list[j]*60
                in_peak_rate = max(in_peak_rate, in_list[j])
                out_peak_rate = max(out_peak_rate, out_list[j])
                in_val_rate += in_list[j]
                out_val_rate += out_list[j]
            i += ONEMIN_INTERVAL
            in_val = round(float(in_val)/(SIZE*SIZE*SIZE), 2) #流入流量
            out_val = round(float(out_val)/(SIZE*SIZE*SIZE), 2) #流出流量
            total_val = in_val + out_val #总流量
            in_peak_rate = round(float(in_peak_rate)/(SIZE*SIZE*SIZE), 2) #峰值流入速率
            out_peak_rate = round(float(out_peak_rate)/(SIZE*SIZE*SIZE), 2) #峰值流出速率
            total_peak_rate = in_peak_rate + out_peak_rate #双向峰值速率
            in_average_rate = in_val_rate/ONEMIN_INTERVAL #流入速率(均值)
            out_average_rate = out_val_rate/ONEMIN_INTERVAL #流出速率(均值)
            in_average_rate = round(float(in_val_rate)/(SIZE*SIZE*SIZE), 2)
            out_average_rate = round(float(out_average_rate)/(SIZE*SIZE*SIZE), 2)
            total_average_rate = in_average_rate + out_average_rate #总速率

            if re.match('^100GE.*', '100GE6/0/0'):
                single_average = 100
                self.total_average += 100
            else:
                single_average = 10
                self.total_average += 10

            average_usage = max(in_average_rate, out_average_rate)/(single_average*SIZE) #带宽利用率
            peak_usage = max(in_peak_rate, out_peak_rate)/(single_average*SIZE) #峰值利用率
            average_usage = str(round(average_usage, 2) * 100) + '%'
            peak_usage = str(round(peak_usage, 2) * 100) + '%'

            # t = time.localtime(in_quset[i].clock)
            # t = time.strftime('%m-%d %H:%M:%S', t)

            temp = [11,
                    22,
                    1,
                    'kobe',
                    out_val,
                    in_val,
                    round(total_val, 2), #
                    out_peak_rate,
                    out_average_rate,
                    in_peak_rate,
                    in_average_rate,
                    round(total_peak_rate, 2), #
                    round(total_average_rate, 2), #
                    average_usage,
                    peak_usage]

            data.append(temp)
        e = datetime.datetime.now()
        print e-s
        return data
