#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/9/15 16:43
# @Author  :
# @Site    :
# @File    : views_interface_charshow.py
# @Software: PyCharm5
# @Function:

from django.views.generic import TemplateView
from models import Items, NetworkInterface, NetworkInterfaceGroup, History, HistoryStr, HistoryUint, InterfaceId
from chartdatashow import ChartDataShow
from django.http import JsonResponse
import json
import re
from constant import get_industry_park

class ChartDataPrep(ChartDataShow):
    '''
    为POST、GET方法准备图标数据
    '''
    def get_interface_data(self):
        '''
        所有图表数据收集
        :return:
        '''
        item = NetworkInterface.objects.filter(type=int(self.id))
        chart_data = []
        total_data = {}

        for ite in item: #端口进出流量图表合并
            self.itemid = ite.in_itemid
            self.items = Items.objects.using('zabbixdb').get(itemid=int(self.itemid))
            json_data = self.table_router()
            json_data['value'] = json.loads(json_data['value'])
            self.sum_in_value(json_data)

            title = json_data['text_title'][0]
            ti = title.replace('Incoming', '')
            json_data['text_title'] = ti
            json_data['interface_id'] = str(self.id)

            self.itemid = ite.out_itemid
            self.items = Items.objects.using('zabbixdb').get(itemid=int(self.itemid))
            json_data2 = self.table_router()
            json_data['value2'] = json.loads(json_data2['value'])
            self.sum_out_value(json_data)
            chart_data.append(json_data)

        try:
            for i in range(len(self.in_value)):
                t = self.in_value[i]/1024
                self.in_value[i] = t
            for i in range(len(self.out_value)):
                t = self.out_value[i]/1024
                self.out_value[i] = t
            total_data['value'] = json.dumps(self.in_value)
            total_data['value2'] = json.dumps(self.out_value)
            total_data['units'] = chart_data[0]['units']
            if self.timer == '1小时':
                total_data['text_title'] = 'All network traffic (1h)'
            elif self.timer == '2小时':
                total_data['text_title'] = 'All network traffic (2h)'
            elif self.timer == '1天':
                total_data['text_title'] = 'All network traffic (1d)'
            total_data['clock'] = chart_data[0]['clock']
            total_data['interface_id'] = str(self.id)
            chart_data.insert(0, total_data)
        except:
            pass
        return chart_data

    def table_router(self):
            '''
            数据表路由，itemid寻表
            :param url:
            :return:
            '''
            json_data = None
            self.init_value_type()
            self.set_time_interval()
            if self.value_type == 0:
                json_data = self.chart_data(History)
            elif self.value_type == 1:
                json_data = self.chart_data(HistoryStr)
            elif self.value_type == 3:
                json_data = self.chart_data(HistoryUint)
            return self.units_reset(json_data)

    def get_items_name(self):
        try:
            name = NetworkInterface.objects.filter(in_itemid=self.itemid)[0]
            name = 'Incoming network traffic on ' + name.inter_name
        except:
            name = NetworkInterface.objects.filter(out_itemid=self.itemid)[0]
            name = 'Incoming network traffic on ' + name.inter_name
        return name

    def sum_in_value(self, json_data):
        '''
        单组总流入流量计算
        :param json_data: 端口流入流量
        :return:
        '''
        temp = json.loads(json_data['value'])
        if json_data['units'] == json.dumps('GB'):
            for i in range(len(temp)):
                temp[i] *= 1024
        if self.in_value == None:
                self.in_value = temp
        else:
            for i in range(len(temp)):
                try:
                    if self.in_value[i] is not None and temp[i] is not None:
                        self.in_value[i] += temp[i]
                    elif self.in_value[i] is None and temp[i] is not None:
                        self.in_value[i] = temp[i]
                    else:
                        pass
                except:
                    pass
    def sum_out_value(self, json_data):
        '''
        单组总流出流量计算
        :param json_data: 端口流出流量
        :return:
        '''
        temp = json.loads(json_data['value2'])
        if json_data['units'] == json.dumps('GB'):
            for i in range(len(temp)):
                temp[i] *= 1024
        if self.out_value == None:
                self.out_value = temp
        else:
            for i in range(len(temp)):
                try:
                    if self.out_value[i] is not None and temp[i] is not None:
                        self.out_value[i] += temp[i]
                    elif self.out_value[i] is None and temp[i] is not None:
                        self.out_value[i] = temp[i]
                    else:
                        pass
                except:
                    pass

class InterfacechartshowList(TemplateView, ChartDataPrep):

    template_name = 'zabbixmgr/interface_chartshow.list.html'
    def get_context_data(self, **kwargs):
        context = super(InterfacechartshowList, self).get_context_data(**kwargs)
        # group_name = NetworkInterfaceGroup.objects.using('zabbixdb').all()
        group_name = NetworkInterfaceGroup.objects.all()
        nodelist = []
        no = []
        i = 1
        for grp in group_name:
            dict_obj = {}
            dict_obj['text'] = grp.group_name
            dict_obj['id'] = i
            dict_obj['tags'] = ['0']
            nodelist.append(dict_obj)
            no.append(grp)
            i += 1
        context['no'] = no
        context['treedata'] = json.dumps(nodelist)

        return context

    def get(self, request, *args, **kwargs):
        us = request.user.username
        industry_park =get_industry_park(us)
        url = self.request.get_full_path()
        industry_id = int(re.findall('(\d+)$', url)[0])
        self.id = request.GET.get('id')
        context = self.get_context_data(**kwargs)
        context['industry_park'] = industry_park
        context['industry_id'] = industry_id
        try:

            outside_url = request.get_full_path()
            type = re.findall('(\d+)\/(\d+)\/\d+$', outside_url)
            print type
            tim = int(type[0][0])
            if tim == 0:
                self.timer = '1小时'
            elif tim == 1:
                self.timer = '2小时'
            elif tim == 2:
                self.timer = '1天'
            self.id = int(type[0][1])
        except:
            pass
        chart_data = self.get_interface_data()
        context['timer'] = json.dumps(self.timer)
        context['chart_data'] = json.dumps(chart_data)
        try:
            ntg = NetworkInterfaceGroup.objects.get(id=self.id)
            ntg = ntg.group_name
            context['ntg'] = ntg
        except:
            pass
        return self.render_to_response(context)

    def post(self,request,*args, **kwargs):
        self.id = request.POST.get('id')
        try:
            InterfaceId.objects.all().delete()
            InterfaceId.objects.create(temp_id=self.id)
        except:
            pass
        ntg = NetworkInterfaceGroup.objects.get(id=self.id)
        ntg = ntg.group_name
        chart_data = self.get_interface_data()
        print chart_data
        interface_id = []
        interface_id.append(json.dumps(int(self.id)))
        result = []
        result.append(chart_data)
        result.append(interface_id)
        result.append(json.dumps(ntg.encode('utf-8')))
        return JsonResponse(result,safe=False)
