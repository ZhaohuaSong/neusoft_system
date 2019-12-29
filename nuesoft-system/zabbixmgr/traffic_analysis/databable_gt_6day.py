#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/12 16:48
# @Author  :
# @Site    :
# @File    : databable_gt_6day.py
# @Software: PyCharm

from set_variable_ways import SetVariable
from ..public_ways import PublicWays
from ..constant import *
from django.db.models import Q, Sum

class ResultGt6Day(SetVariable):

    def single_port_data_large_sixday(self, qs, in_list, out_list, time_list, slice, flag, table_flag=0):
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
            pre_clock = time_list[0] + slice[0]*60*60
            last_clock = time_list[0] + slice[1]*60*60
            val_avg = 'value_avg'
            val_max = 'value_max'
            interval = 60*60
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
        if qs.filter(Q(itemid=in_list[0]) & Q(clock__gte=pre_clock) & Q(clock__lt=last_clock)).count() == data_num:
            for k in range(len(in_list)):
                in_qs.append(list(qs.filter(Q(itemid=in_list[k]) & Q(clock__gte=pre_clock) & Q(clock__lt=last_clock)).values_list(val_avg, val_max, 'clock')))
                out_qs.append(list(qs.filter(Q(itemid=out_list[k]) & Q(clock__gte=pre_clock) & Q(clock__lt=last_clock)).values_list(val_avg, val_max, 'clock')))
        else: #这一天端口数据不齐全
            temp_in_qs = []
            temp_out_qs = []
            for k in range(len(in_list)):
                temp_in_qs.append(list(qs.filter(Q(itemid=in_list[k]) & Q(clock__gte=pre_clock) & Q(clock__lt=last_clock)).values_list(val_avg, val_max, 'clock')))
                temp_out_qs.append(list(qs.filter(Q(itemid=out_list[k]) & Q(clock__gte=pre_clock) & Q(clock__lt=last_clock)).values_list(val_avg, val_max, 'clock')))

            for m in range(len(temp_in_qs)):
                in_qs.append([])
                out_qs.append([])
            if len(temp_in_qs[0]) == 0: #简单错误处理，待完善
                in_qs[0] = [(0, 0, 0) for i in range(data_num)]
                out_qs[0] = [(0, 0, 0) for i in range(data_num)]
                return in_qs, out_qs
            n = 0

            temp_time = time_list[0]
            for i in range(data_num):
                try:
                    if temp_in_qs[0][n][2] - temp_time > interval: #判断所有端口此分钟是否都由数据
                        for t in range(len(temp_in_qs)):
                            in_qs[t].append((0, 0, 0))
                            out_qs[t].append((0, 0, 0))
                    else:
                        for t in range(len(temp_in_qs)):
                            try:
                                in_qs[t].append(temp_in_qs[t][n])
                                out_qs[t].append(temp_out_qs[t][n])
                            except:
                                in_qs[t].append((0, 0, 0))
                                out_qs[t].append((0, 0, 0))
                        n += 1
                except:
                    for t in range(len(temp_in_qs)):
                        in_qs[t].append((0, 0, 0))
                        out_qs[t].append((0, 0, 0))
                temp_time += interval
        return in_qs, out_qs

    # def actual_data_prepare_results_lager_sixday(self, qs):
    #     '''
    #     重写数据打包方法, 大于7天(使用trends_uint表)
    #     :param qs:
    #     :return:
    #     '''
    #     data = []
    #     actual_count = self.get_count()
    #     if self.offset > actual_count:
    #         self.offset = int(actual_count)
    #
    #     in_id = [self.in_itemid]
    #     out_id = [self.out_itemid]
    #     time_list = [self.pre_time, self.last_time]
    #     slice = [self.start, self.offset]
    #     in_list, out_list = self.single_port_data_large_sixday(qs, in_id, out_id, time_list, slice, 0)
    #     in_list = in_list[0]
    #     out_list = out_list[0]
    #     print in_list
    #     ti = self.pre_time + self.start*60*60
    #     publicways = PublicWays()
    #     for i in range(len(in_list)):
    #         in_val = in_list[i][0]*3600
    #         out_val = out_list[i][0]*3600
    #         in_val_rate = in_list[i][0]
    #         out_val_rate = out_list[i][0]
    #         out_peak_rate = out_list[i][1]
    #         in_peak_rate = in_list[i][1]
    #
    #         in_val = round(float(in_val)/(SIZE*SIZE*SIZE*8), 2) #流入流量
    #         out_val = round(float(out_val)/(SIZE*SIZE*SIZE*8), 2) #流出流量
    #         total_val = in_val + out_val #总流量
    #         in_peak_rate = round(float(in_peak_rate)/(SIZE*SIZE), 2) #峰值流入速率
    #         out_peak_rate = round(float(out_peak_rate)/(SIZE*SIZE), 2) #峰值流出速率
    #         total_peak_rate = in_peak_rate + out_peak_rate #双向峰值速率
    #         in_average_rate = round(float(in_val_rate)/(SIZE*SIZE), 2) #流入速率(均值)
    #         out_average_rate = round(float(out_val_rate)/(SIZE*SIZE), 2) #流出速率(均值)
    #         total_average_rate = in_average_rate + out_average_rate #总速率
    #
    #         average_usage = max(in_average_rate, out_average_rate)/(self.bandwidth*SIZE) #带宽利用率
    #         peak_usage = max(in_peak_rate, out_peak_rate)/(self.bandwidth*SIZE) #峰值利用率
    #         average_usage = str(round(average_usage, 2) * 100) + '%'
    #         peak_usage = str(round(peak_usage, 2) * 100) + '%'
    #         t = publicways.time_to_localtime(ti)
    #         ti += 60*60
    #
    #         temp = [11,
    #                 22,
    #                 t,
    #                 self.cp_name, #self.union_name
    #                 out_val,
    #                 in_val,
    #                 round(total_val, 2), #
    #                 out_peak_rate,
    #                 out_average_rate,
    #                 in_peak_rate,
    #                 in_average_rate,
    #                 round(total_peak_rate, 2), #
    #                 round(total_average_rate, 2), #
    #                 average_usage,
    #                 peak_usage]
    #         data.append(temp)
    #     return data

    def sort_way_two(self, qs):
        data = []
        if self.time_interval == 3:
            ti_interval = 1
            time_interval = 60
        elif self.time_interval == 4:
            ti_interval = 24
            time_interval = 1440

        self.start *= ti_interval #数据表实际索引
        self.offset *= ti_interval #数据表实际索引
        actual_count = self.get_count()*ti_interval #页面表格数据总量
        if self.offset > actual_count:
            self.offset = int(actual_count)
        in_id = [self.in_itemid]
        out_id = [self.out_itemid]
        time_list = [self.pre_time, self.last_time]
        l_slice = (self.last_time-self.pre_time)/(60*60)
        slice = [0, l_slice]
        in_list, out_list = self.single_port_data_large_sixday(qs, in_id, out_id, time_list, slice, 0)
        in_list = in_list[0]
        out_list = out_list[0]

        in_pack_list = []
        out_pack_list = []
        for i in range(len(in_list)/ti_interval):
            temp_in_lt = in_list[i*ti_interval:i*ti_interval+ti_interval]
            temp_out_lt = out_list[i*ti_interval:i*ti_interval+ti_interval]
            in_sum_val = map(sum, zip(*temp_in_lt))[0]
            in_max_val = map(max, zip(*temp_in_lt))[1]
            out_sum_val = map(sum, zip(*temp_out_lt))[0]
            out_max_val = map(max, zip(*temp_out_lt))[1]
            total_val = in_sum_val + out_sum_val
            total_peak_val = in_max_val + out_max_val
            total_average_val = total_val/ti_interval
            in_pack_list.append((in_sum_val, in_max_val, i*time_interval, total_val, total_peak_val, total_average_val))
            out_pack_list.append((out_sum_val, out_max_val, i*time_interval, total_val, total_peak_val, total_average_val))
        # in_val, out_val = self.sort(in_pack_list, out_pack_list, ti_interval)

        ord = ['average_usage', '-average_usage', 'peak_usage', '-peak_usage']
        if self.sorting_order[0] in ord:
            nw_in_pack_list = self.usage_sort(in_pack_list, out_pack_list)
            in_val, out_val = self.sort(nw_in_pack_list, out_pack_list, ti_interval)
        else :
            in_val, out_val = self.sort(in_pack_list, out_pack_list, ti_interval)
        for i in range(len(in_val)):
            temp = self.data(in_val[i], out_val[i], time_interval, self.pre_time)
            data.append(temp)
        return data
