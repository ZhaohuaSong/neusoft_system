#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/8 9:14
# @Author  :
# @Site    :
# @File    : views_idc_workorder_verify.py
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
from ..zabbixmgr.models import ClientGroup, SheetsInterface, ClientItemid
from ..zabbixmgr.constant import get_industry_park
di = {}

class IDCWorkorderVerifyList(TemplateView):

    template_name = 'cabinetmgr/idc_workorder_verify.list.html'
    def get(self, request, *args, **kwargs):
        us = request.user.username
        industry_park =get_industry_park(us)
        context = self.get_context_data(**kwargs)

        url = self.request.get_full_path()
        industry_id = int(re.findall('(\d+)$', url)[0])
        context['industry_id'] = industry_id
        context['industry_park'] = industry_park
        return self.render_to_response(context)

class IDCWorkorderVerifyJson(BaseDatatableView):
    model = IDCWorkorderPlatform
    columns = ['id',
               'id',
               'workorder_name',
               'client_name',
               'operate_ip',
               'operate_elbox',
               'operate_device',
               'operate_interface',
               'create_time',
               'operate_record',
                'id',
               'workorder_status'
               ]
    order_columns = columns

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        select_box = list(SelectBox.objects.filter(type_id=8).values_list('box_type', flat=True))
        username =  self.request.user.username

        url = self.request.get_full_path()
        industry_id = int(re.findall('(\d+)$', url)[0])
        if username in select_box:
            return self.model.objects.filter(industry_id=industry_id, submit=1)
        else:
            return self.model.objects.filter(industry_id=10000)

    def get_json(self, response):
        data_list = response['data']
        for data in data_list:
            if isinstance(data[8], datetime.datetime):
                data[8]=data[8].strftime("%Y-%m-%d")
        return super(IDCWorkorderVerifyJson, self).get_json(response)

class IpVertifyList(UpdateView):
    template_name = 'cabinetmgr/vertify/ip_vertify.list.html'
    success_url = '/cabinetmgr/idcworkordervertify/list'
    form_class = CreateOrgCheckForm
    def get(self, request, *args, **kwargs):
        url = self.request.get_full_path()
        id_list = re.findall('(\d+)\/(\d+)$', url)[0]
        workorder_id = int(id_list[0])
        self.industry_id = int(id_list[1])
        us = request.user.username

        form = self.get_form()
        context = self.get_context_data(form=form)

        industry_park =get_industry_park(us)
        context['industry_park'] = industry_park
        context['industry_id'] = self.industry_id

        operate_ip = IDCWorkorderPlatform.objects.get(id=workorder_id, industry_id=self.industry_id).operate_ip
        context['operate_ip'] = operate_ip
        context['workorder_id'] = workorder_id

        audit_form = CreateOrgCheckForm(initial={
            'workorder_id': workorder_id,
        })
        context["audit_form"] = audit_form
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = CreateOrgCheckForm(request.POST)
        if form.is_valid():
            result = request.POST.get("result")
            content = request.POST.get("content")
            workorder_id = request.POST.get('workorder_id')
            url = self.request.get_full_path()
            id_list = re.findall('(\d+)\/(\d+)$', url)[0]
            industry_id = int(id_list[1])
            VertifyRecord.objects.create(workorder_id=workorder_id,
                                         user=request.user.username,
                                         result=result,
                                         content=content,
                                         create_time=datetime.datetime.now(),
                                         industry_id=industry_id,
                                         operate_type=1)
            if result == '0':
                operate_ip = 3
            elif result == '1':
                operate_ip = 2
            config_vertify(workorder_id, operate_ip, 0, industry_id)
            self.success_url = '/cabinetmgr/idcworkordervertify/list/' + str(industry_id)
            return HttpResponseRedirect(self.get_success_url())
        return self.form_invalid(form)

    def form_invalid(self, form):
        url = self.request.get_full_path()
        id_list = re.findall('(\d+)\/(\d+)$', url)[0]
        workorder_id = int(id_list[0])
        industry_id = id_list[1]
        form = self.get_form()
        context = self.get_context_data(form=form)
        operate_ip = IDCWorkorderPlatform.objects.get(id=workorder_id, industry_id=industry_id).operate_ip
        context['operate_ip'] = operate_ip
        context['workorder_id'] = workorder_id

        audit_form = CreateOrgCheckForm(initial={
            'workorder_id': workorder_id,
        })
        context["audit_form"] = audit_form
        return self.render_to_response(context)

