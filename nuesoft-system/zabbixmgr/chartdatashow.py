#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/9/11 15:23
# @Author  :
# @Site    :
# @File    : chartdatashow.py
# @Software: PyCharm5
# @Function:

import re
from models import *
from django.db.models import Q
import time
import json
TIME_INTERVAL_ONEHOUR = 3600 #时间段（s）
TIME_INTERVAL_TWOHOUR = 3600*2
TIME_INTERVAL_ONEDAY = 3600*24

ONEHOUR = 60
TWOHOUR = 2*60
ONEDAY = 24*60

class ChartDataShow():
    # def __init__(self, itemid, url=None):
    #     self.url = url
    #     self.items = None
    #     self.itemid = itemid
    #     self.value_type = 0

    url = None
    items = None
    itemid = None
    value_type = None
    in_value = None
    out_value = None
    timer = '1小时'
    slice_timer = None
    interval_time = None
    id = None

    def set_url(self, url):
        self.url = url

    def timestamp_conversion(self, timestamp):
        '''
        时间戳转换
        :param timestamp: 时间戳
        :return:
        '''
        timeArray = time.localtime(timestamp)
        return time.strftime("%H:%M", timeArray)

    def get_hostid(self):
        interface = Interface.objects.using('zabbixdb').all()
        hs_id = []
        for i in interface:
            hs_id.append(i.hostid.hostid)
        return hs_id

    def items_count(self):
        hs_id = self.get_hostid()
        for i in hs_id:
            items = Items.objects.using('zabbixdb').filter(Q(hostid=i))
            return len(items)

    def set_time_interval(self):
        '''
        设置时间间隔
        :return:
        '''
        if self.timer == '1小时':
            self.slice_timer = TIME_INTERVAL_ONEHOUR
            self.interval_time = ONEHOUR
        elif self.timer == '2小时':
            self.slice_timer = TIME_INTERVAL_TWOHOUR
            self.interval_time = TWOHOUR
        elif self.timer == '1天':
            self.slice_timer = TIME_INTERVAL_ONEDAY
            self.interval_time = ONEDAY

    def model_slice(self, History_modle):
        '''
        按时间间隔对model切片，六十条数据，站定间隔1min， 2min， 24min
        :param history:
        :return:
        '''
        delay = int(Items.objects.using('zabbixdb').get(itemid=self.itemid).delay)
        time_interval = int(time.time() - self.slice_timer)
        history = History_modle.objects.using('zabbixdb').filter(Q(clock__gte=time_interval) & Q(itemid=self.itemid))
        history_list = []
        # for i in history:
        #    print i.value
        if self.timer == '1小时' and delay == 60:
            history_list = history
        elif self.timer == '1小时' and delay == 600:
            for his in history:
                for i in range(10):
                    history_list.append(his)
        elif self.timer == '2小时' and delay == 60:
            le = len(history)/2
            for i in range(le):
                history_list.append(history[2*i])
        elif self.timer == '2小时' and delay == 600:
            for his in history:
                for i in range(5):
                    history_list.append(his)
        elif self.timer == '1天' and delay == 60:
            le = len(history)/24
            for i in range(le):
                history_list.append(history[24*i])
        return history_list

    def chart_data(self, History_modle):
        '''
        获取项目某一时段所有数据
        :param History_modle: 数据表模型
        :param itemid: 项目id
        :return:
        '''
        history = self.model_slice(History_modle)
        # import datetime
        # s = datetime.datetime.now()
        # history = History_modle.objects.using('zabbixdb').filter(Q(clock=delay) & Q(itemid=self.itemid))
        # e = datetime.datetime.now()
        # print e-s
        clock = []
        value = []
        json_data = {}
        size = len(history)
        if size >= 59: #一小时/两小时/一天内无停机或停监测
            value_type = Items.objects.using('zabbixdb').get(itemid=self.itemid).value_type
            for histy in history:
                clock.append(self.timestamp_conversion(histy.clock))
                value.append(histy.value)
            if value_type != 1:
                value = json.dumps(value)


        elif size == 0: #一小时/两小时/一天内停机或停监测
            value_type = Items.objects.using('zabbixdb').get(itemid=self.itemid).value_type
            if value_type == 1: # history_str table
                count = self.items_count()*2
                h = History_modle.objects.using('zabbixdb').all().reverse()[:count]
                le = len(h)
                for i in range(le):
                    if h[le-i-1].itemid == self.itemid:
                        val = h[le-i-1].value
                        break
                value.append(val)
                timeArray = time.localtime(time.time())
                time_cur = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                clock.append(time_cur)
            else: # history or history_uint table
                tm = time.time()
                for i in range(60):
                    clock.append(self.timestamp_conversion(tm))
                    value.append(None)
                    tm -= self.interval_time
                clock.reverse()
                value = json.dumps(value)
        else: #一小时/两小时/一天内有开机或有监测
            value_type = Items.objects.using('zabbixdb').get(itemid=self.itemid).value_type
            if value_type == 1: #string data no chartshow it's a table
                delay = int(time.time()-3600*2)
                h = History_modle.objects.using('zabbixdb').filter(Q(clock__gte=delay) & Q(itemid=self.itemid))
                value.append(h[0].value)
                timeArray = time.localtime(h[0].clock)
                time_cur = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                clock.append(time_cur)
            else: #double or uint data
                cur_time = time.time()
                last_time = history[size-1].clock
                cl = int((cur_time-last_time)/self.interval_time)
                history_clock = []
                for histy in history: #获取一小时内所有监测时间
                    history_clock.append(histy.clock)
                if cl == 0: #获取最新监测单位时间
                    pass
                else:
                    last_time += cl*self.interval_time
                    if last_time > cur_time:
                        last_time -= self.interval_time
                j = 0
                for i in range(60):
                    if size-j-1 < 0:
                        break
                    if last_time - history[size-j-1].clock < 60:
                        clock.append(self.timestamp_conversion(history[size-j-1].clock))
                        value.append(history[size-j-1].value)
                        j += 1
                    else:
                        clock.append(self.timestamp_conversion(last_time))
                        value.append(history[size-j-1].value)
                    last_time -= self.interval_time
                clock.reverse()
                value.reverse()
                value = json.dumps(value)
        json_data['clock'] = clock
        json_data['value'] = json.dumps(value)
        return json_data

    def value_router(self):
        self.itemid = int(re.findall('(\d+)\/\d+\/$', self.url)[0])
        self.items = Items.objects.using('zabbixdb').get(itemid=self.itemid)
    def init_value_type(self):
        '''
        选表：History、HistoryUint等
        :return:
        '''
        self.value_type = self.items.value_type

    def get_items_name(self):
        # return TemporaryTable.objects.using('zabbixdb').get(tempid=self.itemid).name.encode('utf-8')
        return TemporaryTable.objects.get(tempid=self.itemid).name.encode('utf-8')

    def units_reset(self, json_data):
        '''
        单位及数值转化
        :param json_data: 数据包
        :return:
        '''
        hostid = self.items.hostid.hostid
        ip = Interface.objects.using('zabbixdb').get(hostid=hostid).ip.encode('utf-8')
        # name = self.get_items_name()
        name = 'Incoming traffic on interface NULL0'
        text_title = []
        # json_data = {}
        if self.timer == '1小时':
            text_title.append(ip + ':' + name + '(1h)')
        elif self.timer == '2小时':
            text_title.append(ip + ':' + name + '(2h)')
        elif self.timer == '1天':
            text_title.append(ip + ':' + name + '(1d)')
        json_data['text_title'] = text_title
        units = self.items.units
        if units == 'B' or units == 'bps':
            value = json_data['value']
            value = json.loads(json.loads(value))
            new_value = []

            for val in value:
                try:
                    if val > 1073741824:
                        new_value.append(round(float(val)/(1024*1024*1024), 2))
                        json_data['units'] = json.dumps('GB')
                    else:
                        new_value.append(round(float(val)/(1024*1024), 2))
                        json_data['units'] = json.dumps('MB')
                except:
                    new_value.append(val)
                    json_data['units'] = json.dumps('MB')
            value = json.dumps(json.dumps(new_value))
            json_data['value'] = value

        elif units == 'uptime' or units == 'unixtime':
            value = json_data['value']
            value = json.loads(json.loads(value))
            new_value = []
            for val in value:
                # if val is not None:
                #     ti = time.localtime(val)
                #     new_value.append(time.strftime('%Y-%m-%d %H:%M:%S', ti))
                # else:
                try:
                    new_value.append(val)
                except:
                    pass
            value = json.dumps(json.dumps(new_value))
            json_data['value'] = value
            json_data['units'] = json.dumps('')
        elif units == '%':
            value = json_data['value']
            value = json.loads(json.loads(value))
            new_value = []
            for val in value:
                try:
                    new_value.append(round(val, 2))
                except:
                    new_value.append(val)
            value = json.dumps(json.dumps(new_value))
            json_data['value'] = value
            json_data['units'] = json.dumps('%')
        else:
            json_data['units'] = json.dumps(units)
        return json_data

    def table_router(self):
        '''
        数据表路由，itemid寻表
        :param url:
        :return:
        '''
        json_data = None
        self.value_router()
        self.init_value_type()
        self.set_time_interval()
        if self.value_type == 0:
            json_data = self.chart_data(History)
        elif self.value_type == 1:
            json_data = self.chart_data(HistoryStr)
        elif self.value_type == 3:
            json_data = self.chart_data(HistoryUint)
        return self.units_reset(json_data)
