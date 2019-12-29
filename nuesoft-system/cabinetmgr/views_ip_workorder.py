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
from ..zabbixmgr.constant import get_industry_park

di = {}
class IpDistributeList(TemplateView):
    template_name = 'cabinetmgr/uploadip/ip_distribute.list.html'
    def get(self, request, *args, **kwargs):
        url = self.request.get_full_path()
        id_list = re.findall('(\d+)\/(\d+)$', url)[0]
        self.cl_id = int(id_list[0])
        us = request.user.username
        di[us] = self.cl_id
        industry_park =get_industry_park(us)

        context = self.get_context_data(**kwargs)
        submit = IDCWorkorderPlatform.objects.get(id=self.cl_id).submit
        operate_ip = IDCWorkorderPlatform.objects.get(id=self.cl_id).operate_ip
        workorder_id = IDCWorkorderPlatform.objects.get(id=self.cl_id).id
        context['workorder_id'] = workorder_id
        context['submit'] = submit
        context['operate_ip'] = operate_ip
        context['operate_type'] = 1
        context['industry_id'] = int(id_list[1])
        context['industry_park'] = industry_park
        return self.render_to_response(context)

class IpDistributeJson(BaseDatatableView):
    model = IpAddressList
    columns = ['id',
               'id',
               'client_id',
               'ip_addr',
               'ip_num',
               'ip_set',
               'create_time'
               ]
    order_columns = columns

    def get_initial_queryset(self):
        us = self.request.user.username
        workorder_id = di[us]
        url = self.request.path
        industry_id = int(re.findall('(\d+)$', url)[0])
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return self.model.objects.filter(industry_id=industry_id, workorder_id=workorder_id)

    def get_json(self, response):
        data_list = response['data']
        for data in data_list:
            if isinstance(data[-1], datetime.datetime):
                data[-1]=data[-1].strftime("%Y-%m-%d")
                data[-2] = SelectBox.objects.get(id=data[-2]).box_type
            data[2] = ElectricboxClient.objects.get(id=data[2]).client_name
        return super(IpDistributeJson, self).get_json(response)