class IpVertifyJson(BaseDatatableView):
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
        url = self.request.path
        id_list = re.findall('(\d+)\/(\d+)$', url)[0]
        workorder_id = int(id_list[0])
        industry_id = id_list[1]
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
        return super(IpVertifyJson, self).get_json(response)

from ipsplit.ipListSplit import Split
from itertools import groupby

def get_ip_list(num_list, ip_sp):
    ip_list = []
    fun = lambda x: x[1]-x[0]
    for k, g in groupby(enumerate(num_list), fun):
        l1 = [j for i, j in g]
        if len(l1) > 1:
            scop = str(ip_sp.numToIp(min(l1))) + '-' + str(ip_sp.numToIp(max(l1)))
            ip_list.append(scop)
        else:
            scop = str(ip_sp.numToIp(l1[0]))
            ip_list.append(scop)
    return ip_list

def add_delete_ip(client_id, workorder_id, industry_id):
    '''
    审核通过后将ip添加到对应客户列表
    :return:
    '''
    ip_addr_list = list(IpAddressList.objects.filter(workorder_id=workorder_id, industry_id=industry_id).values_list('ip_addr', 'ip_set', 'mask'))
    total_ip = json.loads(IpLibrary.objects.filter(industry_id=industry_id)[0].all_ip)
    for tup in ip_addr_list:
        if tup[1] == 11:#添加
            ip_num_client = []
            try:
                ip_client_list = json.loads(IpAddress.objects.filter(industry_id=industry_id,client_id=client_id)[0].ip_addr)
                ip_client = Split(ip_client_list)
                ip_num_client = ip_client.getIpList()
            except:
                pass
            ip_library_sp = Split(total_ip)
            ip_sp = Split([tup[0]])

            ip_num_lirary = ip_library_sp.getIpList()
            ip_num = ip_sp.getIpList()

            ip_num_client.extend(ip_num)
            mask_list = []
            ip_list = ip_sp.getAllIpList()
            for ip_ in range(len(ip_num)):
                ip_addr_mask = IpAddressMask(ip_addr=ip_list[ip_], client_id=client_id, mask=tup[2], industry_id=industry_id)
                mask_list.append(ip_addr_mask)
            IpAddressMask.objects.bulk_create(mask_list)
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
            if not IpAddress.objects.filter(client_id=client_id).exists():
                IpAddress.objects.create(ip_addr=json.dumps(ip_list), industry_id=industry_id, ip_num=ip_client_count, client_id=client_id)
            else:
                IpAddress.objects.filter(client_id=client_id, industry_id=industry_id).update(ip_addr=json.dumps(ip_list), ip_num=ip_client_count)
        else:
            ip_client_list = json.loads(IpAddress.objects.filter(industry_id=industry_id,client_id=client_id)[0].ip_addr)
            ip_client = Split(ip_client_list)
            ip_num_client = ip_client.getIpList()
            ip_library_sp = Split(total_ip)
            ip_sp = Split([tup[0]])

            ip_num_lirary = ip_library_sp.getIpList()
            ip_num = ip_sp.getIpList()
            sql = Q()
            ip_list = ip_sp.getAllIpList()
            for ip_ in ip_list:
                sql |= Q(ip_addr=ip_)
            IpAddressMask.objects.filter(sql & Q(industry_id=industry_id)).delete()
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
                IpAddress.objects.filter(client_id=client_id, industry_id=industry_id).update(ip_addr=json.dumps(ip_list), ip_num=ip_client_count)
            else:
                IpAddress.objects.filter(client_id=client_id, industry_id=industry_id).delete()

