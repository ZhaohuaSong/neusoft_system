#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/27 15:46
# @Author  :
# @Site    :
# @File    : chart_data.py
# @Software: PyCharm

import json
from ..models import *

class ChartData():
    def context_data(self, context, in_peak, out_peak, clo, temp_time, id_list, in_avg, out_avg):
        in_peak_rate = in_peak
        out_peak_rate = out_peak
        clock = clo
        context['tickinterval'] = temp_time
        context['value'] = in_peak_rate
        context['value2'] = out_peak_rate
        context['units'] = json.dumps('Gbps')

        industry_id = id_list[5]
        client_group = ClientGroup.objects.filter(industry_id=industry_id)
        client_dict = {}
        group_dict = {}
        port_dict = {}
        for i in range(len(client_group)):
            name = client_group[i].client_name
            client_id = client_group[i].id
            group_dict[str(client_id)] = name
            sheets_interface = SheetsInterface.objects.filter(client_id=client_id, industry_id=industry_id)
            temp_list = []
            for j in range(len(sheets_interface)):
                temp_list.append(sheets_interface[j].ip + '-' + sheets_interface[j].port_name)
                port_dict[str(sheets_interface[j].id)] = sheets_interface[j].ip + '-' + sheets_interface[j].port_name
            client_dict[name] = temp_list
        context['arrData'] = json.dumps(client_dict)
        context['group_dict'] = json.dumps(group_dict)
        context['port_dict'] = json.dumps(port_dict)
        try:
            if max(out_peak_rate) > 10:
                context['interval'] = 10
            elif max(out_peak_rate) > 5 and max(out_peak_rate) <= 10:
                context['interval'] = 5
            elif max(out_peak_rate) <=5:
                context['interval'] = 0.5
            if int(id_list[1]) == 0:
                client = ClientGroup.objects.get(id=int(id_list[0]), industry_id=industry_id).client_name
            elif int(id_list[1]) == 1:
                sht = SheetsInterface.objects.get(id=id_list[0])
                client = sht.port_name
                ip = sht.ip
                client_name = ClientGroup.objects.get(id=sht.client_id, industry_id=industry_id).client_name
                client = client_name + ':' + ip + '-' + str(client)
            in_average = round(in_avg, 2)
            out_average = round(out_avg, 2)
            context['in_peak_rate'] = json.dumps('流入-' + '最大值：' + str(round(max(in_peak_rate), 2)) + ' Gbps    平均值：' + str(in_average) + ' Gbps')
            context['out_peak_rate'] = json.dumps('流出-' + '最大值：' + str(round(max(out_peak_rate), 2)) + ' Gbps    平均值：' + str(out_average) + ' Gbps')
            context['text_title'] = json.dumps([str(client) + '-峰值流入及流出速率'])
            context['clock'] = json.dumps(clock)
        except:
            pass
        return context
