#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/10/25 19:12
# @Author  :
# @Site    :
# @File    : views_ip_workorder.py
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
import pandas as pd
import socket
import struct
from ipsplit.ipListSplit import Split
from itertools import groupby
from ..zabbixmgr.models import Hosts, Items, SheetsInterface, ClientGroup
from ..zabbixmgr.constant import get_industry_park

di = {}
class InterfaceDistributeList(TemplateView):
    template_name = 'cabinetmgr/uploadifc/interface_distribute.list.html'
    def get(self, request, *args, **kwargs):
        url = self.request.get_full_path()
        id_list = re.findall('(\d+)\/(\d+)$', url)[0]
        self.cl_id = int(id_list[0])
        us = request.user.username
        di[us] = self.cl_id
        industry_park =get_industry_park(us)

        context = self.get_context_data(**kwargs)
        submit = IDCWorkorderPlatform.objects.get(id=self.cl_id).submit
        operate_interface = IDCWorkorderPlatform.objects.get(id=self.cl_id).operate_interface
        workorder_id = IDCWorkorderPlatform.objects.get(id=self.cl_id).id
        context['workorder_id'] = workorder_id
        context['submit'] = submit
        context['operate_interface'] = operate_interface
        context['operate_type'] = 4#1-ip，2-机柜，3-设备，4-端口
        context['industry_id'] = int(id_list[1])
        context['industry_park'] = industry_park
        return self.render_to_response(context)

class InterfaceDistributeJson(BaseDatatableView):
    model = InterfaceWorkorder
    columns = ['id',
               'id',
               'client_id',
               'ip',
               'interface',
               'bandwidth',
               'handle_id',
               ]
    order_columns = columns

    def get_initial_queryset(self):
        url = self.request.path
        industry_id = int(re.findall('(\d+)$', url)[0])
        us = self.request.user.username
        workorder_id = di[us]
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return self.model.objects.filter(industry_id=industry_id, workorder_id=workorder_id)

    def get_json(self, response):
        data_list = response['data']
        for data in data_list:
            data[-1] = SelectBox.objects.get(id=data[-1]).box_type
            print data[2], 'ssss'
            data[2] = ElectricboxClient.objects.get(id=data[2]).client_name
        return super(InterfaceDistributeJson, self).get_json(response)