from public_ways import *
def add_delete_elbox(workorder_id, industry_id):
    '''
    审核通过
    :param client_id:
    :param workorder_id:
    :return:
    '''
    electricbox_workorder = ElectricboxWorkorder.objects.filter(workorder_id=workorder_id, industry_id=industry_id)
    building_id = electricbox_workorder[0].building_id
    for elw in electricbox_workorder:
        if elw.handle_id == 12:
            Electricbox.objects.filter(room_id=elw.room_id,
                                       building_id=elw.building,
                                       box_name=elw.box_name,
                                       industry_id=industry_id).update(client_name=None, box_type=50)
            # name_block = elw.box_name.split('-')
            # ContractRack.objects.using('otherdb').filter(building='旗锐',
            #                             room=name_block[0],
            #                             col=name_block[1],
            #                             rack_pos=name_block[2]).delete()
            # ElectricboxWorkorder.objects.filter(id=workorder_id).delete()
        else:
            Electricbox.objects.create(room_id=elw.room_id,
                                       industry_id=industry_id,
                                       building_id=elw.building_id,
                                       device_room=elw.device_room,
                                       box_name=elw.box_name,
                                       client_name=elw.client_name,
                                       power_rating=elw.power_rating,
                                       threshold_rating=elw.threshold_rating,
                                       on_state_date=elw.on_state_date,
                                       power_on_date=elw.power_on_date,
                                       down_power_date=elw.down_power_date,
                                       device_num=elw.device_num,
                                       device_u_num=elw.device_u_num,
                                       box_type=elw.box_type)
            if industry_id != 4:
                name_block = elw.box_name.split('-')
                if len(name_block) == 2:
                    room = name_block[0].lstrip('0')
                    col = name_block[1][0]
                    rack_pos = int(name_block[1][1:])
                else:
                    room = name_block[0]
                    col = name_block[1]
                    rack_pos = int(name_block[2])
                building_name = IDCBuilding.objects.get(id=building_id, park_id=industry_id).building_name
                if not ContractRack.objects.using('otherdb').filter(building=building_name,
                                            room=room,
                                            col=col,
                                            rack_pos=rack_pos).exists():
                    ContractRack.objects.using('otherdb').create(building=building_name,
                                                room=room,
                                                col=col,
                                                rack_pos=rack_pos,
                                                rack_power=elw.power_rating,
                                                rack_status='否')
            ElectricboxWorkorder.objects.filter(id=workorder_id).delete()
    update_device_room(industry_id, building_id)

