#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/11/8 16:43
# @Author  :
# @Site    :
# @File    : interval_datas.py
# @Software: PyCharm

# from sheets_manager import CreateSheetsManager
from models import *
import datetime
from django.db.models import Q
import time
import re
from constant import *
from public_ways import PublicWays
from django.db.models import Sum

class CreateIntervalDatas(PublicWays):

    incoming_interface_list = [] #流入端口itemid
    outgoing_interface_list = [] #流出端口itemid
    client_id = [] #关联id
    client = [] #客户名称
    sheets_interface = None #端口名对象
    clt_inter = True #默认用户存在端口

    def get_itemid(self):
        '''
        获取所有网络端口流量进出itemid
        :return:
        '''
        interface = SheetsInterface.objects.all()
        clg = ClientGroup.objects.all() #需考虑某用户无端口情况
        self.incoming_interface_list = []
        self.outgoing_interface_list = []
        for i in clg:
            in_temp = {}
            out_temp = {}
            in_temp[str(i.id)] = list(interface.filter(client_id=i.id).values_list('in_itemid', flat=True))
            out_temp[str(i.id)] = list(interface.filter(client_id=i.id).values_list('out_itemid', flat=True))
            if len(in_temp) != 0 and len(out_temp) != 0: #无端口用户不计算
                self.clt_inter = False
            self.incoming_interface_list.append(in_temp)
            self.outgoing_interface_list.append(out_temp)
        inter = list(interface.values_list('in_itemid', flat=True)) + list(interface.values_list('out_itemid', flat=True))
        return inter

    def time_interval(self):
        '''
        获取昨天格式化日期
        :return:
        '''
        self.dt = datetime.datetime.now().strftime("%Y-%m-%d")
        timeArray = time.strptime(str(self.dt), "%Y-%m-%d")
        #转换成时间戳
        timestamp = time.mktime(timeArray)
        pre_time = timestamp - ONEDAY
        last_time = timestamp
        t = time.localtime(pre_time)
        self.dtime = time.strftime("%Y-%m-%d", t)
        self.time = pre_time
        self.ptime = pre_time
        self.ltime = last_time
        return pre_time, last_time

    def get_initial_queryset(self):
        '''
        获取所有端口models对象
        :return:
        '''
        all_inter = self.get_itemid()
        sql = Q()
        for i in all_inter:
            sql |= Q(itemid=i)
        pre_time, last_time = self.time_interval()
        return HistoryUint.objects.using('zabbixdb').filter(Q(clock__gte=pre_time) & Q(clock__lte=last_time) & sql)

    def time_to_localtime(self, time_interval):
        '''
        时间戳转标准时间
        :param time_interval:
        :return:
        '''
        t = time.localtime(time_interval)
        t = time.strftime("%Y-%m-%d %H:%M:%S", t)
        return t

    def get_group_average(self, clt):
        '''
        获取对应组的带宽总量
        :return:
        '''
        sht = SheetsInterface.objects.filter(client_id=self.client_id[clt])
        bth = sht.values('client_id').annotate(sum_bandwidth=Sum('bandwidth')).values('sum_bandwidth')
        bandwidth = 0
        for b in bth:
            bandwidth += b['sum_bandwidth']
        return bandwidth

    def onemin_data(self, qs):
        '''
        1min数据组装
        :return:
        '''
        interval = []
        time_list = [self.time, self.time+ONEDAY]
        for k in range(len(self.incoming_interface_list)):
            in_args = self.incoming_interface_list[k] #可能为空，需考虑
            out_args = self.outgoing_interface_list[k]
            ti = self.time
