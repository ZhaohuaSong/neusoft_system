#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/12 16:18
# @Author  :
# @Site    :
# @File    : set_variable_ways.py
# @Software: PyCharm

from base import *
from ..models import *
from django.db.models import Q, Sum
from ..constant import *
from ..public_ways import *

class SetVariable(TrafficAnalysisBase):

    def set_columns(self):
        self.ordering_columns = ['sheetid',
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

        self.columns = ['itemid', 'itemid']
        self.order_columns = self.columns

    def get_itemid(self, id):
        '''
        根据id获取相关参数
        :param id:
        :return:
        '''
        port = SheetsInterface.objects.get(id=id)
        self.in_itemid = port.in_itemid
        self.out_itemid = port.out_itemid
        self.cp_name = port.port_name
        self.ip = port.ip
        client_id = port.client_id
        client_name = ClientGroup.objects.get(id=client_id).client_name
        self.union_name = client_name + ':' + self.ip + '-' + self.cp_name
        self.bandwidth = port.bandwidth

    def group_get_itemid(self, id):
        try:
            clt = ClientGroup.objects.get(id=id)
            clt_name = clt.client_name
            clientid = clt.id
            industry_id = clt.industry_id
            self.cp_name = clt_name
            self.in_itemid = ClientItemid.objects.get(Q(client_name=clt_name) & Q(id_type=0) & Q(industry_id=industry_id)).id
            self.out_itemid = ClientItemid.objects.get(Q(client_name=clt_name) & Q(id_type=1) & Q(industry_id=industry_id)).id
            self.bandwidth = SheetsInterface.objects.filter(client_id=clientid).values('client_id').annotate(sum_bandwidth=Sum('bandwidth')).values('sum_bandwidth')[0]['sum_bandwidth']
        except:
            self.cp_name = ''
            self.in_itemid = 1000
            self.out_itemid = 1000
            self.bandwidth = 0

    def table_conf(self):
        '''
        分表
        :return:
        '''
        # self.table_id = self._querydict.get('table_id')
        try:
            if int(self.table_id) == 0:
                self.table_flag = 0
            elif int(self.table_id) == 1:
                self.table_flag = 1
        except:
            self.table_flag = 0

    def get_url(self):
        pass

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

    def set_count(self, qs):
        '''
        设置数据量
        :param qs: 表描述符
        :return:
        '''
        intel = self.set_interval(self.time_interval)
        self.count = (self.last_time - self.pre_time)/(60*intel)

    def set_count_larger_sixday(self, qs):
        self.count = (self.last_time - self.pre_time)/(60*60)

    def get_count(self):
        '''
        获取数据量
        :return:
        '''
        return self.count

    def usage_sort(self, in_pack_list, out_pack_list):
        '''
        带宽利用率/峰值利用率排序方法
        :param in_pack_list:
        :param out_pack_list:
        :return:
        '''
        nw_pack_list = []
        if self.sorting_order[0] == 'average_usage' or self.sorting_order[0] == '-average_usage':
            index = 0
        elif self.sorting_order[0] == 'peak_usage' or self.sorting_order[0] == '-peak_usage':
            index = 1
        for i in range(len(in_pack_list)):
            if in_pack_list[i][index] <out_pack_list[i][index]:
                nw_pack_list.append(out_pack_list[i])
            else:
                nw_pack_list.append(in_pack_list[i])
        nw_pack_list.sort()
        # for i in range(len(nw_pack_list)):
        #     if nw_pack_list[i][-1] == 1:
        #         nw_pack_list[i] = filter(lambda x: x[2]==nw_pack_list[i][2], in_pack_list)[0]
        return nw_pack_list


    def sort(self, in_pack_list, out_pack_list, time_interval):
        '''
        需要全部排序，再切片定位某页
        :param in_pack_list: 切片列表
        :param out_pack_list:
        :param time_interval:
        :return:
        '''
        order = self.sorting_order[0]
        if order == 'in_val' or order == 'in_average_rate':
            in_pack_list.sort() #分类
            order_flag = 1
        elif order == '-in_val' or order == '-in_average_rate':
            in_pack_list.sort()
            in_pack_list.reverse()
            order_flag = 1
        elif order == 'out_val' or order == 'out_average_rate':
            out_pack_list.sort()
            order_flag = 2
        elif order == '-out_val' or order == '-out_average_rate':
            out_pack_list.sort()
            out_pack_list.reverse()
            order_flag = 2
        elif order == 'total_val':
            in_pack_list.sort(key=lambda x: x[3])
            out_pack_list.sort(key=lambda x: x[3])
            order_flag = 3
        elif order == '-total_val':
            in_pack_list.sort(key=lambda x: x[3])
            out_pack_list.sort(key=lambda x: x[3])
            in_pack_list.reverse()
            out_pack_list.reverse()
            order_flag = 3
        elif order == 'in_peak_rate':
            in_pack_list.sort(key=lambda x: x[1])
            order_flag = 4
        elif order == '-in_peak_rate':
            in_pack_list.sort(key=lambda x: x[1])
            in_pack_list.reverse()
            order_flag = 4
        elif order == 'out_peak_rate':
            out_pack_list.sort(key=lambda x: x[1])
            order_flag = 5
        elif order == '-out_peak_rate':
            out_pack_list.sort(key=lambda x: x[1])
            out_pack_list.reverse()
            order_flag = 5
        elif order == 'total_peak_rate':
            in_pack_list.sort(key=lambda x: x[4])
            out_pack_list.sort(key=lambda x: x[4])
            order_flag = 6
        elif order == '-total_peak_rate':
            in_pack_list.sort(key=lambda x: x[4])
            out_pack_list.sort(key=lambda x: x[4])
            in_pack_list.reverse()
            out_pack_list.reverse()
            order_flag = 6
        elif order == 'total_average_rate':
            in_pack_list.sort(key=lambda x: x[5])
            out_pack_list.sort(key=lambda x: x[5])
            order_flag = 7
        elif order == '-total_average_rate':
            in_pack_list.sort(key=lambda x: x[5])
            out_pack_list.sort(key=lambda x: x[5])
            in_pack_list.reverse()
            out_pack_list.reverse()
            order_flag = 7
        elif order == '-update_time':
            in_pack_list.reverse()
            out_pack_list.reverse()
            order_flag = 8
        elif order == 'average_usage' or order == 'peak_usage':
            order_flag = 9
        elif order == '-average_usage' or order == '-peak_usage':
            in_pack_list.reverse()
            order_flag = 9
        else:
            order_flag = 8

        start_index = self.start/time_interval
        offset_index = self.offset/time_interval

        in_val = []
        out_val = []
        if order_flag == 1 or order_flag == 4:
            in_val = in_pack_list[start_index:offset_index]
            out_val = []
            for i in range(len(in_val)): #通过相同索引排序
                for j in range(len(out_pack_list)):
                    if out_pack_list[j][2] == in_val[i][2]:
                        out_val.append(out_pack_list[j])
                        break
        elif order_flag == 2 or order_flag == 5:
            out_val = out_pack_list[start_index:offset_index]
            in_val = []
            for i in range(len(out_val)):
                for j in range(len(in_pack_list)):
                    if in_pack_list[j][2] == out_val[i][2]:
                        in_val.append(in_pack_list[j])
                        break
        elif order_flag == 3 or order_flag == 6 or order_flag == 7 or order_flag == 8:
            in_val = in_pack_list[start_index:offset_index]
            out_val = out_pack_list[start_index:offset_index]
        elif order_flag == 9:
            val_temp = in_pack_list[start_index:offset_index]
            in_val = []
            out_val = []
            for i in range(len(val_temp)):
                if val_temp[i][-1] == 0:
                    in_val.append(val_temp[i])
                    out_val.append(filter(lambda x: x[2]==val_temp[i][2], out_pack_list)[0])
                else:
                    in_val.append(filter(lambda x: x[2]==val_temp[i][2], in_pack_list)[0])
                    out_val.append(val_temp[i])
        return in_val, out_val

    def data(self, in_tup, out_tup, interval, pre_time):
        in_value = in_tup[0]
        out_value = out_tup[0]
        in_peak_rate = in_tup[1]
        out_peak_rate = out_tup[1]
        time_inter = in_tup[2]
        ti = pre_time + time_inter*60
        publicways = PublicWays()
        # in_val = round(float(in_value*interval*60)/(SIZE*SIZE*SIZE*8), 2) #流入流量
        in_val = round(float(in_value*60)/(SIZE*SIZE*SIZE*8), 2) #流入流量
        out_val = round(float(out_value*60)/(SIZE*SIZE*SIZE*8), 2) #流出流量
        total_val = in_val + out_val #总流量
        in_peak_rate = round(float(in_peak_rate)/(SIZE*SIZE), 2) #峰值流入速率
        out_peak_rate = round(float(out_peak_rate)/(SIZE*SIZE), 2) #峰值流出速率
        total_peak_rate = in_peak_rate + out_peak_rate #双向峰值速率
        in_average_rate = round(float(in_value)/(SIZE*SIZE*interval), 2) #流入速率(均值)
        out_average_rate = round(float(out_value)/(SIZE*SIZE*interval), 2) #流出速率(均值)
        total_average_rate = in_average_rate + out_average_rate #总速率

        average_usage = max(in_average_rate, out_average_rate)/(self.bandwidth*SIZE) #带宽利用率
        peak_usage = max(in_peak_rate, out_peak_rate)/(self.bandwidth*SIZE) #峰值利用率
        average_usage = str(round(average_usage, 2) * 100) + '%'
        peak_usage = str(round(peak_usage, 2) * 100) + '%'
        t = publicways.time_to_localtime(ti)
        ti += 60*60

        temp = [11,
                22,
                t,
                self.cp_name, #self.union_name
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
        return temp