def add_delete_device(workorder_id, industry_id):
    '''
    设备审核tongguo
    :param client_id:
    :param workorder_id:
    :return:
    '''
    networkdevice_workorder = NetworkDeviceWorkorder.objects.filter(workorder_id=workorder_id)
    for ntd in networkdevice_workorder:
        if ntd.handle_id == 12:
            NetworkDevice.objects.filter(box_id=ntd.box_id,
                                        room_id=ntd.room_id,
                                        building_id=ntd.building_id,
                                        industry_id=industry_id,
                                        on_state_date=ntd.on_state_date,
                                        power_on_date=ntd.power_on_date,
                                        start_u_num=ntd.start_u_num,
                                        end_u_num=ntd.end_u_num,
                                        total_u_num=ntd.total_u_num,
                                        device_code=ntd.device_code,
                                        device_type=ntd.device_type,
                                        device_status=ntd.device_status,
                                        power_num=ntd.power_num,
                                        device_alternating=ntd.device_alternating,
                                        device_threshold_rt=float(ntd.device_threshold_rt),
                                        device_num=int(ntd.device_num)).delete()
            el = Electricbox.objects.get(id=ntd.box_id)
            if el.device_num-int(ntd.device_num) == 0:
                name_block = el.box_name.split('-')
                # ContractRack.objects.using('otherdb').filter(building='旗锐', room=name_block[0], col=name_block[1], rack_pos=name_block[2]).update(rack_status='否',
                #                                                                                                                  power_down_time=ntd.down_power_date)
                Electricbox.objects.filter(id=ntd.box_id).update(down_power_date=ntd.down_power_date,
                                                                 # on_state_date=None,
                                                                 #   power_on_date=None,
                                                                   device_num=0,
                                                                   device_u_num=0,
                                                                   box_type=10,
                                                                   )
            else:
                Electricbox.objects.filter(id=ntd.box_id).update(
                                                             device_num=el.device_num-int(ntd.device_num),
                                                             device_u_num=el.device_u_num-int(ntd.end_u_num-ntd.start_u_num+1))
        else:
            NetworkDevice.objects.create(box_id=ntd.box_id,
                                        room_id=ntd.room_id,
                                        building_id=ntd.building_id,
                                        industry_id=industry_id,
                                        on_state_date=ntd.on_state_date,
                                        power_on_date=ntd.power_on_date,
                                        start_u_num=ntd.start_u_num,
                                        end_u_num=ntd.end_u_num,
                                        total_u_num=ntd.total_u_num,
                                        device_code=ntd.device_code,
                                        device_type=ntd.device_type,
                                        device_status=ntd.device_status,
                                        power_num=ntd.power_num,
                                        device_alternating=ntd.device_alternating,
                                        device_threshold_rt=float(ntd.device_threshold_rt),
                                        device_num=int(ntd.device_num))

            elx = Electricbox.objects.get(industry_id=industry_id, building_id=ntd.building_id, id=ntd.box_id)
            name_block = elx.box_name.split('-')
            building_name = IDCBuilding.objects.get(building_id=ntd.building_id, park_id=industry_id).building_name
            if ContractRack.objects.using('otherdb').filter(building=building_name, room=name_block[0], col=name_block[1], rack_pos=name_block[2]).exists():
                crk = ContractRack.objects.using('otherdb').get(building=building_name, room=name_block[0], col=name_block[1], rack_pos=name_block[2])
                if crk.power_up_time ==None and crk.power_down_time == None:
                    ContractRack.objects.using('otherdb').filter(building=building_name, room=name_block[0], col=name_block[1], rack_pos=name_block[2]).update(rack_status='是',
                                                                                                                                     power_up_time=ntd.power_on_date)
                elif crk.power_up_time !=None and crk.power_down_time != None and crk.power_down_time >= crk.power_up_time:
                    timeArray = time.strptime(str(crk.power_up_time), "%Y-%m-%d %H:%M:%S")
                    first_time = time.strftime("%Y-%m", timeArray)
                    timeArray = time.strptime(str(ntd.power_on_date), "%Y-%m-%d %H:%M:%S")
                    second_time = time.strftime("%Y-%m", timeArray)
                    if first_time == second_time:
                        ContractRack.objects.using('otherdb').filter(building=building_name, room=name_block[0], col=name_block[1], rack_pos=name_block[2]).update(rack_status='是',
                                                                                                                                     # power_up_time=ntd.power_on_date,
                                                                                                                                     power_up_secondarytime=ntd.power_on_date)
                    else:
                        ContractRack.objects.using('otherdb').filter(building=building_name, room=name_block[0], col=name_block[1], rack_pos=name_block[2]).update(rack_status='是',
                                                                                                                                     power_up_time=ntd.power_on_date)

            if elx.on_state_date == None and elx.down_power_date == None or elx.on_state_date !=None and elx.down_power_date !=None:
                box_type = 40
                client_id = ElectricboxClient.objects.get(client_name=ntd.client_name).id
                Electricbox.objects.filter(id=ntd.box_id).update(client_name=client_id,
                                                            on_state_date=ntd.on_state_date,
                                                             power_on_date=ntd.power_on_date,
                                                             down_power_date=None,
                                                             device_num=ntd.device_num,
                                                             device_u_num=ntd.total_u_num,
                                                             box_type=box_type)
            else:
                el = Electricbox.objects.get(industry_id=industry_id, building_id=ntd.building_id,id=ntd.box_id)
                Electricbox.objects.filter(industry_id=industry_id, building_id=ntd.building_id,id=ntd.box_id).update(
                                                                                    device_num=ntd.device_num+el.device_num,
                                                                                    device_u_num=el.device_u_num+ntd.total_u_num)

