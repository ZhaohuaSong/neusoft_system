#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/10/19 14:21
# @Author  :
# @Site    :
# @File    : idc_buildingmgr.py
# @Software: PyCharm

from django.views.generic import TemplateView
from models import *
from ..common.datatables.views import BaseDatatableView
from ..vanilla.model_views import CreateView
import json
from django.db.models import Q
from forms import *
import re
from django.http import HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse

class IDCBuildingmgrList(TemplateView):
    template_name = 'cabinetmgr/idc_buildingmgr.list.html'

    def get(self, request, *args, **kwargs):
        idc_building = IDCBuilding.objects.all()
        nodelist = []
        i = 0
        for n in idc_building:
            dict_obj = {}
            dict_obj['text'] = n.building_name
            dict_obj['id'] = n.id
            dict_obj['tags'] = ['0']
            nodelist.append(dict_obj)
            i += 1

        context = self.get_context_data()
        context['request'] = request
        context['treedata'] = json.dumps(nodelist)
        return self.render_to_response(context)

class IDCBuildingmgrJson(BaseDatatableView):
    '''
    Josn data
    '''
    model = BuildingRoom
    columns = ['id', 'id','room_name','id']
    order_columns = ['id', 'id','room_name','id']

    def filter_queryset(self, qs):
        #搜索数据集
        id = self._querydict.get('id')
        search = self._querydict.get('search[value]', None)
        col_data = self.extract_datatables_column_data()

        q = Q()

        for col_no, col in enumerate(col_data):
            if search and col['searchable']:
                q |= Q(**{'{0}__icontains'.format(self.columns[col_no].replace('.', '__')): search})
            if col['search.value']:
                qs = qs.filter(
                    **{'{0}__icontains'.format(self.columns[col_no].replace('.', '__')): col['search.value']})
        qs = qs.filter(q)

        #1、在用户列表中屏蔽掉自己
        qs = qs.filter(Q(building_id=id))
        return qs
