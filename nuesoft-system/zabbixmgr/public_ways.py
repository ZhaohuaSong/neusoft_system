#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/11/22 16:56
# @Author  :
# @Site    :
# @File    : public_ways.py
# @Software: PyCharm

import datetime
import time
from django.db.models import Q

ONEDAY = 3600*24

class PublicWays():
    def time_interval(self, date):
        '''
        获取昨天格式化日期(就一天)
        :return:
        '''
        dt = datetime.datetime.now().strftime("%Y-%m-%d")
        timeArray = time.strptime(str(dt), "%Y-%m-%d")
        #转换成时间戳
        timestamp = time.mktime(timeArray)
        pre_time = timestamp - ONEDAY*date
        last_time = timestamp -ONEDAY*(date-1)
        return int(pre_time), int(last_time)

    def mutil_time_interval(self, date):
        '''
        获取多天格式化日期
        :param date:
        :return:
        '''
        dt = datetime.datetime.now().strftime("%Y-%m-%d")
        timeArray = time.strptime(str(dt), "%Y-%m-%d")
        #转换成时间戳
        timestamp = time.mktime(timeArray)
        pre_time = timestamp - ONEDAY*(date)
        last_time = timestamp
        return int(pre_time), int(last_time)

    def time_to_localtime(self, time_interval):
        '''
        时间戳转标准时间
        :param time_interval:
        :return:
        '''
        t = time.localtime(time_interval)
        t = time.strftime("%Y-%m-%d %H:%M:%S", t)
        return t

    def localtime_to_time_standard(self, lot):
        '''
        标准时间转时间戳
        :param lot:
        :return:
        '''
        timeArray = time.strptime(str(lot), "%Y-%m-%d %H:%M:%S")
        #转换成时间戳
        timestamp = time.mktime(timeArray)
        return int(timestamp)

    def localtime_to_time(self, timeArry):
        '''

        :param timeArry: '20171129
        :return:
        '''
        timeArry = timeArry[0:4] + '-' + timeArry[4:6] + '-' + timeArry[6:8]
        t = time.strptime(timeArry, "%Y-%m-%d")
        y,m,d = t[0:3]
        timestring = datetime.datetime(y,m,d)
        timestring = time.mktime(time.strptime(str(timestring), '%Y-%m-%d %H:%M:%S'))
        return int(timestring)

    def select_client_data(self, qs, in_list, out_list, time_list):
        '''
        一次性抓取所有用户数据，避免频繁访问数据库
        :param self:
        :param qs: 数据库描述符
        :param in_list:  流入端口列表
        :param out_list:  流出端口列表
        :param time_list:  起止时间列表
        :return: 返回起止时间数据列表(缺失数据0填补)
        '''
        in_qs = []
        out_qs = []
        cl = []
        data_num = int((time_list[1]-time_list[0])/60) #1天数量(间隔1min)
        if qs.filter(itemid=in_list[0]).count() == data_num: #所有端口这一天数据齐全
        # if len(in_qs) != 0:
            for k in range(len(in_list)):
                in_qs.append(list(qs.filter(itemid=in_list[k]).values_list('value', flat=True)))
                out_qs.append(list(qs.filter(itemid=out_list[k]).values_list('value', flat=True)))
        else: #这一天端口数据不齐全
            temp_in_qs = []
            temp_out_qs = []
            for k in range(len(in_list)):
                temp_in_qs.append(list(qs.filter(itemid=in_list[k]).values_list('value', 'clock')))
                temp_out_qs.append(list(qs.filter(itemid=out_list[k]).values_list('value', 'clock')))

            for m in range(len(temp_in_qs)):
                in_qs.append([])
                out_qs.append([])
            # if len(temp_in_qs[0]) == 0: #简单错误处理，待完善
            #     return in_qs, out_qs

            n = 0
            temp_time = time_list[0]
            for i in range(data_num):
                try:
                    f = 0
                    if temp_in_qs[0][n][1] - temp_time > 60: #判断所有端口此分钟是否都由数据
                        f = -1
                    else:
                        n += 1

                    if f == -1: #此分钟有一个端口无数据
                        for t in range(len(temp_in_qs)):
                            in_qs[t].append(0)
                            out_qs[t].append(0)
                    else: #此分钟全部端口都由数据
                        for t in range(len(temp_in_qs)):
                            try:
                                in_qs[t].append(temp_in_qs[t][n][0])
                                out_qs[t].append(temp_out_qs[t][n][0])
                            except:
                                in_qs[t].append(0)
                                out_qs[t].append(0)

                except:
                    for t in range(len(temp_in_qs)):
                        in_qs[t].append(0)
                        out_qs[t].append(0)
                temp_time += 60
        return in_qs, out_qs #返回的只有value字段数据

    def single_port_data(self, qs, in_list, out_list, time_list, slice, flag, table_flag=0):
        '''
        抓取端口一页数据加载至页面表格
        :param self:
        :param qs: 数据库描述符
        :param in_list:  流入端口列表
        :param out_list:  流出端口列表
        :param time_list:  起止时间列表
        :return: 返回起止时间数据列表(缺失数据0填补)
        '''
        in_qs = []
        out_qs = []
        if flag == 0: #表格数据标志
            data_num = int(slice[1]-slice[0])
            pre_clock = time_list[0] + slice[0]*60
            last_clock = time_list[0] + slice[1]*60
            val = 'value'
            interval = 60
        elif flag == 1: #图表标志
            if table_flag == 0:
                interval = 60*60
                val = 'value_max'
            elif table_flag == 1:
                interval = 60
                val = 'value'
            data_num = int((time_list[1]-time_list[0])/interval)
            pre_clock = time_list[0]
            last_clock = time_list[1]
        # if len(qs.filter(itemid=in_list[0]).values_list('value', flat=True)) == data_num: #所有端口这一天数据齐全(不严谨)
        # cccc = pre_clock
        # for i in range(22):
        #     if cccc > last_clock:
        #         break
        #     print qs.filter(Q(itemid=in_list[0]) & Q(clock__gte=cccc) & Q(clock__lt=cccc+86400)).count()
        #     cccc += 86400
        # print qs.filter(Q(itemid=in_list[0]) & Q(clock__gte=pre_clock) & Q(clock__lt=last_clock)).count(), 'qqqqqqqqqqqqq'
        # print data_num, 'uuuuuuuuuuuuu'
        if qs.filter(Q(itemid=in_list[0]) & Q(clock__gte=pre_clock) & Q(clock__lt=last_clock)).count() == data_num: #这一天端口数据齐全
            for k in range(len(in_list)):
                in_qs.append(list(qs.filter(Q(itemid=in_list[k]) & Q(clock__gte=pre_clock) & Q(clock__lt=last_clock)).values_list(val, flat=True)))
                out_qs.append(list(qs.filter(Q(itemid=out_list[k]) & Q(clock__gte=pre_clock) & Q(clock__lt=last_clock)).values_list(val, flat=True)))
        else: #这一天端口数据不齐全
            temp_in_qs = []
            temp_out_qs = []
            for k in range(len(in_list)):
                temp_in_qs.append(list(qs.filter(Q(itemid=in_list[k]) & Q(clock__gte=pre_clock) & Q(clock__lt=last_clock)).values_list(val, 'clock')))
                temp_out_qs.append(list(qs.filter(Q(itemid=out_list[k]) & Q(clock__gte=pre_clock) & Q(clock__lt=last_clock)).values_list(val, 'clock')))
            for m in range(len(temp_in_qs)):
                in_qs.append([])
                out_qs.append([])
            if len(temp_in_qs[0]) == 0: #简单错误处理，待完善
                in_qs[0] = [0 for i in range(data_num)]
                out_qs[0] = [0 for i in range(data_num)]
                return in_qs, out_qs

            n = 0
            temp_time = time_list[0]
            for i in range(data_num):
                try:
                    f = 0
                    if temp_in_qs[0][n][1] - temp_time > interval: #判断所有端口此分钟是否都由数据
                        for t in range(len(temp_in_qs)):
                            in_qs[t].append(temp_in_qs[t][n][0])
                    else: #此分钟全部端口都由数据
                        for t in range(len(temp_in_qs)):
                            try:
                                in_qs[t].append(temp_in_qs[t][n][0])
                                n += 1
                            except:
                                in_qs[t].append(0)
                except:
                    for t in range(len(temp_in_qs)):
                        in_qs[t].append(0)
                temp_time += interval

            n = 0
            temp_time = time_list[0]
            for i in range(data_num):
                try:
                    f = 0
                    if temp_in_qs[0][n][1] - temp_time > interval: #判断所有端口此分钟是否都由数据
                        for t in range(len(temp_in_qs)):
                            out_qs[t].append(temp_out_qs[t][n][0])
                    else: #此分钟全部端口都由数据
                        for t in range(len(temp_in_qs)):
                            try:
                                out_qs[t].append(temp_out_qs[t][n][0])
                                n += 1
                            except:
                                out_qs[t].append(0)
                except:
                    for t in range(len(temp_in_qs)):
                        out_qs[t].append(0)
                temp_time += interval
        return in_qs, out_qs