def vertify_notpass_interface(client_id, workorder_id):
    '''
    端口ip审核不通过驳回
    :param client_id:
    :param workorder_id:
    :return:
    '''
    pass

def vertify_pass_interface(workorder_id, industry_id):
    '''
    端口审核通过
    :param workorder_id:
    :return:
    '''
    interfaceworkorder = InterfaceWorkorder.objects.filter(industry_id=industry_id, workorder_id=workorder_id)

    for itf in interfaceworkorder:
        client_name = ElectricboxClient.objects.get(id=itf.client_id).client_name
        if itf.handle_id == 11:
            client_id = None
            if ClientGroup.objects.filter(industry_id=industry_id,client_name=client_name).exists():
                client_id = ClientGroup.objects.get(industry_id=industry_id,client_name=client_name).id
            else:
                ClientGroup.objects.create(industry_id=industry_id,client_name=client_name)
                client_id = ClientGroup.objects.get(industry_id=industry_id,client_name=client_name).id
                ClientItemid.objects.create(industry_id=industry_id,client_name=client_name, id_type=0)
                ClientItemid.objects.create(industry_id=industry_id,client_name=client_name, id_type=1)
            SheetsInterface.objects.create(port_name=itf.interface,
                                              ip=itf.ip,
                                              bandwidth=itf.bandwidth,
                                              client_id=client_id,
                                              table_id=1,
                                              in_itemid=itf.in_itemid,
                                              out_itemid=itf.out_itemid,
                                              industry_id=industry_id)
        else:
            client_name = ElectricboxClient.objects.get(id=itf.client_id, industry_id=industry_id)
            client_id = ClientGroup.objects.get(client_name=client_name, industry_id=industry_id).id
            SheetsInterface.objects.filter(port_name=itf.interface,
                                              ip=itf.ip,
                                              bandwidth=itf.bandwidth,
                                              client_id=client_id,
                                              table_id=1,
                                              in_itemid=itf.in_itemid,
                                              out_itemid=itf.out_itemid,industry_id=industry_id).delete()

def config_vertify(workorder_id, operate, type, industry_id):
    if type == 0:
        IDCWorkorderPlatform.objects.filter(id=workorder_id, industry_id=industry_id).update(operate_ip=operate)
    elif type == 1:
        IDCWorkorderPlatform.objects.filter(id=workorder_id, industry_id=industry_id).update(operate_elbox=operate)
    elif type == 2:
        IDCWorkorderPlatform.objects.filter(id=workorder_id, industry_id=industry_id).update(operate_device=operate)
    elif type == 3:
        IDCWorkorderPlatform.objects.filter(id=workorder_id, industry_id=industry_id).update(operate_interface=operate)
    idc = IDCWorkorderPlatform.objects.get(id=workorder_id, industry_id=industry_id)
    vertify_list = []
    vertify_list.append(idc.operate_ip)
    vertify_list.append(idc.operate_elbox)
    vertify_list.append(idc.operate_device)
    vertify_list.append(idc.operate_interface)

    idc_pf = IDCWorkorderPlatform.objects.get(id=workorder_id, industry_id=industry_id)
    client_id = ElectricboxClient.objects.get(client_name=idc_pf.client_name, industry_id=industry_id).id
    if operate == 3: #审核不通过即可操作
        if type == 0:
            pass
            # add_delete_ip(client_id, workorder_id)
        elif type == 1:
            pass
            # add_delete_elbox(client_id, workorder_id)
        elif type == 2:
            add_delete_device(client_id, workorder_id)
        elif type == 3:
            vertify_notpass_interface(client_id, workorder_id)
    else: #审核通过
        if type == 0:
            add_delete_ip(client_id, workorder_id, industry_id)
        elif type == 1:
            add_delete_elbox(workorder_id, industry_id)
        elif type == 2:
            add_delete_device(workorder_id, industry_id)
        elif type == 3:
            vertify_pass_interface(workorder_id, industry_id)

    #更新状态
    if 1 not in vertify_list and 3 in vertify_list: #审核不通过
        IDCWorkorderPlatform.objects.filter(id=workorder_id, industry_id=industry_id).update(workorder_status=3)
    elif 2 not in vertify_list and 3 not in vertify_list: #待审核
        IDCWorkorderPlatform.objects.filter(id=workorder_id, industry_id=industry_id).update(workorder_status=0)
    elif 1 not in vertify_list and 3 not in vertify_list: #审核通过
        IDCWorkorderPlatform.objects.filter(id=workorder_id, industry_id=industry_id).update(workorder_status=2)
    else: #审核中
        IDCWorkorderPlatform.objects.filter(id=workorder_id, industry_id=industry_id).update(workorder_status=1)
    return HttpResponseRedirect(reverse('cabinetmgr:idcworkordervertify.list'))