def interface_workorder_handle(request):

    context = {}
    if request.method == 'POST':
        form = UpLoadFileForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.cleaned_data['filename']
            destination = open(settings.MEDIA_ROOT+'/interface_workorder/'+str(f).encode('gbk'),'wb+')
            for chunk in f.chunks():
                destination.write(chunk)
            destination.close()
            dirlist = os.listdir(settings.MEDIA_ROOT+'/interface_workorder/')[0].decode('gbk')

            data_xls = pd.read_excel(settings.MEDIA_ROOT+'/interface_workorder/' + dirlist,sep=',',encoding='utf-8')
            df = data_xls.loc[:]
            colns = df.columns.size#列数 2
            rowns = df.iloc[:,0].size#行数 3
            error_list = []
            temp_list=[]
            url = request.get_full_path()
            id_list = re.findall('(\d+)\/(\d+)$', url)[0]
            workorder_id = int(id_list[0])
            industry_id = int(id_list[1])
            if colns != 6:
                temp_list.append('表格字段数不正确')
                error_list.append(temp_list)
                tb_col = list(data_xls.columns)
                tb_col.insert(0, '错误信息')
                error_list.insert(0, tb_col)
                context['error_list'] = json.dumps(error_list)
                return render(request, 'cabinetmgr/uploadifc/uploadifc_fail.list.html', context)
            # total_ip = json.loads(IpLibrary.objects.filter(industry_id=industry_id)[0].all_ip)
            for i in range(0, len(df)):
                industry_name = df.iloc[i][0]
                client_name = df.iloc[i][1]
                ip = df.iloc[i][2]
                interface = df.iloc[i][3]
                bandwidth = df.iloc[i][4]
                handle = str(df.iloc[i][5])

                if not IndustryPark.objects.filter(park=industry_name).exists():
                    temp_list.append('园区不存在')
                    temp_list.extend([ str(t) for t in df.iloc[i] ])
                    error_list.append(temp_list)
                    continue
                if not ElectricboxClient.objects.filter(industry_id=industry_id, client_name=client_name).exists():
                    temp_list.append('客户不存在')
                    temp_list.extend([ str(t) for t in df.iloc[i] ])
                    error_list.append(temp_list)
                    continue
                # cl_id = ElectricboxClient.objects.get(client_name=client_name, industry_id=industry_id).id
                # client_exist = True
                # try:
                #     ip_client_list = json.loads(IpAddress.objects.filter(industry_id=industry_id,client_id=cl_id)[0].ip_addr)
                #     ip_client = Split(ip_client_list)
                #     ip_num_client = ip_client.getIpList()
                # except:
                #     client_exist = False
                # ip_library_sp = Split(total_ip)
                # ip_sp = Split([ip])
                #
                # ip_num_lirary = ip_library_sp.getIpList()
                # ip_num = ip_sp.getIpList()

                temp_list = []

                if not re.search('\d+\.\d+\.\d+\.\d+', ip):
                    temp_list.append('ip格式不正确')
                    temp_list.extend([ str(t) for t in df.iloc[i] ])
                    error_list.append(temp_list)
                    continue
                interface_ip_list = ['188.1.184.1', '188.1.184.2', '188.1.184.3', '188.1.184.4']

                if not Hosts.objects.using('zabbixdb').filter(host=ip).exists():
                    temp_list.append('ip不正确')
                    temp_list.extend([ str(t) for t in df.iloc[i] ])
                    error_list.append(temp_list)
                    continue
                ind_id = IndustryPark.objects.get(park=industry_name).id
                if ClientGroup.objects.filter(client_name=client_name, industry_id=ind_id).exists():
                    cl_id = ClientGroup.objects.get(client_name=client_name, industry_id=ind_id).id
                    if SheetsInterface.objects.filter(port_name=interface, ip=ip, client_id=cl_id).exists():
                        temp_list.append('端口已存在')
                        temp_list.extend([ str(t) for t in df.iloc[i] ])
                        error_list.append(temp_list)
                        continue
                if handle != '添加' and handle != '回收':
                    temp_list.append('操作方式不正确，请填写添加或回收')
                    temp_list.extend([ str(t) for t in df.iloc[i] ])
                    error_list.append(temp_list)
                    continue

                idcworkorderplatform = IDCWorkorderPlatform.objects.filter(industry_id=industry_id, operate_interface=1).exclude(workorder_status=2)
                for ipf in idcworkorderplatform:
                    if InterfaceWorkorder.objects.filter(industry_id=industry_id, workorder_id=ipf.id, ip=ip, interface=interface).exists():
                        temp_list.append('目标在其他工单操作')
                        temp_list.extend([ str(t) for t in df.iloc[i] ])
                        error_list.append(temp_list)
                        continue
                client_table = IDCWorkorderPlatform.objects.get(industry_id=industry_id, id=workorder_id).client_name
                if str(client_table) != str(client_name):
                    temp_list.append('与工单客户不一致')
                    temp_list.extend([ str(t) for t in df.iloc[i] ])
                    error_list.append(temp_list)
                    continue
                client_id = ElectricboxClient.objects.get(industry_id=industry_id, client_name=client_name).id
                if handle == '添加':
                    host_id = Hosts.objects.using('zabbixdb').get(host=ip).hostid
                    in_ite = Items.objects.using('zabbixdb').filter(Q(hostid=host_id)
                                                          & Q(key_field__contains='net.if.in[ifHCInOctets')
                                                          & Q(name__contains='Interface %s'% interface)
                                                          & Q(flags=4))[0]

                    out_ite = Items.objects.using('zabbixdb').filter(Q(hostid=host_id)
                                                                  & Q(key_field__contains='net.if.out[ifHCOutOctets')
                                                                  & Q(name__contains='Interface %s'% interface)
                                                                  & Q(flags=4))[0]

                    InterfaceWorkorder.objects.create(ip=ip,
                                                      interface=interface,
                                                      bandwidth=bandwidth,
                                                      client_id=client_id,
                                                      in_itemid=in_ite.itemid,
                                                      out_itemid=out_ite.itemid,
                                                      table_id=1,
                                                      handle_id=11,
                                                      industry_id=industry_id,
                                                      workorder_id=workorder_id)
                if handle == '回收':
                    # client_table = IDCWorkorderPlatform.objects.get(id=workorder_id).client_name
                    # if str(client_table) != str(client_name):
                    #     temp_list.append('与工单客户不一致')
                    #     temp_list.extend([ str(t) for t in df.iloc[i] ])
                    #     error_list.append(temp_list)
                    #     continue
                    client_id = ClientGroup.objects.get(industry_id=industry_id,client_name=client_name).id
                    if not SheetsInterface.objects.filter(port_name=interface,
                                                          ip=ip,
                                                          bandwidth=bandwidth,
                                                          client_id=client_id,
                                                          table_id=1).exists():
                        temp_list.append('目标不存在')
                        temp_list.extend([ str(t) for t in df.iloc[i] ])
                        error_list.append(temp_list)
                        continue

                    sht = SheetsInterface.objects.get(port_name=interface,
                                                          ip=ip,
                                                          bandwidth=bandwidth,
                                                          client_id=client_id,
                                                          table_id=1)
                    client_id = ElectricboxClient.objects.get(industry_id=industry_id, client_name=client_name).id
                    InterfaceWorkorder.objects.create(ip=sht.ip,
                                                      interface=sht.port_name,
                                                      bandwidth=sht.bandwidth,
                                                      client_id=client_id,
                                                      in_itemid=sht.in_itemid,
                                                      out_itemid=sht.out_itemid,
                                                      table_id=1,
                                                      handle_id=12,
                                                      industry_id=industry_id,
                                                      workorder_id=workorder_id)

            os.remove(settings.MEDIA_ROOT+'/interface_workorder/' + dirlist)
            if not error_list:
                context['result'] = '操作成功！'
                context['form'] = form
                context['workorder_id'] = workorder_id
                return HttpResponseRedirect('/cabinetmgr/interfacedistribute/list/' + str(workorder_id) + '/' + str(industry_id))
            else:
                tb_col = list(data_xls.columns)
                tb_col.insert(0, '错误信息')
                error_list.insert(0, tb_col)
                context['error_list'] = json.dumps(error_list)
                us = request.user.username
                industry_park =get_industry_park(us)
                context['industry_park'] = industry_park
                return render(request, 'cabinetmgr/uploadifc/uploadifc_fail.list.html', context)
    elif request.method == 'GET':
        try:
            form = UpLoadFileForm
            context['form'] = form
            context['imgPath'] = ''
        except Exception as e:
            print "++++++++++++++++++++++++<<<<<<<<<<<<<<<Exception>>>>>>>>>>>>>>>>>>>>>>>>>++++++++++++++++++"
            pass
        us = request.user.username
        industry_park =get_industry_park(us)
        context['industry_park'] = industry_park
        return render(request, 'cabinetmgr/upload_file.html', context)

def interface_retry_botton(request):
    '''
    清除记录准备重新添加
    :param request:
    :return:
    '''
    url = request.get_full_path()
    id_list = re.findall('(\d+)\/(\d+)$', url)[0]
    workorder_id = int(id_list[0])
    industry_id = int(id_list[1])
    InterfaceWorkorder.objects.filter(workorder_id=workorder_id, industry_id=industry_id).delete()
    IDCWorkorderPlatform.objects.filter(id=workorder_id, industry_id=industry_id).update(submit=0,operate_interface=1, workorder_status=0)
    VertifyRecord.objects.filter(workorder_id=workorder_id, operate_type=4, industry_id=industry_id).delete()
    return HttpResponseRedirect('/cabinetmgr/interfacedistribute/list/' + str(workorder_id) + '/' + str(industry_id))

def delete_workorder_interface(request):
    '''
    回退
    :param request:
    :return:
    '''
    json_data = json.loads(request.GET.get('ids'))
    id_del = json_data['ids']
    sql = Q()
    for i in id_del:
        sql |= Q(id=i)
    InterfaceWorkorder.objects.filter(sql).delete()
    name_dict = {'code': '00', 'desc': '回退成功!'}
    return JsonResponse(name_dict)