def ip_workorder_add(request):

    context = {}
    if request.method == 'POST':
        form = UpLoadFileForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.cleaned_data['filename']
            destination = open(settings.MEDIA_ROOT+'/ipworkorder/'+str(f).encode('gbk'),'wb+')
            for chunk in f.chunks():
                destination.write(chunk)
            destination.close()
            dirlist = os.listdir(settings.MEDIA_ROOT+'/ipworkorder/')[0].decode('gbk')

            data_xls = pd.read_excel(settings.MEDIA_ROOT+'/ipworkorder/' + dirlist,sep=',',encoding='utf-8')
            df = data_xls.loc[:]
            colns = df.columns.size#列数 2
            rowns = df.iloc[:,0].size#行数 3
            error_list = []
            temp_list=[]
            url = request.get_full_path()
            industry_id = int(re.findall('(\d+)$', url)[0])
            if colns != 6:
                temp_list.append('表格字段数不正确')
                error_list.append(temp_list)
                tb_col = list(data_xls.columns)
                tb_col.insert(0, '错误信息')
                error_list.insert(0, tb_col)
                context['error_list'] = json.dumps(error_list)
                return render(request, 'cabinetmgr/uploadip/uploadip_fail.list.html', context)
            total_ip = json.loads(IpLibrary.objects.filter(industry_id=industry_id)[0].all_ip)
            us = request.user.username
            workorder_id=di[us]

            for i in range(0, len(df)):
                industry_name = df.iloc[i][0]
                client_name = df.iloc[i][1]
                ip = df.iloc[i][2]
                add_ip_num = df.iloc[i][3]
                mask = df.iloc[i][4]
                handle = str(df.iloc[i][5])

                if not IndustryPark.objects.filter(park=industry_name).exists():
                    temp_list.append('园区不存在')
                    temp_list.extend([ str(t) for t in df.iloc[i] ])
                    error_list.append(temp_list)
                    continue

                if not ElectricboxClient.objects.filter(client_name=client_name, industry_id=industry_id).exists():
                    temp_list.append('客户不存在')
                    temp_list.extend([ str(t) for t in df.iloc[i] ])
                    error_list.append(temp_list)
                    continue
                cl_id = ElectricboxClient.objects.get(client_name=client_name, industry_id=industry_id).id
                client_exist = True
                try:
                    ip_client_list = json.loads(IpAddress.objects.filter(industry_id=industry_id,client_id=cl_id)[0].ip_addr)
                    ip_client = Split(ip_client_list)
                    ip_num_client = ip_client.getIpList()
                except:
                    client_exist = False
                ip_library_sp = Split(total_ip)
                ip_sp = Split([ip])

                ip_num_lirary = ip_library_sp.getIpList()
                ip_num = ip_sp.getIpList()

                temp_list = []

                if not re.search('\d+\.\d+\.\d+\.\d+\-\d+\.\d+\.\d+\.\d+', ip):
                    temp_list.append('ip格式不正确')
                    temp_list.extend([ str(t) for t in df.iloc[i] ])
                    error_list.append(temp_list)
                    continue
                if handle != '添加' and handle != '删除':
                    temp_list.append('操作方式不正确，请填写添加或删除')
                    temp_list.extend([ str(t) for t in df.iloc[i] ])
                    error_list.append(temp_list)
                    continue
                ip_place = 0
                for i_ in ip_num:
                    if i_ not in ip_num_lirary:
                        ip_place = 1
                        break
                if ip_place == 1:
                    temp_list.append('ip不属于管辖范围')
                    temp_list.extend([ str(t) for t in df.iloc[i] ])
                    error_list.append(temp_list)
                    continue
                ip_li = ip.split('-')
                if struct.unpack('!I', socket.inet_aton(ip_li[0]))[0] > struct.unpack('!I', socket.inet_aton(ip_li[1]))[0]:
                    temp_list.append('ip范围不正确')
                    temp_list.extend([ str(t) for t in df.iloc[i] ])
                    error_list.append(temp_list)
                    continue
                if handle == '添加':
                    if IpAddress.objects.filter(industry_id=industry_id,client_id=cl_id).exists():
                        for ip_num_ in ip_num:
                            if ip_num_ in ip_num_client:
                                temp_list.append('ip重复')
                                temp_list.extend([ str(t) for t in df.iloc[i] ])
                                error_list.append(temp_list)
                                break
                        if error_list:
                            continue
                    ip_num_client = []
                    try:
                        ip_client_list = json.loads(IpAddress.objects.filter(industry_id=industry_id,client_id=cl_id)[0].ip_addr)
                        ip_client = Split(ip_client_list)
                        ip_num_client = ip_client.getIpList()
                    except:
                        pass
                    ip_library_sp = Split(total_ip)
                    ip_sp = Split([ip])

                    ip_num_lirary = ip_library_sp.getIpList()
                    ip_num = ip_sp.getIpList()
                    if len(ip_num) != int(add_ip_num):
                        temp_list.append('ip数量不正确')
                        temp_list.extend([ str(t) for t in df.iloc[i] ])
                        error_list.append(temp_list)
                        continue

                    ip_num_client.extend(ip_num)
                    ip_num_client.sort()
                    ip_client_count = len(ip_num_client)
                    ip_count = len(ip_num)
                    ip_list = []
                    fun = lambda x: x[1]-x[0]
                    for k, g in groupby(enumerate(ip_num_client), fun):
                        l1 = [j for i, j in g]
                        if len(l1) > 1:
                            scop = str(ip_sp.numToIp(min(l1))) + '-' + str(ip_sp.numToIp(max(l1)))
                            ip_list.append(scop)
                        else:
                            scop = str(ip_sp.numToIp(l1[0]))
                            ip_list.append(scop)
                    # if not IpAddress.objects.filter(client_id=cl_id).exists():
                    #     IpAddress.objects.create(ip_addr=json.dumps(ip_list), industry_id=1, ip_num=ip_client_count, client_id=cl_id)
                    # else:
                    #     IpAddress.objects.filter(client_id=cl_id).update(ip_addr=json.dumps(ip_list), ip_num=ip_client_count)
                    # us = request.user.username
                    # workorder_id = di[us]
                    IpAddressList.objects.create(ip_addr=ip,
                                                 industry_id=industry_id,
                                                 ip_num=ip_count,
                                                 mask=int(mask),
                                                 client_id=cl_id,
                                                 ip_set=11,
                                                 workorder_id=workorder_id,
                                                 create_time=datetime.datetime.now())
                if handle == '删除':
                    if not IpAddress.objects.filter(industry_id=industry_id,client_id=cl_id).exists():
                        temp_list.append('客户ip不存在')
                        temp_list.extend([ str(t) for t in df.iloc[i] ])
                        error_list.append(temp_list)
                        continue
                    if IpAddress.objects.filter(industry_id=industry_id,client_id=cl_id).exists():
                        flag = 0
                        for i in ip_num:
                            if i not in ip_num_client:
                                temp_list.append('客户ip不存在')
                                temp_list.extend([ str(t) for t in df.iloc[i] ])
                                error_list.append(temp_list)
                                flag = 1
                                break
                        if flag == 1:
                            continue
                    ip_client_list = json.loads(IpAddress.objects.filter(industry_id=industry_id,client_id=cl_id)[0].ip_addr)
                    ip_client = Split(ip_client_list)
                    ip_num_client = ip_client.getIpList()
                    ip_library_sp = Split(total_ip)
                    ip_sp = Split([ip])

                    ip_num_lirary = ip_library_sp.getIpList()
                    ip_num = ip_sp.getIpList()
                    for i in ip_num:
                        ip_num_client.remove(i)
                    ip_num_client.sort()
                    ip_client_count = len(ip_num_client)
                    ip_count = len(ip_num)
                    # ip_list = []
                    # if ip_client_count > 0:
                    #     fun = lambda x: x[1]-x[0]
                    #     for k, g in groupby(enumerate(ip_num_client), fun):
                    #         l1 = [j for i, j in g]
                    #         if len(l1) > 1:
                    #             scop = str(ip_sp.numToIp(min(l1))) + '-' + str(ip_sp.numToIp(max(l1)))
                    #             ip_list.append(scop)
                    #         else:
                    #             scop = str(ip_sp.numToIp(l1[0]))
                    #             ip_list.append(scop)
                    #     IpAddress.objects.filter(client_id=cl_id).update(ip_addr=json.dumps(ip_list), ip_num=ip_client_count)
                    # else:
                    #     IpAddress.objects.filter(client_id=cl_id).delete()
                    # us = request.user.username
                    # workorder_id = di[us]
                    IpAddressList.objects.create(ip_addr=ip,
                                                 industry_id=industry_id,
                                                 ip_num=ip_count,
                                                 mask=int(mask),
                                                 client_id=cl_id,
                                                 ip_set=12,
                                                 workorder_id=workorder_id,
                                                 create_time=datetime.datetime.now())

            os.remove(settings.MEDIA_ROOT+'/ipworkorder/' + dirlist)
            if not error_list:
                context['result'] = '操作成功！'
                context['form'] = form
                us = request.user.username
                context['workorder_id'] = di[us]
                return HttpResponseRedirect('/cabinetmgr/ipdistribute/list/' + str(di[us]) + '/' + str(industry_id))
            else:
                tb_col = list(data_xls.columns)
                tb_col.insert(0, '错误信息')
                error_list.insert(0, tb_col)
                context['error_list'] = json.dumps(error_list)
                us = request.user.username
                industry_park =get_industry_park(us)
                context['industry_park'] = industry_park
                return render(request, 'cabinetmgr/uploadip/uploadip_fail.list.html', context)
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