class ElectricboxVertifyList(UpdateView):
    template_name = 'cabinetmgr/vertify/electricbox_vertify.list.html'
    success_url = '/cabinetmgr/idcworkordervertify/list'
    form_class = CreateOrgCheckForm
    def get(self, request, *args, **kwargs):
        user = request.user.username
        industry_park = get_industry_park(user)
        url = self.request.get_full_path()
        id_list = re.findall('(\d+)\/(\d+)$', url)[0]
        workorder_id = int(id_list[0])
        industry_id = int(id_list[1])

        form = self.get_form()
        context = self.get_context_data(form=form)
        operate_elbox = IDCWorkorderPlatform.objects.get(id=workorder_id, industry_id=industry_id).operate_elbox
        context['operate_elbox'] = operate_elbox
        context['workorder_id'] = workorder_id
        context['industry_id'] = industry_id
        context['industry_park'] = industry_park

        audit_form = CreateOrgCheckForm(initial={
            'workorder_id': workorder_id,
        })
        context["audit_form"] = audit_form
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = CreateOrgCheckForm(request.POST)
        if form.is_valid():
            result = request.POST.get("result")
            content = request.POST.get("content")
            workorder_id = request.POST.get('workorder_id')
            url = self.request.get_full_path()
            id_list = re.findall('(\d+)\/(\d+)$', url)[0]
            industry_id = int(id_list[1])
            VertifyRecord.objects.create(workorder_id=workorder_id,
                                         user=request.user.username,
                                         result=result,
                                         content=content,
                                         create_time=datetime.datetime.now(),
                                         industry_id=industry_id,
                                         operate_type=2)
            if result == '0':
                operate_elbox = 3
            elif result == '1':
                operate_elbox = 2
            config_vertify(workorder_id, operate_elbox, 1, industry_id)
            self.success_url = '/cabinetmgr/idcworkordervertify/list/' + str(industry_id)
            return HttpResponseRedirect(self.get_success_url())
        return self.form_invalid(form)

    def form_invalid(self, form):
        url = self.request.get_full_path()
        workorder_id = int(re.findall('(\d+)$', url)[0])
        form = self.get_form()
        context = self.get_context_data(form=form)
        operate_elbox = IDCWorkorderPlatform.objects.get(id=workorder_id, industry_id=1).operate_elbox
        context['operate_elbox'] = operate_elbox
        context['workorder_id'] = workorder_id

        audit_form = CreateOrgCheckForm(initial={
            'workorder_id': workorder_id,
        })
        context["audit_form"] = audit_form
        return self.render_to_response(context)

