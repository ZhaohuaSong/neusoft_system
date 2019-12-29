# -*- coding: utf-8 -*-

from django.views.generic import TemplateView
from ..common.datatables.views import BaseDatatableView
from django.db.models import Q
from django.http import JsonResponse
import json
from models import RoleList
from forms import RoleListForm
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from ..vanilla import CreateView, UpdateView
from ..zabbixmgr.constant import get_industry_park
import re

class ListRole(TemplateView):
    template_name = 'sysadmin/role.list.html'

    def get(self, request, *args, **kwargs):
        us = request.user.username
        industry_park =get_industry_park(us)
        url = self.request.get_full_path()
        industry_id = int(re.findall('(\d+)$', url)[0])
        context = self.get_context_data(**kwargs)
        context['industry_park'] = industry_park
        context['industry_id'] = industry_id
        return self.render_to_response(context)

class RoleJson(BaseDatatableView):
    '''
    Json 数据格式
    '''
    model = RoleList
    columns = ['id', 'id', 'name','id', ]
    order_columns = ['id', 'id',  'name', ]

class CreateRoleView(CreateView):
    '''
    创建视图
    '''
    form_class = RoleListForm
    template_name = 'sysadmin/role.add.html'

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        context = self.get_context_data(form=form)
        us = request.user.username
        industry_park =get_industry_park(us)
        context['industry_park'] = industry_park
        return self.render_to_response(context)

    #POST请求
    def post(self, request, *args, **kwargs):
        form = self.get_form(data=request.POST, files=request.FILES)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    #数据验证通过后执行
    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(reverse('sysadmin:role.list'))


class EditRoleView(UpdateView):
    '''
    编辑视图
    '''
    form_class = RoleListForm
    template_name = 'sysadmin/role.edit.html'
    model = RoleList

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        context = self.get_context_data(form=form)
        us = request.user.username
        industry_park =get_industry_park(us)
        context['industry_park'] = industry_park
        return self.render_to_response(context)

    #数据验证通过后执行
    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(reverse('sysadmin:role.list'))


def role_batches_delete(request):
    '''
    批量删除
    :param request:
    :return:
    '''
    json_data = json.loads(request.GET.get('ids'))
    list_id_del = json_data['ids']
    sql = Q()
    for id in list_id_del:
        sql = sql | Q(id=id)
    role= RoleList.objects.get(id=id)
    print "++++++++++++++++++++"
    print role.name
    if str(role.name)==u"普通用户":
       name_dict = {'code': '00', 'desc': '该角色不允许删除!'}
    else:
       RoleList.objects.filter(sql).delete()
       name_dict = {'code': '00', 'desc': '删除成功!'}

    return JsonResponse(name_dict)