def ip_retry_botton(request):
    '''
    清除记录准备重新添加
    :param request:
    :return:
    '''
    url = request.get_full_path()
    id_list = re.findall('(\d+)\/(\d+)$', url)[0]
    workorder_id = int(id_list[0])
    industry_id = int(id_list[1])
    IpAddressList.objects.filter(workorder_id=workorder_id, industry_id=industry_id).delete()
    IDCWorkorderPlatform.objects.filter(id=workorder_id, industry_id=industry_id).update(submit=0,operate_ip=1, workorder_status=0)
    VertifyRecord.objects.filter(workorder_id=workorder_id, operate_type=1, industry_id=industry_id).delete()
    return HttpResponseRedirect('/cabinetmgr/ipdistribute/list/' + str(workorder_id) + '/' + str(industry_id))

class VertifyRecordList(TemplateView):
    template_name = 'cabinetmgr/uploadip/vertify_record.list.html'

    def get(self, request, *args, **kwargs):
        url = self.request.path
        get_args = re.findall('(\d+)\/(\d+)\/(\d+)$', url)[0]
        workorder_id = get_args[0]
        operate_type = get_args[1]
        industry_id = get_args[2]
        context = self.get_context_data(**kwargs)
        context['workorder_id'] = workorder_id
        context['operate_type'] = operate_type
        us = request.user.username
        industry_park =get_industry_park(us)
        context['industry_id'] = industry_id
        context['industry_park'] = industry_park
        return self.render_to_response(context)