class ElectricboxVertifyJson(BaseDatatableView):
    model = ElectricboxWorkorder
    columns = ['id',
               'id',
               'device_room',
               'box_name',
               'client_name',
               'power_rating',
               'threshold_rating',
               'on_state_date',
               'power_on_date',
               'down_power_date',
               'device_num',
               'device_u_num',
               'box_type',
               'handle_id']
    order_columns = columns

    def get(self, request, *args, **kwargs):
        self.workorder_id = kwargs["workorder_id"]
        return super(ElectricboxVertifyJson, self).get(request)

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        url = self.request.path
        industry_id = int(re.findall('(\d+)$', url)[0])
        return self.model.objects.filter(industry_id=industry_id, workorder_id=self.workorder_id)

    def get_json(self, response):
        data_list = response['data']
        for data in data_list:
            data[4] = ElectricboxClient.objects.get(id=data[4]).client_name
            data[-1] = SelectBox.objects.get(id=data[-1]).box_type
            data[-2] = SelectBox.objects.get(type_id=data[-2]).box_type
        return super(ElectricboxVertifyJson, self).get_json(response)

class NetworkDeviceVertifyList(UpdateView):
    template_name = 'cabinetmgr/vertify/networkdevice_vertify.list.html'
    success_url = '/cabinetmgr/idcworkordervertify/list'
    form_class = CreateOrgCheckForm
    def get(self, request, *args, **kwargs):
        url = self.request.get_full_path()
        id_list = re.findall('(\d+)\/(\d+)$', url)[0]
        workorder_id = int(id_list[0])
        industry_id = int(id_list[1])
        us = request.user.username
        industry_park =get_industry_park(us)

        form = self.get_form()
        context = self.get_context_data(form=form)
        operate_device = IDCWorkorderPlatform.objects.get(id=workorder_id, industry_id=industry_id).operate_device
        context['operate_device'] = operate_device
        context['workorder_id'] = workorder_id
        context['industry_id'] = industry_id
        context['industry_park'] = industry_park

        audit_form = CreateOrgCheckForm(initial={
            'workorder_id': workorder_id,
        })
        context["audit_form"] = audit_form
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = CreateOrgCheckForm(request.POST)
        if form.is_valid():
            result = request.POST.get("result")
            content = request.POST.get("content")
            workorder_id = request.POST.get('workorder_id')
            url = self.request.get_full_path()
            id_list = re.findall('(\d+)\/(\d+)$', url)[0]
            industry_id = int(id_list[1])
            VertifyRecord.objects.create(workorder_id=workorder_id,
                                         user=request.user.username,
                                         result=result,
                                         content=content,
                                         create_time=datetime.datetime.now(),
                                         industry_id=industry_id,
                                         operate_type=3)
            if result == '0':
                operate_device = 3
            elif result == '1':
                operate_device = 2
            config_vertify(workorder_id, operate_device, 2, industry_id)
            self.success_url = '/cabinetmgr/idcworkordervertify/list/' + str(industry_id)
            return HttpResponseRedirect(self.get_success_url())
        return self.form_invalid(form)

    def form_invalid(self, form):
        url = self.request.get_full_path()
        workorder_id = int(re.findall('(\d+)$', url)[0])
        form = self.get_form()
        context = self.get_context_data(form=form)
        operate_device = IDCWorkorderPlatform.objects.get(id=workorder_id, industry_id=1).operate_device
        context['operate_device'] = operate_device
        context['workorder_id'] = workorder_id

        audit_form = CreateOrgCheckForm(initial={
            'workorder_id': workorder_id,
        })
        context["audit_form"] = audit_form
        return self.render_to_response(context)

class NetworkDeviceVertifyJson(BaseDatatableView):
    model = NetworkDeviceWorkorder
    columns = ['id',
               'id',
               'box_id',
               'on_state_date',
               'power_on_date',
               # 'down_power_date',
               'device_num',
               'start_u_num',
               'end_u_num',
               'total_u_num',
               'device_code',
               'device_type',
               'device_status',
               'power_num',
               'device_alternating',
               'device_threshold_rt',
               'handle_id']
    order_columns = columns

    def get(self, request, *args, **kwargs):
        self.workorder_id = kwargs["workorder_id"]
        return super(NetworkDeviceVertifyJson, self).get(request)

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        url = self.request.path
        industry_id = int(re.findall('(\d+)$', url)[0])
        return self.model.objects.filter(industry_id=industry_id, workorder_id=self.workorder_id)

    def get_json(self, response):
        data_list = response['data']
        for data in data_list:
            data[2]=Electricbox.objects.get(id=data[2]).box_name
            if isinstance(data[3], datetime.datetime):
                data[3]=data[3].strftime("%Y-%m-%d")
            if isinstance(data[4], datetime.datetime):
                data[4]=data[4].strftime("%Y-%m-%d")
            if data[-1] == 11:
                data[-1] = '添加'
            elif data[-1] == 12:
                data[-1] = '回收'
        return super(NetworkDeviceVertifyJson, self).get_json(response)

