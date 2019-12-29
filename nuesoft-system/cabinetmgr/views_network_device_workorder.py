#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/12 15:19
# @Author  :
# @Site    :
# @File    : views_network_device_workorder.py
# @Software: PyCharm

from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView
from ..common.datatables.views import BaseDatatableView
from models import *
import json
import datetime, time
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from forms import *
from django.conf import settings
import pandas as pd
import os
import re
from ..vanilla import CreateView, UpdateView
from ..cabinetmgr.models import *
from pandas import DataFrame
import copy
from public_ways import *
from ..zabbixmgr.constant import get_industry_park

di = {}
class NetworkDeviceDistributeList(TemplateView):
    template_name = 'cabinetmgr/uploadnetd/network_device_distribute.list.html'
    def get(self, request, *args, **kwargs):
        url = self.request.get_full_path()
        id_list = re.findall('(\d+)\/(\d+)$', url)[0]
        self.workorder_id = int(id_list[0])
        us = request.user.username
        di[us] = self.workorder_id
        industry_park =get_industry_park(us)

        context = self.get_context_data(**kwargs)
        submit = IDCWorkorderPlatform.objects.get(id=self.workorder_id).submit
        operate_device = IDCWorkorderPlatform.objects.get(id=self.workorder_id).operate_device
        workorder_id = IDCWorkorderPlatform.objects.get(id=self.workorder_id).id
        context['workorder_id'] = workorder_id
        context['submit'] = submit
        context['operate_device'] = operate_device
        context['operate_type'] = 3
        context['industry_id'] = int(id_list[1])
        context['industry_park'] = industry_park
        return self.render_to_response(context)

class NeworkDeviceDistributeJson(BaseDatatableView):
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

    # Electricbox.objects.filter(device_room='旗锐IDC 403机房').update(device_room='403机房')

    # bn = list(Electricbox.objects.all().values_list('client_name', flat=True))
    # bn = set(bn)
    # for b in bn:
    #     print 'kkkk'
    #     if not ElectricboxClient.objects.filter(client_name=b).exists():
    #         ElectricboxClient.objects.create(client_name=b)
    # bnid = ElectricboxClient.objects.all()
    # for bd in bnid:
    #     Electricbox.objects.filter(client_name=bd.client_name).update(client_name=bd.id)

    def get_json(self, response):
        data_list = response['data']
        url = self.request.path
        industry_id = int(re.findall('(\d+)$', url)[0])
        for data in data_list:
            data[2]=Electricbox.objects.get(industry_id=industry_id, id=data[2]).box_name
            if isinstance(data[3], datetime.datetime):
                data[3]=data[3].strftime("%Y-%m-%d")
            if isinstance(data[4], datetime.datetime):
                data[4]=data[4].strftime("%Y-%m-%d")
            if data[-1] == 11:
                data[-1] = '添加'
            elif data[-1] == 12:
                data[-1] = '回收'
        return super(NeworkDeviceDistributeJson, self).get_json(response)

    def get_initial_queryset(self):
        us = self.request.user.username
        workorder_id = di[us]
        url = self.request.path
        industry_id = int(re.findall('(\d+)$', url)[0])
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return self.model.objects.filter(industry_id=industry_id, workorder_id=workorder_id)

