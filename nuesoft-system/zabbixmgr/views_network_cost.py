#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/17 11:57
# @Author  :
# @Site    :
# @File    : views_network_cost.py
# @Software: PyCharm

from django.views.generic import TemplateView
from models import *
from ..common.datatables.views import BaseDatatableView
from ..vanilla.model_views import CreateView
import json
from django.db.models import Q
import calendar, datetime, time
from forms import CreateGroupclientPortForm
import re
from django.http import HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse
import calendar
import logging
from django.conf import settings
from constant import get_industry_park
logger = logging.getLogger(__name__)

PRICE = 1
sh = ''

class NetworkCostList(TemplateView):
    template_name = 'zabbixmgr/network_cost.list.html'

    def get(self, request, *args, **kwargs):
        us = request.user.username
        industry_park =get_industry_park(us)
        url = self.request.get_full_path()
        industry_id = int(re.findall('(\d+)$', url)[0])
        clientgroup = ClientGroup.objects.filter(industry_id=industry_id)
        nodelist = []
        i = 0
        # 从数据字典组成JSON数据给树形控件
        for n in clientgroup:
            dict_obj = {}
            dict_obj['text'] = n.client_name
            dict_obj['id'] = n.id
            dict_obj['tags'] = ['0']
            nodelist.append(dict_obj)
            i += 1

        context = self.get_context_data()

        context['industry_park'] = industry_park
        context['industry_id'] = industry_id
        context['request'] = request
        context['treedata'] = json.dumps(nodelist)
        return self.render_to_response(context)

