#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/5 18:54
# @Author  :
# @Site    :
# @File    : views_iplist.py
# @Software: PyCharm

from django.views.generic import TemplateView
from ..common.datatables.views import BaseDatatableView
from django.db.models import Q
import datetime
from django.shortcuts import render,render_to_response
import time
import re
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from ..vanilla import CreateView, UpdateView
from models import *
from forms import *
import json
from django.db.models import Sum
import os
from subprocess import *
from decimal import Decimal
from django.conf import settings
import logging
from ipsplit.ipListSplit import Split
from ..zabbixmgr.constant import get_industry_park
logger = logging.getLogger(__name__)

class IpBackupList(TemplateView):
    template_name = 'cabinetmgr/ip_backup_list.html'

    def get(self, request, *args, **kwargs):
        us = request.user.username
        industry_park =get_industry_park(us)
        context = self.get_context_data(**kwargs)

        url = self.request.get_full_path()
        industry_id = int(re.findall('(\d+)$', url)[0])
        context['industry_id'] = industry_id
        context['industry_park'] = industry_park
        client_list = ElectricboxClient.objects.filter(industry_id=industry_id).values_list('id', 'client_name')
        nodelist = []
        no = []
        i = 1
        for cl in client_list:
            dict_obj = {}
            dict_obj['text'] = cl[1]
            dict_obj['id'] = cl[0]
            dict_obj['tags'] = ['0']
            nodelist.append(dict_obj)
            no.append(cl)
            i += 1
        context['request'] = request
        context['treedata'] = json.dumps(nodelist)
        return self.render_to_response(context)

class IpBackupListJson(BaseDatatableView):
    model = IpBackupModel
    columns = ['id',
               'id',
               'begin_ip',
               'end_ip',
               'unit_name',
               'network_name',
               'unit_type',
               'bussiness_license_num',
               'unit_property',
               'provinces',
               'city',
               'county',
               'administrative_level',
               'profession',
               'address',
               'customer_name',
               'customer_phone',
               'customer_email',
               'physical_gateway',
               'usage_mode',
               'use_time',
               'use_way',
               'report_unit',
               'source_unit',
               'redistribution_unit',
               'record_representation',
               'gateway_ip_addr',
               'source_record',
               'relate_num']
    order_columns = columns

    def filter_queryset(self, qs):
        #搜索数据集
        id = self._querydict.get('id', None)
        if id:
            return super(IpBackupListJson, self).filter_queryset(qs).filter(client_id=id)
        else:
            return super(IpBackupListJson, self).filter_queryset(qs)

    def get_initial_queryset(self):
        url = self.request.path
        industry_id = int(re.findall('(\d+)$', url)[0])
        id = self._querydict.get('id', None)
        client_name = None
        try:
            client_name = ElectricboxClient.objects.get(id=id).client_name
        except:
            pass
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return self.model.objects.filter(industry_id=industry_id, unit_name=client_name)

    def my_paging(self):
        """ Paging
        """
        if self.pre_camel_case_notation:
            limit = min(int(self._querydict.get('iDisplayLength', 10)), self.max_display_length)
            start = int(self._querydict.get('iDisplayStart', 0))
        else:
            limit = min(int(self._querydict.get('length', 10)), self.max_display_length)
            start = int(self._querydict.get('start', 0))

        # if pagination is disabled ("paging": false)
        id = self._querydict.get('id', None)
        ip_list = []
        if IpAddress.objects.filter(client_id=id).exists():
            ip = json.loads(IpAddress.objects.get(client_id=id).ip_addr)
            ip_list = Split(ip).getAllIpList()
            self.total_records = len(ip_list)
            if self.total_records < limit:
                offset = self.total_records - start
            else:
                offset = start + limit
            self.total_display_records = offset
            return ip_list[start:offset]
        self.total_records = 0
        self.total_display_records = 0
        return ip_list

    def my_prepare_results(self, ip_list, qs):
        data = []
        if qs:
            col = qs[0]
            for item in ip_list:
                gateway_ip_addr = re.findall('\d+\.\d+\.\d+\.', item)[0] + '254'
                temp_data = [11,
                            12,
                            item,
                            item,
                            col.unit_name,
                            col.unit_type,
                            col.bussiness_license_num,
                            col.unit_property,
                            col.provinces,
                            col.city,
                            col.county,
                            col.administrative_level,
                            col.profession,
                            col.address,
                            col.customer_name,
                            col.customer_phone,
                            col.customer_email,
                            col.physical_gateway,
                            col.usage_mode,
                            col.use_time,
                            col.use_way,
                            col.report_unit,
                            col.source_unit,
                            col.redistribution_unit,
                            col.record_representation,
                            gateway_ip_addr,
                            col.source_record,
                            col.relate_num]
                data.append(temp_data)
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
            qs = self.get_initial_queryset()
            ip_list = self.my_paging()
            if self.pre_camel_case_notation:
                aaData = self.my_prepare_results(ip_list, qs)

                ret = {'sEcho': int(self._querydict.get('sEcho', 0)),
                       'iTotalRecords': self.total_records,
                       'iTotalDisplayRecords': self.total_display_records,
                       'aaData': aaData
                       }
            else:
                data = self.my_prepare_results(ip_list, qs)
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