class VertifyRecordJson(BaseDatatableView):
    model = VertifyRecord
    columns = ['id',
               'id',
               'user',
               'content',
               'result',
               'create_time'
               ]
    order_columns = columns

    def get(self, request, *args, **kwargs):
        self.workorder_id = kwargs["workorder_id"]
        self.operate_type = kwargs['operate_type']
        return super(VertifyRecordJson, self).get(request)

    def get_initial_queryset(self):
        url = self.request.get_full_path()
        get_args = re.findall('(\d+)\/(\d+)\/(\d+)', url)[0]
        industry_id = get_args[2]
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return self.model.objects.filter(industry_id=industry_id, workorder_id=self.workorder_id, operate_type=self.operate_type)

    def get_json(self, response):
        data_list = response['data']
        for data in data_list:
            if isinstance(data[-1], datetime.datetime):
                data[-1]=data[-1].strftime("%Y-%m-%d")
            if data[-2] == 0:
                data[-2] = '审核不通过'
            elif data[-2] == 1:
                data[-2] = '审核通过'
        return super(VertifyRecordJson, self).get_json(response)

def delete_workorder_ip(request):
    '''
    回退
    :param request:
    :return:
    '''
    json_data = json.loads(request.GET.get('ids'))
    id_del = json_data['ids']
    url = request.get_full_path()
    industry_id = int(re.findall('(\d+)$', url)[0])
    for dl in range(len(id_del)):
        idl = IpAddressList.objects.get(id=id_del[dl])
        client_id = idl.client_id
        ip_set = idl.ip_set
        ip = idl.ip_addr
        if ip_set == 11:#删除
            ipa = IpAddress.objects.get(industry_id=industry_id,client_id=client_id)
            ip_client_list = json.loads(IpAddress.objects.filter(industry_id=industry_id,client_id=client_id)[0].ip_addr)
            ip_client = Split(ip_client_list)
            ip_num_client = ip_client.getIpList()
            # ip_library_sp = Split(total_ip)
            ip_sp = Split([ip])

            # ip_num_lirary = ip_library_sp.getIpList()
            ip_num = ip_sp.getIpList()
            for i in ip_num:
                ip_num_client.remove(i)
            ip_num_client.sort()
            ip_client_count = len(ip_num_client)
            ip_count = len(ip_num)
            ip_list = []
            if ip_client_count > 0:
                fun = lambda x: x[1]-x[0]
                for k, g in groupby(enumerate(ip_num_client), fun):
                    l1 = [j for i, j in g]
                    if len(l1) > 1:
                        scop = str(ip_sp.numToIp(min(l1))) + '-' + str(ip_sp.numToIp(max(l1)))
                        ip_list.append(scop)
                    else:
                        scop = str(ip_sp.numToIp(l1[0]))
                        ip_list.append(scop)
                IpAddress.objects.filter(industry_id=industry_id, client_id=client_id).update(ip_addr=json.dumps(ip_list), ip_num=ip_client_count)
            else:
                IpAddress.objects.filter(industry_id=industry_id, client_id=client_id).delete()

        else:
            ip_num_client = []
            try:
                ip_client_list = json.loads(IpAddress.objects.filter(industry_id=industry_id,client_id=client_id)[0].ip_addr)
                ip_client = Split(ip_client_list)
                ip_num_client = ip_client.getIpList()
            except:
                pass
            # ip_library_sp = Split(total_ip)
            ip_sp = Split([ip])

            # ip_num_lirary = ip_library_sp.getIpList()
            ip_num = ip_sp.getIpList()

            ip_num_client.extend(ip_num)
            ip_num_client.sort()
            ip_client_count = len(ip_num_client)
            ip_count = len(ip_num)
            ip_list = []
            fun = lambda x: x[1]-x[0]
            for k, g in groupby(enumerate(ip_num_client), fun):
                l1 = [j for i, j in g]
                if len(l1) > 1:
                    scop = str(ip_sp.numToIp(min(l1))) + '-' + str(ip_sp.numToIp(max(l1)))
                    ip_list.append(scop)
                else:
                    scop = str(ip_sp.numToIp(l1[0]))
                    ip_list.append(scop)
            if not IpAddress.objects.filter(industry_id=industry_id, client_id=client_id).exists():
                IpAddress.objects.create(ip_addr=json.dumps(ip_list), industry_id=industry_id, ip_num=ip_client_count, client_id=client_id)
            else:
                IpAddress.objects.filter(industry_id=industry_id, client_id=client_id).update(ip_addr=json.dumps(ip_list), ip_num=ip_client_count)
        IpAddressList.objects.filter(id=id_del[dl]).delete()
    name_dict = {'code': '00', 'desc': '回退成功!'}
    return JsonResponse(name_dict)
