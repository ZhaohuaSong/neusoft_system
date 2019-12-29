#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/11/6 17:24
# @Author  :
# @Site    :
# @File    : views_clientinterfacemgr.py
# @Software: PyCharm

from django.views.generic import TemplateView
from ..common.datatables.views import BaseDatatableView
from models import *
from forms import *
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from ..vanilla.model_views import *

class ClientInterfaceMgrList(TemplateView):
    template_name = 'zabbixmgr/client_interface.list.html'

class ClientInterfaceMgrJson(BaseDatatableView):
    model = ClientGroup
    columns = ['id', 'id','client_name','id']
    order_columns = ['id','id','client_name','id']

class CreateClientInterfaceMgr(CreateView):

    form_class = CreateClientInterfaceMgrForm
    template_name = 'zabbixmgr/client_interfacemgr.add.html'

    #数据验证通过后执行
    def form_valid(self, form):
        self.save(form)
        return HttpResponseRedirect(reverse('zabbixmgr:clientinterfacemgr.list'))

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    #保存
    def save(self, form):
        clientgroup = ClientGroup()
        client_name = form.cleaned_data['client_name']
        clientgroup.client_name = client_name
        # clientgroup.id = 0
        clientgroup.save()

        clt_list = []
        clt_list.append(ClientItemid(client_name=client_name, id_type=0))
        clt_list.append(ClientItemid(client_name=client_name, id_type=1))
        ClientItemid.objects.bulk_create(clt_list)
