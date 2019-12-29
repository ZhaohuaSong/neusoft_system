#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/11/30 16:41
# @Author  :
# @Site    :
# @File    : traffic_data.py
# @Software: PyCharm

from public_ways import PublicWays
from models import *
from constant import *
from django.db.models import Q
import time, datetime
SECOND_MONTH = 60*60*24*30

class GetChartData():
    id = None
    table_id = None
    pre_time = None #时间戳
    last_time = None #时间戳
    time_interval = None
    model = None
    in_itemid = None
    out_itemid = None

    def set_args(self, id_list):
        self.id = id_list[0]
        self.table_id = int(id_list[1])
        self.time_interval = int(id_list[4])
        public = PublicWays()
        self.pre_time = public.localtime_to_time(str(id_list[2]))
        self.last_time = public.localtime_to_time(str(id_list[3]))
        self.industry_id = id_list[5]

    def get_itemid(self):
        port = SheetsInterface.objects.get(id=self.id, industry_id=self.industry_id)
        self.in_itemid = port.in_itemid
        self.out_itemid = port.out_itemid

    def set_chart_interval(self):
        '''
        设置图表数据时间间隔
        :return:
        '''
        da = (self.last_time-self.pre_time)/(60*60*24) #天数
        if da <= 3:
            self.time_id = 2
            self.inter = 1
        elif da > 3 and da <= 7:
            self.time_id = 3
            self.inter = 5
        elif da > 7 and da <=120:
            self.time_id = 4
            self.inter = 60
        elif da > 120:
            self.inter =1440

    def init_queryset(self):
        if self.table_id == 0:#用户
            self.set_chart_interval()
            time_perior = (self.last_time-self.pre_time)/(60*60*24)
            if time_perior > 3:
                self.table_flag = 0
                self.model = GHistoryUint1Hour
            else:
                self.table_flag = 1
                self.model = GHistoryUint1Min

            try:
                clt_name = ClientGroup.objects.get(id=self.id).client_name
                self.in_itemid = ClientItemid.objects.get(Q(client_name=clt_name) & Q(id_type=0)).id
                self.out_itemid = ClientItemid.objects.get(Q(client_name= clt_name) & Q(id_type=1)).id
                print self.in_itemid, self.pre_time, self.last_time
            except:
                self.in_itemid = 1000
                self.out_itemid = 1000
            sql = Q()
            sql |= Q(itemid=self.in_itemid)
            sql |= Q(itemid=self.out_itemid)
            return self.model.objects.filter(Q(clock__gte=self.pre_time) & Q(clock__lt=self.last_time) & sql & Q(industry_id=self.industry_id))
