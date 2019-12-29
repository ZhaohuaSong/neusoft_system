#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  :
# @Date         : 2017/1/11
# @Version      : 0.0.1
# @Link         :

from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView
import json
from django.conf import settings
from django.db.models import Sum
import os
import xlrd
import pandas as pd
from models import *
import re
import datetime
from table_data_insert import *
from django.db.models import Q
from ..zabbixmgr.constant import get_industry_park
from room_graph.room_graph_data import RoomGraphData

class GraphListView(TemplateView):
    """
     ===============================================================================
     function：    显示文件链接列表
     developer:
     add-time      2017/2/4
     ===============================================================================
    """
    template_name = 'cabinetmgr/graph.list.html'

    import sys
    defaultencoding = 'utf-8'
    if sys.getdefaultencoding() != defaultencoding:
        reload(sys)
        sys.setdefaultencoding(defaultencoding)

    def get(self, request, *args, **kwargs):
        us = request.user.username
        industry_park =get_industry_park(us)
        context = self.get_context_data()
        url = self.request.get_full_path()
        industry_id = int(re.findall('(\d+)$', url)[0])
        context['industry_id'] = industry_id
        context['industry_park'] = industry_park

        nodelist = []
        building = IDCBuilding.objects.filter(park_id=int(industry_id))
        for bd in building:
            room = BuildingRoom.objects.filter(building_id=bd.id, industry_id=industry_id)
            nodes = {}
            nodes['text'] = bd.building_name
            room_list = []
            for rm in room:
                room_list.append({'text': rm.room_name, 'id': str(rm.id) + '-' + str(bd.id) + '-' + str(industry_id)})
            nodes['nodes'] = room_list
            nodelist.append(nodes)
        context['treedata'] = json.dumps(nodelist)

        return self.render_to_response(context)

    def post(self,request,*args, **kwargs):
        id_list = request.POST.get('id').split('-')
        room_id = int(id_list[0])
        building_id = int(id_list[1])
        industry_id = int(id_list[2])
        room_graph_data = RoomGraphData(room_id, building_id, industry_id)
        if industry_id == 1 and building_id == 1:
            table_data = room_graph_data.qirui_data_list()
        elif industry_id == 2 and building_id == 2:
            table_data = room_graph_data.huaxinyuan_G3_data_list()
        elif industry_id == 2 and building_id == 3:
            table_data = room_graph_data.huaxinyuan_G6_data_list()
        return JsonResponse(json.dumps(table_data),safe=False)