def network_device_workorder(request):
    context = {}
    if request.method == 'POST':
        form = UpLoadFileForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.cleaned_data['filename']
            destination = open(settings.MEDIA_ROOT+'/network_device_workorder/'+str(f).encode('gbk'),'wb+')
            for chunk in f.chunks():
                destination.write(chunk)
            destination.close()
            dirlist = os.listdir(settings.MEDIA_ROOT+'/network_device_workorder/')[0].decode('gbk')
            data_xls = pd.read_excel(settings.MEDIA_ROOT+'/network_device_workorder/' + dirlist,sep=',',encoding='utf-8')
            df = data_xls.loc[:]
            colns = df.columns.size#列数 2
            rowns = df.iloc[:,0].size#行数 3
            # try:
            error_list = []
            url = request.get_full_path()
            industry_id = int(re.findall('(\d+)$', url)[0])
            if colns != 18:
                temp_list=[]
                temp_list.append('表格字段数不正确')
                error_list.append(temp_list)
                tb_col = list(data_xls.columns)
                tb_col.insert(0, '错误信息')
                error_list.insert(0, tb_col)
                context['error_list'] = json.dumps(error_list)
                return render(request, 'cabinetmgr/uploadnetd/uploadnetd_fail.list.html', context)
            for i in range(rowns):
                industry_name = df.iloc[i][0]
                building_name = df.iloc[i][1]
                client_name = df.iloc[i][2]
                room_name = df.iloc[i][3]
                box_name = df.iloc[i][4]
                on_state_date=df.iloc[i][5]
                power_on_date=df.iloc[i][6]
                down_power_date=df.iloc[i][7]
                start_u_num=df.iloc[i][8]
                end_u_num=df.iloc[i][9]
                device_code=df.iloc[i][11]
                device_type=df.iloc[i][12]
                device_status=df.iloc[i][13]
                power_num=df.iloc[i][14]
                device_alternating=df.iloc[i][15]
                device_threshold_rt=float(df.iloc[i][16])
                device_num=int(df.iloc[i][10])
                error_dict = {}
                temp_list = []
                if not IndustryPark.objects.filter(park=industry_name).exists():
                    temp_list.append('园区不存在')
                    temp_list.extend([ str(t) for t in df.iloc[i] ])
                    error_list.append(temp_list)
                    continue
                if not IDCBuilding.objects.filter(building_name=building_name, park_id=industry_id).exists():
                    temp_list.append('机楼不存在')
                    temp_list.extend([ str(t) for t in df.iloc[i] ])
                    error_list.append(temp_list)
                    continue
                if not ElectricboxClient.objects.filter(industry_id=industry_id, client_name=client_name).exists():
                    temp_list.append('客户不存在')
                    temp_list.extend([ str(t) for t in df.iloc[i] ])
                    error_list.append(temp_list)
                    continue
                building_id = IDCBuilding.objects.get(park_id=industry_id,building_name=building_name).id
                if not BuildingRoom.objects.filter(building_id=building_id, industry_id=industry_id,room_name=room_name).exists():
                    temp_list.append('机房不存在')
                    temp_list.extend([ str(t) for t in df.iloc[i] ])
                    error_list.append(temp_list)
                    continue
                if not Electricbox.objects.filter(building_id=building_id, industry_id=industry_id,box_name=box_name).exists():
                    temp_list.append('机架不存在')
                    temp_list.extend([ str(t) for t in df.iloc[i] ])
                    error_list.append(temp_list)
                    continue
                if not isinstance(on_state_date, datetime.datetime) or not isinstance(power_on_date, datetime.datetime):
                    temp_list.append('时间格式不正确')
                    temp_list.extend([ str(t) for t in df.iloc[i] ])
                    error_list.append(temp_list)
                    continue
                if df.iloc[i][-1] == '添加':
                    if on_state_date > power_on_date:
                        temp_list.append('加电时间不可小于上架时间')
                        temp_list.extend([ str(t) for t in df.iloc[i] ])
                        error_list.append(temp_list)
                        continue
                    if start_u_num > end_u_num:
                        temp_list.append('起始u数不可大于结束u数')
                        temp_list.extend([ str(t) for t in df.iloc[i] ])
                        error_list.append(temp_list)
                        continue
                    elbox = Electricbox.objects.get(industry_id=industry_id, building_id=building_id, device_room=room_name, box_name=box_name)
                    if NetworkDevice.objects.filter(Q(industry_id=industry_id) & Q(building_id=building_id) & Q(box_id=elbox.id) & Q(start_u_num=start_u_num)).exists():
                        temp_list.append('u数已经存在，请选择其他u数')
                        temp_list.extend([ str(t) for t in df.iloc[i] ])
                        error_list.append(temp_list)
                        continue
                    if NetworkDevice.objects.filter(Q(industry_id=industry_id) & Q(building_id=building_id) & Q(box_id=elbox.id) & Q(start_u_num=start_u_num)).exists():
                        temp_list.append('u数已经存在，请选择其他u数')
                        temp_list.extend([ str(t) for t in df.iloc[i] ])
                        error_list.append(temp_list)
                        continue
                    device_power = 0
                    if NetworkDevice.objects.filter(industry_id=industry_id, building_id=building_id, box_id=elbox.id).exists():
                        device_power = NetworkDevice.objects.filter(industry_id=industry_id,box_id=elbox.id).values('box_id').annotate(sum_power=Sum('device_threshold_rt'))[0]['sum_power']
                    if  (float(device_power) + float(df.iloc[i][-2]))/1000 >= elbox.power_rating:
                        temp_list.append('设备总功率超过机柜额定功率，不可添加设备')
                        temp_list.extend([ str(t) for t in df.iloc[i] ])
                        error_list.append(temp_list)
                        continue
                    # NetworkDevice.objects.create(box_id=elbox.id,
                    #                              room_id=elbox.room_id,
                    #                              building_id=1,
                    #                              industry_id=1,
                    #                              on_state_date=df.iloc[i][4],
                    #                            power_on_date=df.iloc[i][5],
                    #                            start_u_num=df.iloc[i][7],
                    #                            end_u_num=df.iloc[i][8],
                    #                            total_u_num=df.iloc[i][8] - df.iloc[i][7] + 1,
                    #                            device_code=df.iloc[i][10],
                    #                            device_type=df.iloc[i][11],
                    #                            device_status=df.iloc[i][12],
                    #                            power_num=df.iloc[i][13],
                    #                            device_alternating=df.iloc[i][14],
                    #                            device_threshold_rt=float(df.iloc[i][15]),
                    #                            device_num=int(df.iloc[i][9]))

                    us = request.user.username
                    NetworkDeviceWorkorder.objects.create(box_id=elbox.id,
                                                 room_id=elbox.room_id,
                                                 building_id=building_id,
                                                 industry_id=industry_id,
                                                client_name=client_name,
                                                 on_state_date=on_state_date,
                                               power_on_date=power_on_date,
                                               start_u_num=start_u_num,
                                               end_u_num=end_u_num,
                                               total_u_num=end_u_num - start_u_num + 1,
                                               device_code=device_code,
                                               device_type=device_type,
                                               device_status=device_status,
                                               power_num=power_num,
                                               device_alternating=device_alternating,
                                               device_threshold_rt=device_threshold_rt,
                                               device_num=device_num,
                                                handle_id=11,
                                                workorder_id=di[us])

                    # if Electricbox.objects.get(industry_id=1, building_id=1, id=elbox.id).on_state_date == None:
                    #     box_type = 40
                    #     Electricbox.objects.filter(id=elbox.id).update(on_state_date=df.iloc[i][4],
                    #                                                  power_on_date=df.iloc[i][5],
                    #                                                  down_power_date=None,
                    #                                                  device_num=df.iloc[i][9],
                    #                                                  device_u_num=df.iloc[i][8] - df.iloc[i][7] + 1,
                    #                                                  box_type=box_type)
                    # else:
                    #     el = Electricbox.objects.get(industry_id=1, building_id=1,id=elbox.id)
                    #     Electricbox.objects.filter(industry_id=1, building_id=1,id=elbox.id).update(
                    #                                                                         device_num=df.iloc[i][9]+el.device_num,
                    #                                                                         device_u_num=el.device_u_num+df.iloc[i][8] - df.iloc[i][7] + 1)
                elif df.iloc[i][-1] == '删除':
                    if not isinstance(down_power_date, datetime.datetime):
                        temp_list.append('时间格式不正确')
                        temp_list.extend([ str(t) for t in df.iloc[i] ])
                        error_list.append(temp_list)
                        continue

                    elbox = Electricbox.objects.get(industry_id=industry_id, building_id=building_id, device_room=df.iloc[i][2], box_name=df.iloc[i][3])
                    el = Electricbox.objects.get(industry_id=industry_id, building_id=building_id,id=elbox.id)
                    us = request.user.username
                    if not NetworkDevice.objects.filter(box_id=elbox.id,
                                                 room_id=elbox.room_id,
                                                 building_id=building_id,
                                                 industry_id=industry_id,
                                                 on_state_date=on_state_date,
                                               power_on_date=power_on_date,
                                               start_u_num=start_u_num,
                                               end_u_num=end_u_num,
                                               total_u_num=end_u_num - start_u_num + 1,
                                               device_code=device_code,
                                               device_type=device_type,
                                               device_status=device_status,
                                               power_num=power_num,
                                               device_alternating=device_alternating,
                                               device_threshold_rt=device_threshold_rt,
                                               device_num=device_num).exists():
                        temp_list.append('设备不存在')
                        temp_list.extend([ str(t) for t in df.iloc[i] ])
                        error_list.append(temp_list)
                        continue
                    # NetworkDevice.objects.filter(box_id=elbox.id,
                    #                              room_id=elbox.room_id,
                    #                              building_id=1,
                    #                              industry_id=1,
                    #                              on_state_date=df.iloc[i][4],
                    #                            power_on_date=df.iloc[i][5],
                    #                            start_u_num=df.iloc[i][7],
                    #                            end_u_num=df.iloc[i][8],
                    #                            total_u_num=df.iloc[i][8] - df.iloc[i][7] + 1,
                    #                            device_code=df.iloc[i][10],
                    #                            device_type=df.iloc[i][11],
                    #                            device_status=df.iloc[i][12],
                    #                            power_num=df.iloc[i][13],
                    #                            device_alternating=df.iloc[i][14],
                    #                            device_threshold_rt=float(df.iloc[i][15]),
                    #                            device_num=int(df.iloc[i][9])).delete()
                    NetworkDeviceWorkorder.objects.create(box_id=elbox.id,
                                                 room_id=elbox.room_id,
                                                 building_id=building_id,
                                                 industry_id=industry_id,
                                                 on_state_date=on_state_date,
                                               power_on_date=power_on_date,
                                                down_power_date=down_power_date,
                                               start_u_num=start_u_num,
                                               end_u_num=end_u_num,
                                               total_u_num=end_u_num - start_u_num + 1,
                                               device_code=device_code,
                                               device_type=device_type,
                                               device_status=device_status,
                                               power_num=power_num,
                                               device_alternating=device_alternating,
                                               device_threshold_rt=device_threshold_rt,
                                               device_num=device_num,
                                                handle_id=12,
                                                workorder_id=di[us])

                    # if el.device_num-int(df.iloc[i][9]) == 0:
                    #     Electricbox.objects.filter(id=elbox.id).update(down_power_date=datetime.datetime.now(),
                    #                                                    device_num=0,
                    #                                                    device_u_num=0,
                    #                                                    on_state_date=None,
                    #                                                    power_on_date=None,
                    #                                                    box_type=10,
                    #                                                    )
                    # else:
                    #     Electricbox.objects.filter(id=elbox.id).update(
                    #                                                  device_num=el.device_num-int(df.iloc[i][9]),
                    #                                                  device_u_num=el.device_u_num-int(df.iloc[i][8] - df.iloc[i][7] + 1))


            os.remove(settings.MEDIA_ROOT+'/network_device_workorder/' + dirlist)
            if not error_list:
                context['result'] = '操作成功！'
                context['form'] = form
                us = request.user.username
                context['workorder_id'] = di[us]
                return HttpResponseRedirect('/cabinetmgr/networkdevicedistribute/list/' + str(di[us]) + '/' + str(industry_id))
            else:
                tb_col = list(data_xls.columns)
                tb_col.insert(0, '错误信息')
                error_list.insert(0, tb_col)
                context['error_list'] = json.dumps(error_list)
                us = request.user.username
                industry_park =get_industry_park(us)
                context['industry_park'] = industry_park
                return render(request, 'cabinetmgr/uploadnetd/uploadnetd_fail.list.html', context)
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

