#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/25 16:11
# @Author  :
# @Site    :
# @File    : tabpage_data.py
# @Software: PyCharm

from ..common.datatables.views import BaseDatatableView
from constant import *
from models import *
from public_ways import PublicWays
import logging
from django.conf import settings
from django.db.models import Sum
from django.db.models import Q
logger = logging.getLogger(__name__)

class TabPageData(BaseDatatableView, PublicWays):
    model = TrendsUint #90天需修改model
    groupid = None
    pre_time = None
    last_time = None
    start_slice = None
    offset_slice = None
    daycount = 1

    columns = ['sheetid',
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
    order_columns = columns

    def set_groupid(self):
        pass

    def set_interface_list(self, groupid):
        '''
        生成出入itemid列表
        :param groupid: 用户id
        :return: 返回itemid列表
        '''
        in_list = list(SheetsInterface.objects.filter(client_id=groupid).values_list('in_itemid', flat=True))
        out_list = list(SheetsInterface.objects.filter(client_id=groupid).values_list('out_itemid', flat=True))
        return in_list, out_list

    def set_itemid_sql(self, in_itl, out_itl):
        '''
        设置出入itemid的sql
        :param in_itl: 入itemid列表
        :param out_itl:出itemid列表
        :return: 返回出入itemid的sql
        '''
        sql_in = Q()
        sql_out = Q()
        for i in range(len(in_itl)):
            sql_in |= Q(itemid=in_itl[i])
            sql_out |= Q(itemid=out_itl[i])

        return sql_in, sql_out

    def set_data(self):
        '''
        个参数初始化借口
        :return:
        '''
        self.set_groupid()
        self.incoming_interface_list, self.outgoing_interface_list = self.set_interface_list(self.groupid)
        self.pre_time, self.last_time = self.mutil_time_interval(self.daycount)

    def set_daycount(self):
        '''
        设置天数
        :return:
        '''
        self.daycount = self._querydict.get('search[value]', None)
        if self.daycount == '':
            self.daycount = 1
        else :
            self.daycount = int(self.daycount)
    def get_initial_queryset(self):
        self.set_data()
        self.in_sql, self.out_sql = self.set_itemid_sql(self.incoming_interface_list, self.outgoing_interface_list)
        sql = self.in_sql | self.out_sql
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return self.model.objects.using('zabbixdb').filter(sql & Q(clock__gte=int(self.pre_time)) & Q(clock__lt=int(self.last_time)))

    def paging(self, qs):
        """ Paging
        """
        if self.pre_camel_case_notation:
            limit = min(int(self._querydict.get('iDisplayLength', 10)), self.max_display_length)
            start = int(self._querydict.get('iDisplayStart', 0))
        else:
            limit = min(int(self._querydict.get('length', 10)), self.max_display_length)
            start = int(self._querydict.get('start', 0))

        # if pagination is disabled ("paging": false)
        self.drug_start = start
        if limit == -1:
            return qs
        self.start_slice = start
        self.offset_slice = start + limit
        return qs

    def get_page_datalist(self, qs, in_id, out_id):
        '''
        获取单页数据列表
        :param qs: 数据库句柄
        :param in_id: 进id列表
        :param out_id: 出id列表
        :return: 返回出入流量列表
        '''
        in_data = []
        out_data = []
        for i in range(len(in_id)):
            in_data.append(list(qs.filter(itemid=in_id[i]).values_list( 'value_max', flat=True)))
            out_data.append(list(qs.filter(itemid=out_id[i]).values_list( 'value_max', flat=True)))
        return in_data, out_data

    def set_time_column(self):
        '''
        时间设置
        :return:
        '''
        if self.daycount == 1:
            time_col = '近1天'
        elif self.daycount == 7:
            time_col = '近7天'
        elif self.daycount == 30:
            time_col = '近1个月'
        elif self.daycount == 90:
            time_col = '近3个月'
        return time_col

    def prepare_results(self, qs):
        if self.offset_slice > SheetsInterface.objects.filter(client_id=self.groupid).count():
            self.offset_slice = SheetsInterface.objects.filter(client_id=self.groupid).count()
        in_itemid_sql, out_itemid_sql = self.set_itemid_sql(self.incoming_interface_list[self.start_slice:self.offset_slice], self.outgoing_interface_list[self.start_slice:self.offset_slice])
        #各端口求和
        in_val_avg = qs.filter(in_itemid_sql).values('itemid').annotate(sum_value_avg=Sum('value_avg')).values('itemid', 'sum_value_avg')
        out_val_avg = qs.filter(out_itemid_sql).values('itemid').annotate(sum_value_avg=Sum('value_avg')).values('itemid', 'sum_value_avg')
        in_max_list, out_max_list =self.get_page_datalist(qs, self.incoming_interface_list[self.start_slice:self.offset_slice], self.outgoing_interface_list[self.start_slice:self.offset_slice])
        data = []
        for i in range(self.offset_slice-self.start_slice-1):
            in_val = in_val_avg[i]['sum_value_avg']
            out_val = out_val_avg[i]['sum_value_avg']
            if not in_max_list[i]:
                in_peak_rate = 0
            else:
                in_peak_rate = max(in_max_list[i])
            if not out_max_list[i]:
                out_peak_rate = 0
            else:
                out_peak_rate = max(out_max_list[i])
            in_val = round(float(in_val * 3600)/(SIZE*SIZE*SIZE*8), 2) #流入流量
            out_val = round(float(out_val * 3600)/(SIZE*SIZE*SIZE*8), 2) #流出流量

            total_val = in_val + out_val #总流量
            in_peak_rate = round(float(in_peak_rate)/(SIZE*SIZE), 2) #峰值流入速率
            out_peak_rate = round(float(out_peak_rate)/(SIZE*SIZE), 2) #峰值流出速率
            total_peak_rate = in_peak_rate + out_peak_rate #双向峰值速率
            in_average_rate = round(float(in_val_avg[i]['sum_value_avg']/(self.daycount*24*SIZE*SIZE)), 2) #流入速率(均值)
            out_average_rate = round(float(out_val_avg[i]['sum_value_avg']/(self.daycount*24*SIZE*SIZE)), 2) #流出速率(均值)
            total_average_rate = in_average_rate + out_average_rate #总速率

            bandwidth = SheetsInterface.objects.get(in_itemid=self.incoming_interface_list[self.start_slice+i]).bandwidth

            average_usage = max(in_average_rate, out_average_rate)/(bandwidth*SIZE) #带宽利用率
            peak_usage = max(in_peak_rate, out_peak_rate)/(bandwidth*SIZE) #峰值利用率
            average_usage = str(round(average_usage, 2) * 100) + '%'
            peak_usage = str(round(peak_usage, 2) * 100) + '%'

            #子端口数据生成
            self.dt = self.time_to_localtime(self.pre_time)
            sht = SheetsInterface.objects.get(in_itemid=self.incoming_interface_list[self.start_slice+i])
            time_col = self.set_time_column()
            temp = [self.incoming_interface_list[self.start_slice+i],
                     self.incoming_interface_list[self.start_slice+i],
                     time_col,
                     str(sht.ip) + '-' + str(sht.port_name),
                     out_val,
                     in_val,
                     round(total_val, 2),
                     out_peak_rate,
                     out_average_rate,
                     in_peak_rate,
                     in_average_rate,
                     round(total_peak_rate, 2),
                     total_average_rate,
                     average_usage,
                     peak_usage]
            data.append(temp)
        return data

    def get_context_data(self, *args, **kwargs):
        '''
            获取上下文数据
        :param args:
        :param kwargs:
        :return:
        '''
        try:
            self.initialize(*args, **kwargs)
            self.set_daycount()
            qs = self.get_initial_queryset()
            # number of records before filtering

            total_records = SheetsInterface.objects.filter(client_id=self.groupid).count()
            # qs = self.filter_queryset(qs)
            # number of records after filtering

            total_display_records = SheetsInterface.objects.filter(client_id=self.groupid).count()
            # qs = self.ordering(qs)
            qs = self.paging(qs)

            # prepare output data
            if self.pre_camel_case_notation:
                aaData = self.prepare_results(qs)

                ret = {'sEcho': int(self._querydict.get('sEcho', 0)),
                       'iTotalRecords': total_records,
                       'iTotalDisplayRecords': total_display_records,
                       'aaData': aaData
                       }
            else:
                data = self.prepare_results(qs)

                ret = {'draw': int(self._querydict.get('draw', 0)),
                       'recordsTotal': total_records,
                       'recordsFiltered': total_display_records,
                       'data': data
                       }
        except Exception as e:
            logger.exception(str(e))

            if settings.DEBUG:
                import sys
                from django.views.debug import ExceptionReporter
                reporter = ExceptionReporter(None, *sys.exc_info())
                text = "\n" + reporter.get_traceback_text()
            else:
                text = "\n异步获取数据,生成表格失败 !."

            if self.pre_camel_case_notation:
                ret = {'result': 'error',
                       'sError': text,
                       'text': text,
                       'aaData': [],
                       'sEcho': int(self._querydict.get('sEcho', 0)),
                       'iTotalRecords': 0,
                       'iTotalDisplayRecords': 0,}
            else:
                ret = {'error': text,
                       'data': [],
                       'recordsTotal': 0,
                       'recordsFiltered': 0,
                       'draw': int(self._querydict.get('draw', 0))}

        return ret