class NetworkCostJson(BaseDatatableView):
    model = GHistoryUint5Min
    # s = datetime.datetime.now()
    # pre_time = 1546272000
    # last_time = 1548950400
    # clientgroup = ClientGroup.objects.all()
    # for cl_name in clientgroup:
    #     in_itemid = ClientItemid.objects.get(client_name=cl_name.client_name, id_type=0).id
    #     out_itemid = ClientItemid.objects.get(client_name=cl_name.client_name, id_type=1).id
    #     in_list = list(GHistoryUint1Min.objects.filter(itemid=in_itemid, clock__gte=1546272000, clock__lt=1548950400).values_list('value', flat=True))
    #     out_list = list(GHistoryUint1Min.objects.filter(itemid=out_itemid, clock__gte=1546272000, clock__lt=1548950400).values_list('value', flat=True))
    #     for i in range((last_time-pre_time)/(60*5)):
    #         print i
    #         if i == ((last_time-pre_time)/(60*5)):
    #             break
    #         GHistoryUint5Min.objects.filter(itemid=in_itemid, clock=1546272000+i*5*60).update(value=in_list[i*5])
    #         GHistoryUint5Min.objects.filter(itemid=out_itemid, clock=1546272000+i*5*60).update(value=out_list[i*5])
    #     print 'kkk'
    # e = datetime.datetime.now()
    # print e-s
    columns = ['itemid', 'itemid', 'clock', 'in_traffic', 'out_traffic', 'total_traffic']
    order_columns = columns

    # def get_json(self, response):
    #     data_list = response['data']
    #     for data in data_list:
    #         if isinstance(data[2], datetime.datetime):
    #             data[2] = data[2].strftime('%Y-%m')
    #     return super(NetworkCostJson, self).get_json(response)

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        url = self.request.path
        industry_id = int(re.findall('(\d+)$', url)[0])
        return self.model.objects.filter(industry_id=industry_id)

    def ordering(self, qs):
        return qs

    def filter_queryset(self, qs):
        #搜索数据集
        id = self._querydict.get('id', 0)
        global sh
        search = self._querydict.get('search[value]', '2018-12')
        if sh == ''and search == '':
            sh = str(datetime.datetime.now().year) + '-' + str(datetime.datetime.now().month)
        elif sh != '' and search != '':
            sh = search
        timeArray = time.strptime(sh, "%Y-%m")
        timeStart = int(time.mktime(timeArray))

        search_month = sh.split('-')
        monthRange = calendar.monthrange(int(search_month[0]),int(search_month[1]))
        timeEnd = monthRange[1]*86400 + timeStart

        # id = self._querydict.get('id')
        # search = self._querydict.get('search[value]', None)
        col_data = self.extract_datatables_column_data()

        q = Q()

        # for col_no, col in enumerate(col_data):
        #     if search and col['searchable']:
        #         q |= Q(**{'{0}__icontains'.format(self.columns[col_no].replace('.', '__')): search})
        #     if col['search.value']:
        #         qs = qs.filter(
        #             **{'{0}__icontains'.format(self.columns[col_no].replace('.', '__')): col['search.value']})
        qs = qs.filter(q)

        qs = qs.filter(Q(clock__gte=timeStart)& Q(clock__lt=timeEnd))
        return qs

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
        url = self.request.path
        industry_id = int(re.findall('(\d+)$', url)[0])
        id = self._querydict.get('id', None)
        try:

            cl_name = ClientGroup.objects.get(id=int(id)).client_name
            in_itemid = ClientItemid.objects.get(Q(client_name=cl_name) & Q(industry_id=industry_id) & Q(id_type=0)).id
            out_itemid = ClientItemid.objects.get(Q(client_name=cl_name) & Q(industry_id=industry_id) & Q(id_type=1)).id
            in_list = list(qs.filter(itemid=in_itemid).values_list('clock', 'value_max'))
            out_list = list(qs.filter(itemid=out_itemid).values_list('clock', 'value_max'))
            # sort_col_ = int(self._querydict.get('order[{0}][column]'.format(0)))
            # print sort_col_
            out_list.sort(key=lambda x: x[1])
            # out_list = out_list[0:int(0.95*len(out_list))]
        except:
            in_list = []
            out_list = []
        self.total_records = len(out_list)
        if self.total_records < limit:
            offset = self.total_records - start
        else:
            offset = start + limit
        self.total_display_records = offset

        page_out_list = out_list[start:offset]
        in_list = dict(in_list)
        page_in_list = []
        for tp in page_out_list:
            if tp[0] in in_list:
                page_in_list.append((tp[0], in_list[tp[0]]))
        value_list = [page_in_list, page_out_list]
        return value_list

    def prepare_results(self, qs):
        data = []
        for i in range(len(qs[0])):
            timeArray = time.localtime(qs[0][i][0])
            otherStyleTime = time.strftime("%Y%m%d%H%M%S", timeArray)
            data.append([0,
                         0,
                         otherStyleTime,
                         round(float(qs[0][i][1])/(1024*1024), 2),
                         round(float(qs[1][i][1])/(1024*1024), 2),
                         round(float((qs[0][i][1]+qs[1][i][1]))/(1024*1024), 2)])
        return data

    def get_context_data(self, *args, **kwargs):
        '''
            获取上下文数据
        :param args:
        :param kwargs:
        :return:
        '''
        import datetime
        try:

            self.initialize(*args, **kwargs)
            qs = self.get_initial_queryset()
            # number of records before filtering
            # self.total_records = qs.count() #暂时关闭
            qs = self.filter_queryset(qs)
            # number of records after filtering

            # total_display_records = qs.count() #暂时关闭
            qs = self.ordering(qs)
            qs = self.paging(qs)


            # prepare output data
            if self.pre_camel_case_notation:
                aaData = self.prepare_results(qs)

                ret = {'sEcho': int(self._querydict.get('sEcho', 0)),
                       'iTotalRecords': self.total_records,
                       'iTotalDisplayRecords': self.total_display_records,
                       'aaData': aaData
                       }
            else:
                data = self.prepare_results(qs)
                ret = {'draw': int(self._querydict.get('draw', 0)),
                       'recordsTotal': self.total_display_records,
                       'recordsFiltered': self.total_records,
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

class NetworkCount():
    '''
    流量计费
    '''
    # unix_ts = 1538323200
    # times = datetime.datetime.fromtimestamp(unix_ts)
    # NetworkCost.objects.filter(update_time='2018年10月').update(cost_month=times)
    # print type(times)
    # print type(datetime.datetime(datetime.date.today().year,datetime.date.today().month,1))

    def last_month(self):
        '''
        获取上月头尾时间戳
        :return:
        '''
        self.year = datetime.datetime.now().year
        self.month = datetime.datetime.now().month
        tss1 = '%s-%s-1 00:00:00'% (self.year, self.month-1)
        tss2 = '%s-%s-1 00:00:00'% (self.year, self.month)

        timeArray1 = time.strptime(tss1, "%Y-%m-%d %H:%M:%S")
        timeStamp1 = int(time.mktime(timeArray1))
        timeArray2 = time.strptime(tss2, "%Y-%m-%d %H:%M:%S")
        timeStamp2 = int(time.mktime(timeArray2))
        return timeStamp1, timeStamp2

    def get_5min_data(self):
        '''
        获取数据
        :return:
        '''
        pre_clock, last_clock = self.last_month()
        # print pre_clock, last_clock
        # c = 1530374400
        # for i in range(37):
        #     in_val = list(GHistoryUint5Min.objects.filter(Q(itemid=35) & Q(clock__gte=c) & Q(clock__lt=c+86400)).values_list('value_max', flat=True))
        #     print len(in_val), c, c+86400
        #     c += 86400

        cl = list(ClientGroup.objects.values_list('id', 'client_name'))
        cost_list = []
        now_month_first_date = datetime.datetime(datetime.date.today().year,datetime.date.today().month,1)
        for c in cl:
            in_id = ClientItemid.objects.get(Q(client_name=c[1]) & Q(id_type=0)).id
            out_id = ClientItemid.objects.get(Q(client_name=c[1]) & Q(id_type=1)).id
            in_val = list(GHistoryUint5Min.objects.filter(Q(itemid=in_id) & Q(clock__gte=pre_clock) & Q(clock__lt=last_clock)).values_list('value_max', flat=True))
            out_val = list(GHistoryUint5Min.objects.filter(Q(itemid=out_id) & Q(clock__gte=pre_clock) & Q(clock__lt=last_clock)).values_list('value_max', flat=True))
            in_val.sort()
            in_val.reverse()
            out_val.sort()
            out_val.reverse()
            # if c[1] == '承启通'.decode('utf-8'):
            #     print len(in_val)
            #     print len(out_val)
            in_value = sum(in_val[int(0.05*len(in_val)):])
            out_value = sum(out_val[int(0.05*len(in_val)):])
            in_cost = in_value*300/(1024*1024*1024*8)*PRICE
            out_cost = out_value*300/(1024*1024*1024*8)*PRICE
            networkcost = NetworkCost(in_cost=in_cost, out_cost=out_cost, total_cost=in_cost+out_cost, client_id=c[0], cost_month=now_month_first_date)
            cost_list.append(networkcost)
        NetworkCost.objects.bulk_create(cost_list)