class EditNeworkDeviceDistribute(UpdateView):
    form_class = EditNetworkDeviceForm
    template_name = 'cabinetmgr/network_device.edit.html'
    model = NetworkDeviceWorkorder

    #获取当前用户参数
    def get(self, request, *args, **kwargs):
        url = request.get_full_path()
        deviceid = int(re.findall('(\d+)\/$', url)[0])
        self.deviceid = deviceid
        us = request.user.username
        public_id.rq = request
        public_id.di[us] = self.deviceid

        self.object = self.get_object()
        form = EditNetworkDeviceForm(self.object, None)
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form(data=request.POST, files=request.FILES)
        form.set_user(self.object)

        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    # 数据验证通过后执行
    def form_valid(self, form):
        self.save(form)
        us_name = self.request.user.username
        box_id = di[us_name]
        return HttpResponseRedirect('/cabinetmgr/networkdevicedistribute/list/' + str(box_id))

    def save(self, form):
        on_state_date = form.cleaned_data['on_state_date']
        power_on_date = form.cleaned_data['power_on_date']
        start_u_num = form.cleaned_data['start_u_num']
        end_u_num = form.cleaned_data['end_u_num']
        total_u_num = end_u_num - start_u_num + 1
        device_code = form.cleaned_data['device_code']
        device_type = form.cleaned_data['device_type']
        device_status = str(form.cleaned_data['device_status'].box_type)
        power_num = str(form.cleaned_data['power_num'].box_type)
        device_alternating = form.cleaned_data['device_alternating']
        device_threshold_rt = form.cleaned_data['device_threshold_rt']
        device_num = form.cleaned_data['device_num']

        user = self.object
        user.on_state_date = on_state_date
        user.power_on_date = power_on_date
        user.start_u_num = start_u_num
        user.end_u_num = end_u_num
        user.total_u_num = total_u_num
        user.device_code = device_code
        user.device_code = device_code
        user.device_type = device_type
        user.device_status = device_status
        user.power_num = power_num
        user.device_alternating = device_alternating
        user.device_threshold_rt = device_threshold_rt
        user.device_num = device_num


        us_name = self.request.user.username
        box_id = public_id.di[us_name]
        nd_ = NetworkDeviceWorkorder.objects.get(id=box_id)
        box_id = nd_.box_id
        device_num = form.cleaned_data['device_num']
        start_u_num = form.cleaned_data['start_u_num']
        end_u_num = form.cleaned_data['end_u_num']
        total_u_num = end_u_num - start_u_num + 1
        el = Electricbox.objects.get(id=box_id)
        el_device_num = device_num - nd_.device_num
        el_total_u_num = total_u_num - nd_.total_u_num
        user.save()
        NetworkDevice.objects.filter(box_id=box_id, start_u_num=nd_.start_u_num, end_u_num=nd_.end_u_num).update(box_id=box_id,
                                                                                                         room_id=nd_.room_id,
                                                                                                         building_id=1,
                                                                                                         industry_id=1,
                                                                                                         on_state_date=on_state_date,
                                                                                                       power_on_date=power_on_date,
                                                                                                       start_u_num=start_u_num,
                                                                                                       end_u_num=end_u_num,
                                                                                                       total_u_num=total_u_num,
                                                                                                       device_code=device_code,
                                                                                                       device_type=device_type,
                                                                                                       device_status=device_status,
                                                                                                       power_num=power_num,
                                                                                                       device_alternating=device_alternating,
                                                                                                       device_threshold_rt=device_threshold_rt,
                                                                                                       device_num=device_num)
        Electricbox.objects.filter(id=box_id).update(device_num=el.device_num + el_device_num,device_u_num=el.device_u_num+el_total_u_num)