########################################################################################
        elif self.table_id == 1:#端口
            time_perior = (self.last_time-self.pre_time)/(60*60*24)
            if time_perior > 3:
                self.table_flag = 0
                self.model = TrendsUint
            else:
                self.table_flag = 1
                self.model = HistoryUint

            self.get_itemid()
            sql = Q()
            sql |= Q(itemid=self.in_itemid)
            sql |= Q(itemid=self.out_itemid)
            return self.model.objects.using('zabbixdb').filter(Q(clock__gte=self.pre_time) & Q(clock__lt=self.last_time) & sql)

    def set_interval(self, inter_val):
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

    def set_hourti(self):
        itl = (self.last_time-self.pre_time)/SECOND_MONTH
        if itl < 3:
            self.hour_ti = 1
        elif itl >=3 and itl < 4:
            self.hour_ti = 4
        elif itl >= 4 and itl < 5:
            self.hour_ti = 8
        elif itl >= 5 and itl < 6:
            self.hour_ti = 12
        elif itl >=6:
            self.hour_ti = 24

    def interface_treat_data(self, qs):
        time_interval = self.set_interval(self.time_interval)
        in_id = [self.in_itemid]
        out_id = [self.out_itemid]
        time_list = [self.pre_time, self.last_time]
        publicways = PublicWays()
        slice = [0, self.count/2]
        in_list, out_list = publicways.single_port_data(qs, in_id, out_id, time_list, slice, 1, table_flag=self.table_flag)
        in_list = in_list[0]
        out_list = out_list[0]

        ti = self.pre_time
        n = 0
        in_peak_rate_list = []
        out_peak_rate_list = []
        clock_list = []
        #一下为图标数据，从所有数据按一定间隔抽取部分较大的数据，否则过载
        if self.table_flag == 1: #3天内
            for i in range(len(in_list)/time_interval):
                try:
                    in_peak_rate = max(in_list[i*time_interval: i*time_interval+time_interval])
                except:
                    in_peak_rate = 0
                try:
                    out_peak_rate = max(out_list[i*time_interval: i*time_interval+time_interval])
                except:
                    out_peak_rate = 0
                in_peak_rate = round(float(in_peak_rate)/(SIZE*SIZE*SIZE), 2) #峰值流入速率
                out_peak_rate = round(float(out_peak_rate)/(SIZE*SIZE*SIZE), 2) #峰值流出速率
                in_peak_rate_list.append(in_peak_rate)
                out_peak_rate_list.append(out_peak_rate)
                t = publicways.time_to_localtime(ti)
                t = time.localtime(ti)
                t = time.strftime("%y-%m-%d %H:%M", t)
                clock_list.append(t)
                ti += 60*time_interval
        elif self.table_flag == 0:
            self.set_hourti()
            n = 0
            for i in range(len(in_list)/self.hour_ti):
                in_peak_rate = 0
                out_peak_rate = 0
                for j in range(self.hour_ti):
                    in_peak_rate = max(in_peak_rate, in_list[n+j])
                    out_peak_rate = max(out_peak_rate, out_list[n+j])
                n += self.hour_ti
                in_peak_rate = round(float(in_peak_rate)/(SIZE*SIZE*SIZE), 2) #峰值流入速率
                out_peak_rate = round(float(out_peak_rate)/(SIZE*SIZE*SIZE), 2) #峰值流出速率
                in_peak_rate_list.append(in_peak_rate)
                out_peak_rate_list.append(out_peak_rate)
                t = publicways.time_to_localtime(ti)
                t = time.localtime(ti)
                t = time.strftime("%Y-%m-%d %H:%M:%S", t)
                clock_list.append(t)
                ti += 60*60
        in_avg = sum(in_list)/((SIZE*SIZE*SIZE)*len(in_list))
        out_avg = sum(out_list)/((SIZE*SIZE*SIZE)*len(out_list))
        return in_peak_rate_list, out_peak_rate_list, clock_list, in_avg, out_avg

