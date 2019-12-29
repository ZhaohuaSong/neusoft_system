#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from ..common.datatables.views import BaseDatatableView
from models import SysLog
from django.views.generic import TemplateView
from ..zabbixmgr.constant import get_industry_park
import re

class SysLogList(TemplateView):
    template_name = 'sysadmin/syslog.list.html'
    def get(self, request, *args, **kwargs):
        us = request.user.username
        industry_park =get_industry_park(us)
        url = self.request.get_full_path()
        industry_id = int(re.findall('(\d+)$', url)[0])
        context = self.get_context_data(**kwargs)
        context['industry_park'] = industry_park
        context['industry_id'] = industry_id
        return self.render_to_response(context)

class SyslogJson(BaseDatatableView):
    '''
    Json 数据格式
    '''
    model = SysLog
    columns = ['id', 'id', 'user_name', 'user_mobile', 'user_role_name', 'sys_org_name', 'handle_url','handle_params','ip_address', 'sys_timestamp']
    order_columns = ['id', 'id', 'user_name', 'user_mobile', 'user_role_name', 'sys_org_name', 'handle_url','handle_params', 'ip_address','sys_timestamp']
