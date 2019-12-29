#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/9/5 9:50
# @Author  :
# @Site    :
# @File    : temporarydb.py
# @Software: PyCharm5
# @Function:

import re
from models import *
from django.db.models import Q
import time, datetime

class GetTableData():
    # def __init__(self, appl_id):
    #     self.applicationid = appl_id
    #     self.cur_itemid = 0
    #     self.history = None
    #     self.cur_delay = 0
    #     self.count = 0 #写入记录表的总项目数量
    #     self.temporarytable = None
    applicationid = None
    cur_itemid = 0
    history = None
    cur_delay = 0
    count = 0 #写入记录表的总项目数量
    temporarytable = None

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
            self.count += len(items)

    def value_trans(self, hist):

        units = Items.objects.using('zabbixdb').get(itemid=hist.itemid).units
        if units == '%':
            value = round(hist.value, 2)
            value = str(value) + ' %'
        elif units == 'B'or units == 'bps':
            if hist.value > 1073741824:
                value = round(float(hist.value)/(1024*1024*1024), 2)
                value = str(value) + ' GB'
            else:
                value = round(float(hist.value)/(1024*1024), 2)
                value = str(value) + ' MB'
        elif units == 'uptime' or units == 'unixtime':
            value = time.localtime(hist.value)
            value = time.strftime('%Y-%m-%d %H:%M:%S', value)
        else:
            value = hist.value
            value = str(value) + ' ' + units
        return value

    def table_data(self, History_model):
        '''
        过滤最接近当前时间的数据
        :param History_model: 一切片的model
        :return:
        '''
        # data = []
        # for hist in self.history:
        #     if hist.itemid == self.cur_itemid:
        #         if len(data) == 0:
        #             data.append(self.value_trans(hist))
        #             data.append(hist.clock)
        #         elif len(data) != 0:
        #             if data[1] < hist.clock:
        #                 data[0] = self.value_trans(hist)
        #                 data[1] = hist.clock
        # print data
        # if len(data) != 0:
        #     return data
        # else:
        #数据不存在，扩大范围
        temp_clock = []
        try:
            #数据存在
            try:
                de = int(self.cur_delay)
                de *=2
            except:
                if self.cur_delay[-1] == 'm':
                    de = 2*60*int(self.cur_delay[:-1])
                elif self.cur_delay[-1] == 'h':
                    de = 2*3600*int(self.cur_delay[:-1])

            delay = int(time.time())-int(de)
            self.history = History_model.objects.using('zabbixdb').filter(Q(clock__gte=delay) & Q(itemid=self.cur_itemid))
            for hisuint in self.history:
                if len(temp_clock) == 0:
                    temp_clock.append(self.value_trans(hisuint))
                    temp_clock.append(hisuint.clock)
                else:
                    if temp_clock[1] < hisuint.clock:
                        temp_clock[0] = self.value_trans(hisuint)
                        temp_clock[1] = hisuint.clock
            if len(temp_clock) != 0:
                return temp_clock
            else:
                temp_clock.append('暂无数据')
                temp_clock.append(time.time())
                return temp_clock
        except:
            temp_clock.append('暂无数据')
            temp_clock.append(time.time())
            return temp_clock

    def choose_table(self, History_model):
        '''
        对表切片
        :param History_model: 表
        :return:
        '''
        self.history = History_model.objects.using('zabbixdb').all().reverse()[:3]
        # print self.history[0].value, self.history[0].clock, self.history[0].itemid
        # history_count = History_model.objects.using('zabbixdb').count()
        # if history_count > self.count:
        #     self.history = History_model.objects.using('zabbixdb').all()[history_count-self.count:]
        # else:
        #     self.history = History_model.objects.using('zabbixdb').all()

    def table_router(self, History_model):
        self.choose_table(History_model)
        data = self.table_data(History_model)
        val = str(data[0])
        timeArray = time.localtime(data[1])
        otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        clock = otherStyleTime
        return val, clock
        # return str(data[0]), otherStyleTime

    def get_data(self, qs):

        data = []
        for item_appl in qs:
            data_list = []
            self.cur_itemid = item_appl.itemid
            self.cur_delay = item_appl.delay
            data_list.append(self.cur_itemid)
            data_list.append(self.cur_itemid)
            try: #应用名获取
                name = item_appl.name
                key_field = item_appl.key_field
                na = re.findall('(\$+\d)', name)
                key_field = re.findall('\[(.+)\]', key_field)[0]
                key_field = key_field.split(',')
                for n in na:
                    name = name.replace(n, key_field[int(n[1:])-1])
                data_list.append(name)
            except:
                data_list.append(item_appl.name)
                # self.temporarytable.name = item_appl.itemid.name
                # temporary_name = item_appl.itemid.name

            if item_appl.value_type == 0: #value获取, history表
                val , clo = self.table_router(History)
            elif item_appl.value_type == 1: #value获取, history_str表
                val , clo = self.table_router(HistoryStr)
            elif item_appl.value_type == 3: #value获取, history_uint表
                val , clo = self.table_router(HistoryUint)
            data_list.append(val)
            data_list.append(clo)
            data_list.append(self.cur_itemid)
            # self.temporarytable.save(using='zabbixdb')
            data.append(data_list)
        return data