####################################################################################
#待删
    def set_minti(self):
        itl = (self.last_time-self.pre_time)/SECOND_MONTH
        if itl < 2:
            self.min_ti = 1
        elif itl >=2 and itl < 3:
            self.min_ti = 5
        elif itl >= 3 and itl < 6:
            self.min_ti = 720
        elif itl >= 6:
            self.min_ti = 1440

    def client_treat_data(self, qs):
        in_peak_rate_list = []
        out_peak_rate_list = []
        clock_list = []
        self.set_minti()
        public = PublicWays()
        temp_time = public.time_to_localtime(self.pre_time)
        temp_time = datetime.datetime.strptime(str(temp_time), "%Y-%m-%d %H:%M:%S")

        # data_list = list(qs.values_list('in_peak_rate', 'out_peak_rate', 'update_time'))
        data_num = (self.last_time-self.pre_time)/(60*self.inter)

        if self.inter == 1:
            value_type = 'value'
        else:
            value_type = 'value_max'
        in_data_list = list(qs.filter(itemid=self.in_clientid).values_list(value_type, flat=True))
        out_data_list = list(qs.filter(itemid=self.out_clientid).values_list(value_type, flat=True))
        ck_list = list(qs.filter(itemid=self.in_clientid).values_list('clock', flat=True))
        first_clock = ck_list[0]
        t_time = public.time_to_localtime(first_clock)
        t_time = datetime.datetime.strptime(str(t_time), "%Y-%m-%d %H:%M:%S")

        if len(in_data_list) == data_num:
            for i in range(len(in_data_list)):
                in_peak_rate_list.append(round(float(in_data_list[i])/(SIZE*SIZE*SIZE), 2))
                out_peak_rate_list.append(round(float(out_data_list[i])/(SIZE*SIZE*SIZE), 2))
                clock_list.append(t_time)
                t_time += datetime.timedelta(minutes=self.inter)
        else:
            if len(in_data_list) == 0: #简单错误处理，待完善
                for i in range(data_num):
                    in_peak_rate_list.append(float(0))
                    out_peak_rate_list.append(float(0))
                    clock_list.append(temp_time)
                    temp_time += datetime.timedelta(minutes=self.inter)
            else:
                n = 0
                new_data_list = []
                tp_time = public.localtime_to_time_standard(temp_time)
                for i in range(data_num):
                    try:
                        # ck_time = public.localtime_to_time_standard(ck_list[n])
                        ck_time = ck_list[n]
                        if (ck_time - tp_time) == 0: #有数据
                            t = public.time_to_localtime(ck_list[n])
                            t = datetime.datetime.strptime(str(t), "%Y-%m-%d %H:%M:%S")
                            new_data_list.append((in_data_list[n], out_data_list[n], t))
                            n += 1
                        else: #没有数据
                            t = public.time_to_localtime(tp_time)
                            t = datetime.datetime.strptime(str(t), "%Y-%m-%d %H:%M:%S")
                            new_data_list.append((0, 0, t))
                    except:
                        t = public.time_to_localtime(tp_time)
                        t = datetime.datetime.strptime(str(t), "%Y-%m-%d %H:%M:%S")
                        new_data_list.append((0, 0, t))

                    tp_time += self.inter*60
                for i in range(len(new_data_list)):
                    in_peak_rate_list.append(float(new_data_list[i][0]/(SIZE*SIZE*SIZE)))
                    out_peak_rate_list.append(float(new_data_list[i][1]/(SIZE*SIZE*SIZE)))
                    clock_list.append(new_data_list[i][2])

        public = PublicWays()
        t = public.time_to_localtime(self.pre_time)
        p_time = datetime.datetime.strptime(str(t), "%Y-%m-%d %H:%M:%S")
        pt_list = []
        while p_time < clock_list[0]: #self.pre_time 前为空
            pt_list.append(p_time + datetime.timedelta(minutes=self.inter))
            p_time += datetime.timedelta(minutes=self.inter)
        if self.time_interval == 1:
            til = 1
        elif self.time_interval == 2:
            til = 5
        elif self.time_interval == 3:
            til = 60
        elif self.time_interval == 4:
            til = 1440
        t = public.time_to_localtime(self.last_time-til*60)
        l_time = datetime.datetime.strptime(str(t), "%Y-%m-%d %H:%M:%S")
        lt_list = []
        temp_time = clock_list[-1]
        while temp_time < l_time: #self.last_time后为空
            lt_list.append(temp_time + datetime.timedelta(minutes=self.inter))
            temp_time += datetime.timedelta(minutes=self.inter)
        pre_prl = [0 for i in range(len(pt_list))]
        last_prl = [0 for i in range(len(lt_list))]
        in_peak_rate_list = pre_prl + in_peak_rate_list + last_prl
        out_peak_rate_list = pre_prl + out_peak_rate_list + last_prl
        clock_list = pt_list + clock_list + lt_list
        clock_list = [str(clock_list[i]) for i in range(len(clock_list))]
        return in_peak_rate_list, out_peak_rate_list, clock_list
#####################################################################################################
    def get_data(self, id_list):
        self.set_args(id_list)
        qs = self.init_queryset()
        if self.table_id == 0:
            self.count = qs.count()
            return self.interface_treat_data(qs)
            # return self.client_treat_data(qs)
        else:
            self.count = qs.count()
            return self.interface_treat_data(qs)
