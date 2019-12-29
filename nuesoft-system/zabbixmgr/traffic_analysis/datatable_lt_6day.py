#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/12 16:06
# @Author  :
# @Site    :
# @File    : datatable_lt_6day.py
# @Software: PyCharm


from set_variable_ways import SetVariable
from ..public_ways import PublicWays
from ..constant import *

class ResultLt6Day(SetVariable):

    def actual_data_prepare_results(self, qs):
        '''
        默认排序方法，重写数据打包方法, 小于7天(使用history_uint表)
        :param qs:
        :return:
        '''
        time_interval = self.set_interval(self.time_interval)
        data = []
        self.start *= time_interval
        self.offset *= time_interval
        actual_count = self.get_count()*time_interval
        if self.offset > actual_count:
            self.offset = int(actual_count)
        in_id = [self.in_itemid]
        out_id = [self.out_itemid]
        time_list = [self.pre_time, self.last_time]
        publicways = PublicWays()
        slice = [self.start, self.offset]
        in_list, out_list = publicways.single_port_data(qs, in_id, out_id, time_list, slice, 0)
        in_list = in_list[0]
        out_list = out_list[0]

        ti = self.pre_time + self.start*60
        n = 0
        for i in range(len(in_list)/time_interval):
            in_val = 0
            out_val = 0
            in_val_rate = 0
            out_val_rate = 0
            out_peak_rate = 0
            in_peak_rate = 0
            for j in range(time_interval):
                in_val += in_list[n+j]*60
                out_val += out_list[n+j]*60
                in_peak_rate = max(in_peak_rate, in_list[n+j])
                out_peak_rate = max(out_peak_rate, out_list[n+j])
                in_val_rate += in_list[n+j]
                out_val_rate += out_list[n+j]
            n += time_interval

            in_val = round(float(in_val)/(SIZE*SIZE*SIZE*8), 2) #流入流量
            out_val = round(float(out_val)/(SIZE*SIZE*SIZE*8), 2) #流出流量
            total_val = in_val + out_val #总流量
            in_peak_rate = round(float(in_peak_rate)/(SIZE*SIZE), 2) #峰值流入速率
            out_peak_rate = round(float(out_peak_rate)/(SIZE*SIZE), 2) #峰值流出速率
            total_peak_rate = in_peak_rate + out_peak_rate #双向峰值速率
            in_average_rate = round(float(in_val_rate/time_interval)/(SIZE*SIZE), 2) #流入速率(均值)
            out_average_rate = round(float(out_val_rate/time_interval)/(SIZE*SIZE), 2) #流出速率(均值)
            total_average_rate = in_average_rate + out_average_rate #总速率

            average_usage = max(in_average_rate, out_average_rate)/(self.bandwidth*SIZE) #带宽利用率
            peak_usage = max(in_peak_rate, out_peak_rate)/(self.bandwidth*SIZE) #峰值利用率
            average_usage = str(round(average_usage, 2) * 100) + '%'
            peak_usage = str(round(peak_usage, 2) * 100) + '%'
            t = publicways.time_to_localtime(ti)
            ti += 60*time_interval

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

            data.append(temp)
        return data

    def sort_way_one(self, qs):
        '''
        按出入流量、出入平均流量排序
        :return:
        '''
        time_interval = self.set_interval(self.time_interval)
        data = []
        self.start *= time_interval
        self.offset *= time_interval
        actual_count = self.get_count()*time_interval
        if self.offset > actual_count:
            self.offset = int(actual_count)

        in_id = [self.in_itemid]
        out_id = [self.out_itemid]
        time_list = [self.pre_time, self.last_time]
        publicways = PublicWays()
        l_slice = (self.last_time-self.pre_time)/60
        slice = [0, l_slice]
        in_list, out_list = publicways.single_port_data(qs, in_id, out_id, time_list, slice, 0)
        in_list = in_list[0]
        out_list = out_list[0]

        in_pack_list = []
        out_pack_list = []
        for i in range(len(in_list)/time_interval):
            in_sum_val = sum(in_list[i*time_interval:i*time_interval+time_interval]) #单位时间粒度流入流速
            try:
                in_max_val = max(in_list[i*time_interval:i*time_interval+time_interval]) #单位时间粒度峰值入流速
            except:
                in_max_val = 0
            out_sum_val = sum(out_list[i*time_interval:i*time_interval+time_interval]) #单位时间粒度流出流速
            try:
                out_max_val = max(out_list[i*time_interval:i*time_interval+time_interval]) #单位时间粒度峰值出流速
            except:
                out_max_val = 0
            total_val = in_sum_val + out_sum_val #单位时间粒度总流速
            total_peak_val = in_max_val + out_max_val #单位时间粒度双向峰值速率
            total_average_val = total_val/time_interval #单位时间粒度总速率
            in_pack_list.append((in_sum_val, in_max_val, i*time_interval, total_val, total_peak_val, total_average_val, 0))
            out_pack_list.append((out_sum_val, out_max_val, i*time_interval, total_val, total_peak_val, total_average_val, 1))

        ord = ['average_usage', '-average_usage', 'peak_usage', '-peak_usage']
        if self.sorting_order[0] in ord:
            nw_in_pack_list = self.usage_sort(in_pack_list, out_pack_list)
            in_val, out_val = self.sort(nw_in_pack_list, out_pack_list, time_interval)
        else :
            in_val, out_val = self.sort(in_pack_list, out_pack_list, time_interval)
        for i in range(len(in_val)):
            temp = self.data(in_val[i], out_val[i], time_interval, self.pre_time)
            data.append(temp)
        return data