def delete_workorder_networkdevice(request):

    json_data = json.loads(request.GET.get('ids'))
    id_del = json_data['ids']
    sql = Q()
    for i in id_del:
        sql |= Q(id=i)
    NetworkDeviceWorkorder.objects.filter(sql).delete()
    name_dict = {'code': '00', 'desc': '回退成功!'}
    return JsonResponse(name_dict)

    # json_data = json.loads(request.GET.get('ids'))
    # id_del = json_data['ids']
    # for id_ in id_del:
    #     nd_ = NetworkDeviceWorkorder.objects.get(id=id_)
    #     if NetworkDeviceWorkorder.objects.get(id=id_).handle_id == 11:
    #         NetworkDevice.objects.filter(box_id=nd_.box_id,
    #                                              room_id=nd_.room_id,
    #                                              building_id=1,
    #                                              industry_id=1,
    #                                              on_state_date=nd_.on_state_date,
    #                                            power_on_date=nd_.power_on_date,
    #                                            start_u_num=nd_.start_u_num,
    #                                            end_u_num=nd_.end_u_num,
    #                                            total_u_num=nd_.total_u_num,
    #                                            device_code=nd_.device_code,
    #                                            device_type=nd_.device_type,
    #                                            device_status=nd_.device_status,
    #                                            power_num=nd_.power_num,
    #                                            device_alternating=nd_.device_alternating,
    #                                            device_threshold_rt=nd_.device_threshold_rt,
    #                                            device_num=nd_.device_num).delete()
    #         NetworkDeviceWorkorder.objects.filter(id=id_).delete()
    #         el = Electricbox.objects.get(id=nd_.box_id)
    #         if el.device_num-nd_.device_num == 0:
    #             Electricbox.objects.filter(id=nd_.box_id).update(down_power_date=datetime.datetime.now(),
    #                                                              on_state_date=None,
    #                                                                power_on_date=None,
    #                                                            device_num=0,
    #                                                            device_u_num=0,
    #                                                            box_type=10,
    #                                                            )
    #         else:
    #             Electricbox.objects.filter(id=nd_.box_id).update(
    #                                                          device_num=el.device_num-nd_.device_num,
    #                                                          device_u_num=el.device_u_num-nd_.total_u_num)
    #     else:
    #         NetworkDevice.objects.create(box_id=nd_.box_id,
    #                                      room_id=nd_.room_id,
    #                                      building_id=1,
    #                                      industry_id=1,
    #                                      on_state_date=nd_.on_state_date,
    #                                    power_on_date=nd_.power_on_date,
    #                                    start_u_num=nd_.start_u_num,
    #                                    end_u_num=nd_.end_u_num,
    #                                    total_u_num=nd_.total_u_num,
    #                                    device_code=nd_.device_code,
    #                                    device_type=nd_.device_type,
    #                                    device_status=nd_.device_status,
    #                                    power_num=nd_.power_num,
    #                                    device_alternating=nd_.device_alternating,
    #                                    device_threshold_rt=nd_.device_threshold_rt,
    #                                    device_num=nd_.device_num)
    #         NetworkDeviceWorkorder.objects.filter(id=id_).delete()
    #         if Electricbox.objects.get(industry_id=1, building_id=1, id=nd_.box_id).on_state_date == None:
    #             box_type = 40
    #             Electricbox.objects.filter(id=nd_.box_id).update(on_state_date=nd_.on_state_date,
    #                                                          power_on_date=nd_.power_on_date,
    #                                                          device_num=nd_.device_num,
    #                                                          device_u_num=nd_.total_u_num,
    #                                                          box_type=box_type)
    #         else:
    #             el = Electricbox.objects.get(industry_id=1, building_id=1,id=nd_.box_id)
    #             Electricbox.objects.filter(industry_id=1, building_id=1,id=nd_.box_id).update(
    #                                                                                 device_num=nd_.device_num+el.device_num,
    #                                                                                 device_u_num=el.device_u_num+nd_.total_u_num)
    # name_dict = {'code': '00', 'desc': '回退成功！'}
    # return JsonResponse(name_dict)

def device_retry_botton(request):
    '''
    清除记录准备重新添加
    operate_type:1-ip,2-elbox,3-device,4-port
    :param request:
    :return:
    '''
    url = request.get_full_path()
    id_list = re.findall('(\d+)\/(\d+)$', url)[0]
    workorder_id = int(id_list[0])
    industry_id = int(id_list[1])
    NetworkDeviceWorkorder.objects.filter(workorder_id=workorder_id, industry_id=industry_id).delete()
    IDCWorkorderPlatform.objects.filter(id=workorder_id, industry_id=industry_id).update(submit=0,operate_device=1, workorder_status=0)
    VertifyRecord.objects.filter(workorder_id=workorder_id, operate_type=3, industry_id=industry_id).delete()
    return HttpResponseRedirect('/cabinetmgr/networkdevicedistribute/list/' + str(workorder_id) + '/' + str(industry_id))