######################################################################################################################
            interval = []
            in_li = in_args[in_args.keys()[0]]
            out_li = out_args[out_args.keys()[0]]
            sql1 = sql2 = Q()
            cl_name = ClientGroup.objects.get(id=int(in_args.keys()[0])).client_name
            industry_id = ClientGroup.objects.get(id=int(in_args.keys()[0])).industry_id
            in_clientid = ClientItemid.objects.get(Q(client_name=cl_name) & Q(id_type=0) & Q(industry_id=industry_id)).id
            out_clientid = ClientItemid.objects.get(Q(client_name=cl_name) & Q(id_type=1) & Q(industry_id=industry_id)).id
            for i in range(len(in_li)):
                sql1|= Q(itemid=in_li[i])
                sql2 |= Q(itemid=out_li[i])
            # t = 0
            in_group_list = []
            out_group_list = []
            ww = 0
            for i in range(len(in_li)):
                in_val = list(HistoryUint.objects.using('zabbixdb').filter(Q(itemid=in_li[i]) & Q(clock__gte=self.time) & Q(clock__lt=self.time+86400)).values_list('value', flat=True))
                out_val = list(HistoryUint.objects.using('zabbixdb').filter(Q(itemid=out_li[i]) & Q(clock__gte=self.time) & Q(clock__lt=self.time+86400)).values_list('value', flat=True))
                ck_in = list(HistoryUint.objects.using('zabbixdb').filter(Q(itemid=in_li[i]) & Q(clock__gte=self.time) & Q(clock__lt=self.time+86400)).values_list('clock', flat=True))
                ck_out = list(HistoryUint.objects.using('zabbixdb').filter(Q(itemid=out_li[i]) & Q(clock__gte=self.time) & Q(clock__lt=self.time+86400)).values_list('clock', flat=True))
                if in_clientid == 49:
                    ww += sum(in_val)
                    print ww
                if len(in_val) !=1440:
                    in_val_new = []
                    f = 0
                    try:
                        vv = ck_in[0]
                        for r in range(1440):
                            if r == 1440:
                                break
                            try:
                                if ck_in[f]-vv > 60:
                                    # print 'if', f
                                    in_val_new.append(in_val[f])
                                else:
                                    # print 'else', f
                                    try:
                                        in_val_new.append(in_val[f])
                                        f += 1
                                    except:
                                        in_val_new.append(0)
                            except:
                                in_val_new.append(in_val[f-1])
                            vv += 60
                    except:
                        in_val_new = [0 for i in range(1440)]
                    in_val = in_val_new
                if len(out_val) !=1440:
                    out_val_new = []
                    f = 0
                    try:
                        vv = ck_out[0]
                        for r in range(1440):
                            if r == 1440:
                                break
                            try:
                                if ck_out[f]-vv > 60:
                                    # print 'if', f
                                    out_val_new.append(out_val[f])
                                else:
                                    # print 'else', f
                                    try:
                                        out_val_new.append(out_val[f])
                                        f += 1
                                    except:
                                        out_val_new.append(0)
                            except:
                                out_val_new.append(out_val[f-1])
                            vv += 60
                    except:
                        out_val_new = [0 for i in range(1440)]
                    out_val = out_val_new
                ti = self.time
                in_group_list.append(in_val)
                out_group_list.append(out_val)
            # if in_args.keys()[0] == '22':
            #     for hh in in_group_list[0]:
            #         print hh, 'kkkkkkkkk'
            # industry_id = ClientItemid.objects.get(id=in_clientid).industry_id
            for i in range(len(in_group_list[0])):
                in_value = 0
                out_value = 0
                for j in range(len(in_group_list)):
                    # print i, j
                    in_value += in_group_list[j][i]
                    out_value += out_group_list[j][i]
                in_inter = GHistoryUint1Min(itemid=in_clientid, clock=ti, value=in_value, ns=int(in_args.keys()[0]), industry_id=industry_id)
                out_inter = GHistoryUint1Min(itemid=out_clientid, clock=ti, value=out_value, ns=int(out_args.keys()[0]), industry_id=industry_id)
                interval.append(in_inter)
                interval.append(out_inter)
                ti += 60
            GHistoryUint1Min.objects.bulk_create(interval)
            print k

    def group_history_5min_data(self):
        '''
        客户5min/1h/1d历史表生成（新）
        :return:
        '''
        in_itemid = ClientItemid.objects.filter(id_type=0).values_list('id', flat=True)
        out_itemid = ClientItemid.objects.filter(id_type=1).values_list('id', flat=True)
        # self.ptime = 1536336000
        # self.ltime = 1538928000

        for i in range(len(in_itemid)):
            ti = self.ptime
            cltgroup = []
            in_list = list(GHistoryUint1Min.objects.filter(Q(itemid=in_itemid[i]) & Q(clock__gte=self.ptime) & Q(clock__lt=self.ltime)).values_list('value', flat=True))
            out_list = list(GHistoryUint1Min.objects.filter(Q(itemid=out_itemid[i]) & Q(clock__gte=self.ptime) & Q(clock__lt=self.ltime)).values_list('value', flat=True))
            industry_id = ClientItemid.objects.get(id=in_itemid[i]).industry_id
            for j in range(len(in_list)/5):
                in_min_val = min(in_list[j*5:j*5+5])
                in_max_val = max(in_list[j*5:j*5+5])
                in_avg_val = sum(in_list[j*5:j*5+5])/len(in_list[j*5:j*5+5])

                out_min_val = min(out_list[j*5:j*5+5])
                out_max_val = max(out_list[j*5:j*5+5])
                out_avg_val = sum(out_list[j*5:j*5+5])/len(out_list[j*5:j*5+5])
                in_val = GHistoryUint5Min(itemid=in_itemid[i], clock=ti, value_min=in_min_val, value_max=in_max_val, value_avg=in_avg_val, value=in_list[j*5+4], industry_id=industry_id)
                out_val = GHistoryUint5Min(itemid=out_itemid[i], clock=ti, value_min=out_min_val, value_max=out_max_val, value_avg=out_avg_val, value=out_list[j*5+4], industry_id=industry_id)
                cltgroup.append(in_val)
                cltgroup.append(out_val)

                ti += 60*5

            GHistoryUint5Min.objects.bulk_create(cltgroup)
            print i

    def group_history_data(self, time_interval):
        '''
        客户1h/1d历史表生成（新）
        :param time_interval: 间隔
        :return:
        '''
        in_itemid = ClientItemid.objects.filter(id_type=0).values_list('id', flat=True)
        out_itemid = ClientItemid.objects.filter(id_type=1).values_list('id', flat=True)

        if time_interval == 12:
            get_model = GHistoryUint5Min
            set_model = GHistoryUint1Hour
            interval = 60
        elif time_interval == 24:
            get_model = GHistoryUint1Hour
            set_model = GHistoryUint1Day
            interval = 1440


        for i in range(len(in_itemid)):
            industry_id = ClientItemid.objects.get(id=in_itemid[i]).industry_id
            ti = self.ptime
            cltgroup = []
            in_max_list = list(get_model.objects.filter(Q(itemid=in_itemid[i]) & Q(clock__gte=self.ptime) & Q(clock__lt=self.ltime)).values_list('value_max', flat=True))
            in_avg_list = list(get_model.objects.filter(Q(itemid=in_itemid[i]) & Q(clock__gte=self.ptime) & Q(clock__lt=self.ltime)).values_list('value_avg', flat=True))
            in_min_list = list(get_model.objects.filter(Q(itemid=in_itemid[i]) & Q(clock__gte=self.ptime) & Q(clock__lt=self.ltime)).values_list('value_min', flat=True))
            out_max_list = list(get_model.objects.filter(Q(itemid=out_itemid[i]) & Q(clock__gte=self.ptime) & Q(clock__lt=self.ltime)).values_list('value_max', flat=True))
            out_avg_list = list(get_model.objects.filter(Q(itemid=out_itemid[i]) & Q(clock__gte=self.ptime) & Q(clock__lt=self.ltime)).values_list('value_avg', flat=True))
            out_min_list = list(get_model.objects.filter(Q(itemid=out_itemid[i]) & Q(clock__gte=self.ptime) & Q(clock__lt=self.ltime)).values_list('value_min', flat=True))

            for j in range(len(in_avg_list)/time_interval):
                in_min_val = min(in_min_list[j*time_interval:j*time_interval+time_interval])
                in_max_val = max(in_max_list[j*time_interval:j*time_interval+time_interval])
                in_avg_val = sum(in_avg_list[j*time_interval:j*time_interval+time_interval])/len(in_avg_list[j*time_interval:j*time_interval+time_interval])

                out_min_val = min(out_min_list[j*time_interval:j*time_interval+time_interval])
                out_max_val = max(out_max_list[j*time_interval:j*time_interval+time_interval])
                out_avg_val = sum(out_avg_list[j*time_interval:j*time_interval+time_interval])/len(out_avg_list[j*time_interval:j*time_interval+time_interval])
                in_val = set_model(itemid=in_itemid[i], clock=ti, value_min=in_min_val, value_max=in_max_val, value_avg=in_avg_val, industry_id=industry_id)
                out_val = set_model(itemid=out_itemid[i], clock=ti, value_min=out_min_val, value_max=out_max_val, value_avg=out_avg_val, industry_id=industry_id)
                cltgroup.append(in_val)
                cltgroup.append(out_val)

                ti += 60*interval

            set_model.objects.bulk_create(cltgroup)
            if interval == 60:
                print i, '5hour data'
            else:
                print i, '1day data'

    def interval_data(self, timeid, time_interval):
        '''
        5min/1h/1d数据生成通用接口
        :param timeid:时间间隔id
        :param time_interval:时间间隔5min、5*12min、12h
        :return:
        '''
        clientgroup = ClientGroup.objects.all()
        interval = []
        date_time = self.time_to_localtime(self.time)
        for k in range(len(clientgroup)):
            intervaldatas = list(IntervalDatas.objects.filter(Q(client_id=clientgroup[k].id) & Q(time_id=timeid) & Q(update_time__gte=date_time)).values_list('out_val',
                                                                                                                             'in_val',
                                                                                                                              'total_val',
                                                                                                                              'out_peak_rate',
                                                                                                                              'in_peak_rate',
                                                                                                                              'out_average_rate',
                                                                                                                              'in_average_rate',
                                                                                                                              'total_peak_rate',
                                                                                                                              'total_average_rate'))

            ti = self.time
            group_average = self.get_group_average(k)
            n = 0
            for i in range(len(intervaldatas)/time_interval):
                out_val = 0
                in_val = 0
                total_val = 0
                out_peak_rate = 0
                in_peak_rate = 0
                out_average_rate = 0
                in_average_rate = 0
                for j in range(time_interval):
                    out_val += intervaldatas[n+j][0]
                    in_val += intervaldatas[n+j][1]
                    total_val += intervaldatas[n+j][2]
                    out_peak_rate = max(out_peak_rate, intervaldatas[n+j][3])
                    in_peak_rate = max(in_peak_rate, intervaldatas[n+j][4])
                    out_average_rate += intervaldatas[n+j][5]
                    in_average_rate += intervaldatas[n+j][6]
                n += time_interval
                total_peak_rate = out_peak_rate + in_peak_rate
                out_average_rate /= time_interval
                in_average_rate /= time_interval
                total_average_rate = out_average_rate + in_average_rate
                average_usage = max(in_average_rate, out_average_rate)/(group_average*SIZE)
                peak_usage = max(in_peak_rate, out_peak_rate)/(group_average*SIZE)
                average_usage = str(round(average_usage, 2) * 100) + '%'
                peak_usage = str(round(peak_usage, 2) * 100) + '%'
                self.dt = self.time_to_localtime(ti)
                if timeid == 1:
                    ti += 60*5
                elif timeid == 2:
                    ti += 60*60
                elif timeid == 3:
                    ti += 60*60*24
                inte = IntervalDatas(client_id=self.client_id[k],
                             time_id=timeid+1,
                             update_time=self.dt,
                             client=self.client[k],
                             out_val=out_val,
                             in_val=in_val,
                             total_val=total_val,
                             out_peak_rate=out_peak_rate,
                             out_average_rate=out_average_rate,
                             in_peak_rate=in_peak_rate,
                             in_average_rate=in_average_rate,
                             total_peak_rate=total_peak_rate,
                             total_average_rate=total_average_rate,
                             average_usage=average_usage,
                             peak_usage=peak_usage)
                interval.append(inte)
        IntervalDatas.objects.bulk_create(interval)

    def get_group_data(self):
        '''
        获取用户组信息，名称、id
        :return:
        '''
        clt = ClientGroup.objects.all()
        self.client = list(clt.values_list('client_name', flat=True))
        self.client_id = list(clt.values_list('id', flat=True))

    def context_data(self):
        '''
        统一入口
        :return:
        '''
        qs = self.get_initial_queryset()
        self.get_group_data()
        self.onemin_data(qs)
        self.group_history_5min_data()
        self.group_history_data(ONEHOUR_INTERVAL)
        self.group_history_data(ONEDAY_INTERVAL)

        self.incoming_interface_list = []
        self.outgoing_interface_list = []
        self.client_id = [] #关联id
        self.client = [] #客户名称
        self.sheets_interface = None #端口名对象
        self.clt_inter = True #默认用户存在端口

        # self.interval_data(ONEMIN, FIVEMIN_INTERVAL) #5分钟间隔数据
        # self.interval_data(FIVEMIN, ONEHOUR_INTERVAL) #1小时间隔数据
        # self.interval_data(ONEHOUR, ONEDAY_INTERVAL) #一天时间间隔数据