class InterfaceVertifyList(UpdateView):
    template_name = 'cabinetmgr/vertify/interface_vertify.list.html'
    success_url = '/cabinetmgr/idcworkordervertify/list'
    form_class = CreateOrgCheckForm
    def get(self, request, *args, **kwargs):
        url = self.request.get_full_path()
        id_list = re.findall('(\d+)\/(\d+)$', url)[0]
        workorder_id = int(id_list[0])
        industry_id = int(id_list[1])

        form = self.get_form()
        context = self.get_context_data(form=form)
        operate_interface = IDCWorkorderPlatform.objects.get(id=workorder_id, industry_id=industry_id).operate_interface
        context['operate_interface'] = operate_interface
        context['workorder_id'] = workorder_id
        context['industry_id'] = industry_id
        us = request.user.username
        industry_park =get_industry_park(us)
        context['industry_park'] = industry_park

        audit_form = CreateOrgCheckForm(initial={
            'workorder_id': workorder_id,
        })
        context["audit_form"] = audit_form
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = CreateOrgCheckForm(request.POST)
        if form.is_valid():
            result = request.POST.get("result")
            content = request.POST.get("content")
            workorder_id = request.POST.get('workorder_id')
            url = self.request.get_full_path()
            id_list = re.findall('(\d+)\/(\d+)$', url)[0]
            industry_id = int(id_list[1])
            VertifyRecord.objects.create(workorder_id=workorder_id,
                                         user=request.user.username,
                                         result=result,
                                         content=content,
                                         create_time=datetime.datetime.now(),
                                         industry_id=industry_id,
                                         operate_type=4)
            if result == '0':
                operate_interface = 3
            elif result == '1':
                operate_interface = 2
            config_vertify(workorder_id, operate_interface, 3, industry_id)
            self.success_url = '/cabinetmgr/idcworkordervertify/list/' + str(industry_id)
            return HttpResponseRedirect(self.get_success_url())
        return self.form_invalid(form)

    def form_invalid(self, form):
        url = self.request.get_full_path()
        workorder_id = int(re.findall('(\d+)$', url)[0])
        form = self.get_form()
        context = self.get_context_data(form=form)
        operate_interface = IDCWorkorderPlatform.objects.get(id=workorder_id, industry_id=1).operate_interface
        context['operate_interface'] = operate_interface
        context['workorder_id'] = workorder_id

        audit_form = CreateOrgCheckForm(initial={
            'workorder_id': workorder_id,
        })
        context["audit_form"] = audit_form
        return self.render_to_response(context)

class InterfaceVertifyJson(BaseDatatableView):
    model = InterfaceWorkorder
    columns = ['id',
               'id',
               'client_id',
               'ip',
               'interface',
               'bandwidth',
               'handle_id']
    order_columns = columns

    def get(self, request, *args, **kwargs):
        self.workorder_id = kwargs["workorder_id"]
        return super(InterfaceVertifyJson, self).get(request)

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        url = self.request.path
        industry_id = int(re.findall('(\d+)$', url)[0])
        return self.model.objects.filter(industry_id=industry_id, workorder_id=self.workorder_id)

    def get_json(self, response):
        data_list = response['data']
        for data in data_list:
            data[2]=ElectricboxClient.objects.get(id=data[2]).client_name
            if data[-1] == 11:
                data[-1] = '添加'
            elif data[-1] == 12:
                data[-1] = '回收'
        return super(InterfaceVertifyJson, self).get_json(response)
