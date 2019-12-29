#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/10/27 15:45
# @Author  :
# @Site    :
# @File    : sheets_manager.py
# @Software: PyCharm

from models import *
import time
import datetime
from django.db.models import Q
import pandas as pd
import re
from decimal import Decimal as D
from django.db.models import Sum

ONEDAY = 3600*24 #second
SIZE = 1024

class CreateSheetsManager():

    # exl = pd.read_excel('C:\\Users\\Administrator\\Desktop\\111.xlsx' ,sep=',',encoding='utf-8', sheetname=2)
    #
    # exll = exl[exl.columns[3]] #4/3
    # ll = exl[exl.columns[5]]
    # # print ll
    # li = []
    # print exll

    # for i in range(len(exll)):
    #     e = None
    #     # print exll[i]
    #     if type(exll[i]) != float:
    #         exll[i] = exll[i].strip()
    #         # print exll[i]
    #         if re.match('^GE\d+\/\d+\/\d+', exll[i]):
    #             e = exll[i][2:]
    #             # print e
    #             e = 'GigabitEthernet' + str(e)
    #         elif re.match('^G\d+\/\d+\/\d+', exll[i]):
    #             e = exll[i][1:]
    #             e = 'GigabitEthernet' + str(e)
    #         elif re.match('^100.*', exll[i]):
    #             e = exll[i]
    #         else:
    #             continue
    #         e= e.strip()
    #         print e
    #         if AllNetworkInterface.objects.filter(interface_name=e).exists():
    #
    #             net = AllNetworkInterface.objects.filter(interface_name=e)
    #             for n in net:
    #                 p = re.findall('ip\:\s188\.1\.184\.(\d+)', n.name)[0]
    #                 if int(p) == 1 and re.match('^1.*', ll[i]):
    #                     ip = re.findall('ip\:\s(\d+\.\d+\.\d+\.\d+)', n.name)[0]
    #                     # print n.name
    #                     # SheetsInterface.objects.all().delete()
    #                     in_ite = Items.objects.using('zabbixdb').filter(Q(hostid=10300)
    #                                                                   & Q(key_field__contains='net.if.in[ifHCInOctets')
    #                                                                   & Q(name__contains='Interface %s'% e)
    #                                                                   & Q(flags=4))[0]
    #                     out_ite = Items.objects.using('zabbixdb').filter(Q(hostid=10300)
    #                                                                   & Q(key_field__contains='net.if.out[ifHCOutOctets')
    #                                                                   & Q(name__contains='Interface %s'% e)
    #                                                                   & Q(flags=4))[0]
    #                     SheetsInterface.objects.create(client='IDC出口' + str(ll[i]),
    #                                                   port_name=e, ip=ip,
    #                                                   in_itemid=in_ite.itemid,
    #                                                   out_itemid=out_ite.itemid,
    #                                                   table_id=1)
    #                 elif int(p) == 2 and re.match('^2.*', ll[i]):
    #                     ip = re.findall('ip\:\s(\d+\.\d+\.\d+\.\d+)', n.name)[0]
    #                     in_ite = Items.objects.using('zabbixdb').filter(Q(hostid=10288)
    #                                                                   & Q(key_field__contains='net.if.in[ifHCInOctets')
    #                                                                   & Q(name__contains='Interface %s'% e)
    #                                                                   & Q(flags=4))[0]
    #                     out_ite = Items.objects.using('zabbixdb').filter(Q(hostid=10288)
    #                                                                   & Q(key_field__contains='net.if.out[ifHCOutOctets')
    #                                                                   & Q(name__contains='Interface %s'% e)
    #                                                                   & Q(flags=4))[0]
    #                     SheetsInterface.objects.create(client='IDC出口' + str(ll[i]),
    #                                                   port_name=e, ip=ip,
    #                                                   in_itemid=in_ite.itemid,
    #                                                   out_itemid=out_ite.itemid,
    #                                                   table_id=1)
    #
    #                 # if int(p) == 61 and re.match('^1.*', ll[i]):
    #                 #     ip = re.findall('ip\:\s(\d+\.\d+\.\d+\.\d+)', n.name)[0]
    #                 #     in_ite = Items.objects.using('zabbixdb').filter(Q(hostid=10208) & Q(key_field='ifHCInOctets[%s]'% e) & Q(flags=4))[0]
    #                 #     out_ite = Items.objects.using('zabbixdb').filter(Q(hostid=10208) & Q(key_field='ifHCOutOctets[%s]'% e) & Q(flags=4))[0]
    #                 #     SheetsInterface.objects.create(client='IDC出口' + str(ll[i]), port_name=e, ip=ip, in_itemid=in_ite.itemid, out_itemid=out_ite.itemid, table_id=1)
    #                 # elif int(p) == 62 and re.match('^2.*', ll[i]):
    #                 #     ip = re.findall('ip\:\s(\d+\.\d+\.\d+\.\d+)', n.name)[0]
    #                 #     in_ite = Items.objects.using('zabbixdb').filter(Q(hostid=10117) & Q(key_field='ifHCInOctets[%s]'% e) & Q(flags=4))[0]
    #                 #     out_ite = Items.objects.using('zabbixdb').filter(Q(hostid=10117) & Q(key_field='ifHCOutOctets[%s]'% e) & Q(flags=4))[0]
    #                 #     SheetsInterface.objects.create(client='IDC出口' + str(ll[i]), port_name=e, ip=ip, in_itemid=in_ite.itemid, out_itemid=out_ite.itemid, table_id=1)
    #                 #
    #             li.append(e)
    #         else:
    #             pass
    #             print len(exll[i])
    #             print '-------------------'
    #             print len(e), e
    #             print exll[i], ll[i]
    #             print '-------------------'
    # print len(li)
    # print li

    incoming_interface_list = [] #流入端口itemid
    outgoing_interface_list = [] #流出端口itemid
    client_id = [] #关联id
    client = [] #客户名称
    sheets_interface = None #端口名对象
    total_average = 0 #总带宽
    dtime = None #日期

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
        return pre_time, last_time

    def get_itemid(self):
        '''
        获取所有网络端口流量进出itemid
        :return:
        '''
        interface = SheetsInterface.objects.all()
        for inter in interface:
            self.incoming_interface_list.append(inter.in_itemid)
            self.outgoing_interface_list.append(inter.out_itemid)
            self.client.append(inter.client)
            self.client_id.append(inter.client_id)
        all_inter = self.incoming_interface_list + self.outgoing_interface_list
        return all_inter

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

    def get_total_average(self):
        '''
        计算总带宽
        :return:
        '''
        SheetsManager.objects.create(update_time=self.dtime, client='IDC出口') #创建总出口, 按要求排第一
        SheetsManager.objects.create(update_time=self.dtime, client='IDC-BB出口')
        SheetsManager.objects.create(update_time=self.dtime, client='IDC-BR出口')
        SheetsManager.objects.create(update_time=self.dtime, client='IDC-BB03/04出口')
        SheetsManager.objects.create(update_time=self.dtime, client='IDC-BB05/06出口')
        self.sheets_interface = SheetsInterface.objects.all() #计算总带宽

    def prepre_results(self, qs):
        '''
        数据组装
        :return:
        '''
        self.get_total_average()

        interval = []
        for i in range(len(self.incoming_interface_list)):
            in_qs = qs.filter(itemid=self.incoming_interface_list[i])
            out_qs = qs.filter(itemid=self.outgoing_interface_list[i])

            l1 = len(in_qs)
            l2 = len(out_qs)
            #子端口数据组装
            in_val_data = in_qs.values('itemid').annotate(sum_score=Sum('value')).values('itemid', 'sum_score')[0]['sum_score']
            out_val_data = out_qs.values('itemid').annotate(sum_score=Sum('value')).values('itemid', 'sum_score')[0]['sum_score']

            in_val = round(float(in_val_data*60)/(SIZE*SIZE*SIZE*8), 2) #流入流量
            out_val = round(float(out_val_data*60)/(SIZE*SIZE*SIZE*8), 2) #流出流量
            total_val = in_val + out_val #总流量
            in_peak_rate = in_qs.order_by('value')[l1-1].value
            in_peak_rate = round(float(in_peak_rate)/(SIZE*SIZE), 2) #峰值流入速率
            out_peak_rate = out_qs.order_by('value')[l2-1].value
            out_peak_rate = round(float(out_peak_rate)/(SIZE*SIZE), 2) #峰值流出速率
            total_peak_rate = in_peak_rate + out_peak_rate #双向峰值速率
            in_average_rate = in_val_data/len(in_qs)
            in_average_rate = round(float(in_average_rate)/(SIZE*SIZE), 2) #流入速率(均值)
            out_average_rate = out_val_data/len(in_qs)
            out_average_rate = round(float(out_average_rate)/(SIZE*SIZE), 2) #流出速率(均值)
            total_average_rate = in_average_rate + out_average_rate #总速率

            bandwidth = self.sheets_interface[i].bandwidth #带宽利用率

            average_usage = max(in_average_rate, out_average_rate)/(bandwidth*SIZE) #带宽利用率
            peak_usage = max(in_peak_rate, out_peak_rate)/(bandwidth*SIZE) #峰值利用率
            average_usage = str(round(average_usage, 2) * 100) + '%'
            peak_usage = str(round(peak_usage, 2) * 100) + '%'

            #子端口数据生成
            init_sql = SheetsManager(update_time=self.dtime,
                                     client=self.client[i],
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


            interval.append(init_sql)
        SheetsManager.objects.bulk_create(interval)

        #子端口数据汇总
        for i in range(5):
            if i == 0:
                id_list = list(ClientGroup.objects.all().values_list('id', flat=True)) #BB
            elif i == 1:
                id_list = list(ClientGroup.objects.filter(type_id=1).values_list('id', flat=True)) #BB
            elif i == 2:
                id_list = list(ClientGroup.objects.filter(type_id=0).values_list('id', flat=True)) #BR
            elif i == 3:
                id_list = list(ClientGroup.objects.filter(Q(tailer_id='BB03') | Q(tailer_id='BB04')).values_list('id', flat=True)) #BB03/04
            elif i == 4:
                id_list = list(ClientGroup.objects.filter(Q(tailer_id='BB05') | Q(tailer_id='BB06')).values_list('id', flat=True)) #BB05/06
            sql = Q()
            for l in id_list:
                sql |= Q(client_id=l)
            client_name = list(SheetsInterface.objects.filter(sql).values_list('client', flat=True))
            shiter = SheetsInterface.objects.filter(sql)
            bth = shiter.values('client_id').annotate(sum_bandwidth=Sum('bandwidth')).values('sum_bandwidth')
            bandwidth = 0
            for b in bth:
                bandwidth += b['sum_bandwidth']
            sql = Q()
            for n in client_name:
                sql |= Q(client=n)
            sheets_mgr = SheetsManager.objects.filter(Q(update_time=self.dtime) & sql)

            total_out_val = D.from_float(0.00)
            total_in_val = D.from_float(0.00)
            val = D.from_float(0.00)
            total_out_peak_rate = D.from_float(0.00)
            total_out_average_rate = D.from_float(0.00)
            total_in_peak_rate = D.from_float(0.00)
            total_in_average_rate = D.from_float(0.00)
            peak_rate = D.from_float(0.00)
            average_rate = D.from_float(0.00)

            t = 0
            print total_out_val
            for sh in sheets_mgr:
                total_out_val += sh.out_val
                total_in_val += sh.in_val
                val += sh.total_val
                total_out_peak_rate += sh.out_peak_rate
                total_out_average_rate += sh.out_average_rate
                total_in_peak_rate += sh.in_peak_rate
                total_in_average_rate += sh.in_average_rate
                peak_rate += sh.total_peak_rate
                average_rate += sh.total_average_rate
            print total_out_val
            aver_usage = max(total_in_average_rate, total_out_average_rate)/D.from_float(bandwidth*SIZE)
            pea_usage = max(total_in_peak_rate, total_out_peak_rate)/D.from_float(bandwidth*SIZE)
            aver_usage = str(round(aver_usage, 2) * 100) + '%'
            pea_usage = str(round(pea_usage, 2) * 100) + '%'

            #总出口数据
            if i == 0:
                idc_client = 'IDC出口'
            elif i == 1:
                idc_client = 'IDC-BB出口'
            elif i == 2:
                idc_client = 'IDC-BR出口'
            elif i == 3:
                idc_client = 'IDC-BB03/04出口'
            elif i == 4:
                idc_client = 'IDC-BB05/06出口'
            SheetsManager.objects.filter(Q(client=idc_client) & Q(update_time=self.dtime)).update(out_val=total_out_val,
                                         in_val=total_in_val,
                                         total_val=val,
                                         out_peak_rate=total_out_peak_rate,
                                         out_average_rate=total_out_average_rate,
                                         in_peak_rate=total_in_peak_rate,
                                         in_average_rate=total_in_average_rate,
                                         total_peak_rate=peak_rate,
                                         total_average_rate=average_rate,
                                         average_usage=aver_usage,
                                         peak_usage=pea_usage)
