#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/11/21 16:05
# @Author  :
# @Site    :
# @File    : views_traffic_analysis.py
# @Software: PyCharm

import datetime
import json
import logging
import time

from django.conf import settings
from django.db.models import Q
from django.db.models import Sum
from django.http import HttpResponse
from django.views.generic import TemplateView

from constant import *
from models import *
from public_ways import PublicWays
from traffic_analysis.datatable import Datatable
from ..common.datatables.views import BaseDatatableView
from constant import get_industry_park
import re

logger = logging.getLogger(__name__)

class TrafficAnalysisList(TemplateView):
    template_name = 'zabbixmgr/traffic_analysis.list.html'

    # def get(self, request, *args, **kwargs):
    #     us = request.user.username
    #     industry_park =get_industry_park(us)
    #     context = self.get_context_data(**kwargs)
    #
    #     url = self.request.get_full_path()
    #     industry_id = int(re.findall('(\d+)$', url)[0])
    #     context['industry_id'] = industry_id
    #     context['industry_park'] = industry_park
    #     return self.render_to_response(context)

class TrafficAnalysisJson(Datatable, BaseDatatableView):
    '''
    Josn data
    '''

    def get_json(self, response):
        data_list = response['data']
        for data in data_list:
            if isinstance(data[2], datetime.datetime):
                data[2]=data[2].strftime("%m-%d %H:%M")
        return super(TrafficAnalysisJson, self).get_json(response)

    def get_initial_queryset(self):
        '''
        重写数据库初始化方法
        :return:
        '''
        if self.table_flag == 0: #用户表
            # self.model = IntervalDatas
            # return self.model.objects.filter(Q(update_time__gte=self.p_time) & Q(update_time__lt=self.l_time) & Q(client_id=self.id) & Q(time_id=self.time_interval))

            if (self.last_time-self.pre_time) > 518400: #判断是否大于7天(GHistoryUint1Hour保存一年数据)
                self.model = GHistoryUint1Hour
                self.sixday_druge = 0
            else:
                self.model = GHistoryUint1Min
                self.sixday_druge = 1

            self.group_get_itemid(self.id)
            sql = Q()
            sql |= Q(itemid=self.in_itemid)
            sql |= Q(itemid=self.out_itemid)
            return self.model.objects.filter(Q(clock__gte=self.pre_time) & Q(clock__lt=self.last_time) & sql & Q(industry_id=self.industry_id))
        elif self.table_flag == 1: #端口表
#################################################################################
            if (self.last_time-self.pre_time) > 518400: #判断是否大于7天(TrendsUint保存一年数据)
                self.model = TrendsUint
                self.sixday_druge = 0
            else:
                self.model = HistoryUint
                self.sixday_druge = 1

            self.get_itemid(self.id)
            sql = Q()
            sql |= Q(itemid=self.in_itemid)
            sql |= Q(itemid=self.out_itemid)
            return self.model.objects.using('zabbixdb').filter(Q(clock__gte=self.pre_time) & Q(clock__lt=self.last_time) & sql)

        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

    def actual_data_paging(self):
        '''
        重写分页方法
        :param qs:
        :return:
        '''
        if self.pre_camel_case_notation:
            self.limit = min(int(self._querydict.get('iDisplayLength', 10)), self.max_display_length)
            start = int(self._querydict.get('iDisplayStart', 0))
        else:
            self.limit = min(int(self._querydict.get('length', 10)), self.max_display_length)
            self.start = int(self._querydict.get('start', 0))

        self.offset = self.start + self.limit

    def group_ordering(self):
        """ Get parameters from the request and prepare order by clause
        """
        # Number of columns that are used in sorting
        sorting_cols = 0
        if self.pre_camel_case_notation:
            try:
                sorting_cols = int(self._querydict.get('iSortingCols', 0))
            except ValueError:
                sorting_cols = 0
        else:
            sort_key = 'order[{0}][column]'.format(sorting_cols)
            while sort_key in self._querydict:
                sorting_cols += 1
                sort_key = 'order[{0}][column]'.format(sorting_cols)
        self.sorting_order = []
        order_columns = self.ordering_columns
        for i in range(sorting_cols):
            # sorting column
            sort_dir = 'asc'
            try:
                if self.pre_camel_case_notation:
                    sort_col = int(self._querydict.get('iSortCol_{0}'.format(i)))
                    # sorting order
                    sort_dir = self._querydict.get('sSortDir_{0}'.format(i))
                else:
                    sort_col = int(self._querydict.get('order[{0}][column]'.format(i)))
                    # sorting order
                    sort_dir = self._querydict.get('order[{0}][dir]'.format(i))
            except ValueError:
                sort_col = 0
            sdir = '-' if sort_dir == 'desc' else ''
            sortcol = order_columns[sort_col]

            if isinstance(sortcol, list):
                for sc in sortcol:
                    self.sorting_order.append('{0}{1}'.format(sdir, sc.replace('.', '__')))
            else:
                self.sorting_order.append('{0}{1}'.format(sdir, sortcol.replace('.', '__')))

    def get_peak_data(self):
        '''
        获取峰值数据
        :return:
        '''
        pass

    def get_context_data(self, *args, **kwargs):
        '''
        获取上下文数据
        :param args:
        :param kwargs:
        :return:
        '''
        try:
            self.get_url() #外部使用
            self.table_conf() #new way 选表
            self.set_columns() #new way 设置栏位
            self.initialize(*args, **kwargs)
            qs = self.get_initial_queryset()
            self.set_count(qs)
            total_records = int(self.get_count())
            # qs = self.filter_queryset(qs)
            total_display_records = total_records

            # qs = self.ordering(qs) #表太大不可排序
            self.group_ordering() #获取排序字段
            self.actual_data_paging() #获取单页数据量
            # prepare output data
            if self.pre_camel_case_notation:
                if self.sixday_druge == 0:
                    aaData = self.sort_way_two(qs)
                else:
                    aaData = self.sort_way_one(qs)

                ret = {'sEcho': int(self._querydict.get('sEcho', 0)),
                       'iTotalRecords': total_records,
                       'iTotalDisplayRecords': total_display_records,
                       'aaData': aaData
                       }
            else:
                if self.sixday_druge == 0:
                    data = self.sort_way_two(qs)
                else:
                    data = self.sort_way_one(qs)
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

def traffic_analysis_treeview(request):
    if request.method == 'GET':
        nodelist = []
        clientgroup = ClientGroup.objects.all()
        sheetsinterface = SheetsInterface.objects.all()
        for clt in clientgroup:
            treenode = TreeNode()
            treenode.id = clt.id
            treenode.table_id = clt.table_id
            treenode.name = clt.client_name
            treenode.children = []
            td = treenode.dict()
            nodelist.append(td)
        for nlt in nodelist:
            for sht in sheetsinterface:
                if nlt['id'] == sht.client_id:
                    treenode = TreeNode()
                    treenode.id = sht.id
                    treenode.table_id = sht.table_id
                    treenode.name = sht.port_name
                    treenode.children = []
                    td = treenode.dict()
                    nlt['children'].append(td)
    total_data = []
    cur_id = [1, 2]
    total_data.append(cur_id)
    total_data.append(nodelist)
    data = json.dumps(total_data)

    return HttpResponse(data)

class TreeNode:
    def __int__(self, id=None, table_id=None, children=None):
        self.id = id
        self.table_id = table_id
        self.children = children
        self.name = ""
    def dict(self):
        return {'id': self.id, 'name': self.name, 'table_id': self.table_id, 'children': self.children}

