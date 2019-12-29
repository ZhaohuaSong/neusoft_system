#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/6 16:35
# @Author  :
# @Site    :
# @File    : views_electricbox_workorder.py
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
class ElectricboxDistributeList(TemplateView):
    template_name = 'cabinetmgr/uploadelx/electricbox_distribute.list.html'
    def get(self, request, *args, **kwargs):
        url = self.request.get_full_path()
        id_list = re.findall('(\d+)\/(\d+)$', url)[0]
        self.workorder_id = int(id_list[0])

        us = request.user.username
        di[us] = self.workorder_id
        industry_park =get_industry_park(us)

        context = self.get_context_data(**kwargs)
        submit = IDCWorkorderPlatform.objects.get(id=self.workorder_id).submit
        operate_elbox = IDCWorkorderPlatform.objects.get(id=self.workorder_id).operate_elbox
        workorder_id = IDCWorkorderPlatform.objects.get(id=self.workorder_id).id
        context['workorder_id'] = workorder_id
        context['submit'] = submit
        context['operate_elbox'] = operate_elbox
        context['operate_type'] = 2
        context['industry_id'] = int(id_list[1])
        context['industry_park'] = industry_park
        return self.render_to_response(context)

class ElectricboxDistributeJson(BaseDatatableView):
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

    def get_json(self, response):
        data_list = response['data']
        url = self.request.path
        industry_id = int(re.findall('(\d+)$', url)[0])
        for data in data_list:
            data[4] = ElectricboxClient.objects.get(industry_id=industry_id, id=data[4]).client_name
            data[-1] = SelectBox.objects.get(id=data[-1]).box_type
            data[-2] = SelectBox.objects.get(type_id=data[-2]).box_type
        return super(ElectricboxDistributeJson, self).get_json(response)

    def get_initial_queryset(self):
        us = self.request.user.username
        workorder_id = di[us]
        url = self.request.path
        industry_id = int(re.findall('(\d+)$', url)[0])
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return self.model.objects.filter(industry_id=industry_id, workorder_id=workorder_id)

class EditElectricboxWorkorder(UpdateView):
    '''
    编辑视图
    '''
    form_class = EditElectricboxForm
    template_name = 'cabinetmgr/electricbox.edit.html'
    model = ElectricboxWorkorder

    # el = Electricbox.objects.all()
    # for i in el:
    #     Electricbox.objects.filter(id=i.id).update(pre_income_date=i.income_time)
    # Electricbox.objects.filter(box_type=10).update(pre_income_date=datetime.datetime.now())

    # for i in range(1 , 9):
    #     st = list(set(list(Electricbox.objects.filter(room_id=i).order_by('on_state_date').values_list('on_state_date', flat=True))))
    #     st.remove(None)
    #     st = min(st)
    #     Electricbox.objects.filter(room_id=i).update(pre_income_date=st)
    # Electricbox.objects.filter(box_type=50).update(pre_income_date=None)

    ip_total = ['172.16.178.0-172.16.178.255', '172.16.179.0-172.16.179.255']
    # ListData.objects.create(ip_list=json.dumps(ip_total))
    # ip = ListData.objects.all()[0]
    # print json.loads(ip.ip_list)
    # print type(json.loads(ip.ip_list))
    #获取当前用户参数
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = EditElectricboxForm(self.object, None)
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
        return HttpResponseRedirect('/cabinetmgr/electricboxdistribute/list/'+str(self.object.workorder_id))

    def save(self, form):
        room_id = form.cleaned_data['device_room'].id
        device_room = form.cleaned_data['device_room'].room_name
        box_name = form.cleaned_data['box_name']
        client_name = form.cleaned_data['client_name']
        power_rating = form.cleaned_data['power_rating']
        threshold_rating = form.cleaned_data['threshold_rating']
        # on_state_date = form.cleaned_data['on_state_date']
        # power_on_date = form.cleaned_data['power_on_date']
        box_type = form.cleaned_data['box_type'].type_id

        user = self.object

        Electricbox.objects.filter(room_id=user.room_id, industry_id=1, building_id=user.building_id, box_name=user.box_name).update(room_id=room_id,
                                                                                                                                     device_room=device_room,
                                                                                                                                     box_name=box_name,
                                                                                                                                     client_name=client_name,
                                                                                                                                     power_rating=power_rating,
                                                                                                                                     threshold_rating=threshold_rating,
                                                                                                                                     box_type=box_type)
        user.room_id = room_id
        user.device_room = device_room
        user.box_name = box_name
        user.client_name = client_name
        user.power_rating = power_rating
        user.threshold_rating = threshold_rating
        # user.on_state_date = on_state_date
        # user.power_on_date = power_on_date
        user.box_type = box_type
        user.save()

        update_device_room()

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

def electribox_workorder(request):
    context = {}
    if request.method == 'POST':
        form = UpLoadFileForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.cleaned_data['filename']
            destination = open(settings.MEDIA_ROOT+'/electricbox/'+str(f).encode('gbk'),'wb+')
            for chunk in f.chunks():
                destination.write(chunk)
            destination.close()
            dirlist = os.listdir(settings.MEDIA_ROOT+'/electricbox/')[0].decode('gbk')
            data_xls = pd.read_excel(settings.MEDIA_ROOT+'/electricbox/' + dirlist,sep=',',encoding='utf-8')
            df = data_xls.loc[:]
            colns = df.columns.size#列数 2
            rowns = df.iloc[:,0].size#行数 3
            # try:
            error_list = []
            url = request.get_full_path()
            industry_id = int(re.findall('(\d+)$', url)[0])
            for i in range(rowns):
                temp_list = []
                if df.iloc[i][-1] == '添加':
                    industry_name = df.iloc[i][0]
                    building_name = df.iloc[i][1]
                    client_name = df.iloc[i][2]
                    room_name = df.iloc[i][3]
                    box_name = df.iloc[i][4]
                    power_rating = df.iloc[i][5]
                    threshold_rating = df.iloc[i][6]
                    enter_date = df.iloc[i][7]
                    handle = df.iloc[i][8]
                    if colns != 9:
                        temp_list=[]
                        temp_list.append('表格字段数不正确')
                        error_list.append(temp_list)
                        tb_col = list(data_xls.columns)
                        tb_col.insert(0, '错误信息')
                        error_list.insert(0, tb_col)
                        context['error_list'] = json.dumps(error_list)
                        return render(request, 'cabinetmgr/uploadelx/uploadelx_fail.list.html', context)

                    if not IndustryPark.objects.filter(park=industry_name).exists():
                        temp_list.append('园区不存在')
                        temp_list.extend([ str(t) for t in df.iloc[i] ])
                        error_list.append(temp_list)
                        continue
                    # if not re.findall('\d+\-\w\-\d+', box_name):
                    #     temp_list.append('机柜编号不正确')
                    #     temp_list.extend([ str(t) for t in df.iloc[i] ])
                    #     error_list.append(temp_list)
                    #     continue
                    if not IDCBuilding.objects.filter(building_name=building_name, park_id=industry_id).exists():
                        temp_list.append('机楼不存在')
                        temp_list.extend([ str(t) for t in df.iloc[i] ])
                        error_list.append(temp_list)
                        continue
                    building_id = IDCBuilding.objects.get(park_id=industry_id,building_name=building_name).id
                    if not ElectricboxClient.objects.filter(client_name=client_name, industry_id=industry_id).exists():
                        temp_list.append('客户不存在，请先添加客户')
                        temp_list.extend([ str(t) for t in df.iloc[i] ])
                        error_list.append(temp_list)
                        continue
                    us = request.user.username
                    client_table = IDCWorkorderPlatform.objects.get(id=di[us], industry_id=industry_id).client_name

                    if str(client_table) != str(client_name):
                        temp_list.append('与工单客户不一致')
                        temp_list.extend([ str(t) for t in df.iloc[i] ])
                        error_list.append(temp_list)
                        continue
                    if not BuildingRoom.objects.filter(building_id=building_id, industry_id=industry_id,room_name=room_name).exists():
                        temp_list.append('机房不存在')
                        temp_list.extend([ str(t) for t in df.iloc[i] ])
                        error_list.append(temp_list)
                        continue
                    if BuildingRoom.objects.get(industry_id=industry_id, building_id=building_id, room_name=room_name).volume == 1:
                        temp_list.append('机房已满')
                        temp_list.extend([ str(t) for t in df.iloc[i] ])
                        error_list.append(temp_list)
                        continue
                    if Electricbox.objects.filter(building_id=building_id, industry_id=industry_id,box_name=box_name).exists():
                        temp_list.append('机架已存在')
                        temp_list.extend([ str(t) for t in df.iloc[i] ])
                        error_list.append(temp_list)
                        continue
                    if str(box_name) == 'nan' or str(power_rating) == 'nan' or str(threshold_rating) == 'nan' or str(enter_date) == 'nan':
                        temp_list.append('字段不能为空')
                        temp_list.extend([ str(t) for t in df.iloc[i] ])
                        error_list.append(temp_list)
                        continue

                    if not isinstance(enter_date, datetime.datetime):
                        temp_list.append('时间格式不正确')
                        temp_list.extend([ str(t) for t in df.iloc[i] ])
                        error_list.append(temp_list)
                        continue
                    try:
                        dr_sign_box_power_usage = Electricbox.objects.filter(building_id=building_id, industry_id=industry_id,device_room=room_name).values('room_id').annotate(sum_power=Sum('power_rating')).values('sum_power')[0]['sum_power']
                        dr_sign_box_power = DeviceRoom.objects.get(building_id=building_id, industry_id=industry_id,room=room_name).sign_box_power
                        if float(dr_sign_box_power_usage) == float(dr_sign_box_power) or float(dr_sign_box_power_usage) + float(power_rating) > float(dr_sign_box_power):
                            temp_list.append('分配负载功率超过签约负载功率，不可添加机柜')
                            temp_list.extend([ str(t) for t in df.iloc[i] ])
                            error_list.append(temp_list)
                            continue
                    except:
                        pass

                    handle_id = 11
                    client_id = ElectricboxClient.objects.get(industry_id=industry_id, client_name=client_name).id
                    room_id = BuildingRoom.objects.get(industry_id=industry_id, building_id=building_id, room_name=room_name).id
                    # Electricbox.objects.create(room_id=room_id,
                    #                            industry_id=1,
                    #                            building_id=1,
                    #                            device_room=room_name,
                    #                            box_name=box_name,
                    #                            client_name=str(client_id),
                    #                            power_rating=float(power_rating),
                    #                            threshold_rating=float(threshold_rating),
                    #                            device_num=0,
                    #                            device_u_num=0,
                    #                            box_type=10,
                    #                            income_time=enter_date)
                    # name_block = room_name.split('-')
                    # ContractRack.objects.create(building='旗锐',
                    #                             room=name_block[0],
                    #                             col=name_block[1],
                    #                             rack_pos=name_block[2])

                    us = request.user.username
                    ElectricboxWorkorder.objects.create(room_id=room_id,
                                                       industry_id=industry_id,
                                                       building_id=building_id,
                                                       device_room=room_name,
                                                       box_name=box_name,
                                                       client_name=client_id,
                                                        power_rating=float(power_rating),
                                                        threshold_rating=float(threshold_rating),
                                                        device_num=0,
                                                        device_u_num=0,
                                                       box_type=10,
                                                       handle_id=handle_id,
                                                       workorder_id=di[us])
                elif df.iloc[i][-1] == '删除':
                    building_name = df.iloc[i][0]
                    client_name = df.iloc[i][1]
                    room_name = df.iloc[i][2]
                    box_name = df.iloc[i][3]
                    handle = df.iloc[i][4]
                    if colns != 5:
                        temp_list=[]
                        temp_list.append('表格字段数不正确')
                        error_list.append(temp_list)
                        tb_col = list(data_xls.columns)
                        tb_col.insert(0, '错误信息')
                        error_list.insert(0, tb_col)
                        context['error_list'] = json.dumps(error_list)
                        return render(request, 'cabinetmgr/uploadelx/uploadelx_fail.list.html', context)
                    us = request.user.username
                    client_table = IDCWorkorderPlatform.objects.get(industry_id=industry_id, id=di[us]).client_name

                    if str(client_table) != str(client_name):
                        temp_list.append('与工单客户不一致')
                        temp_list.extend([ str(t) for t in df.iloc[i] ])
                        error_list.append(temp_list)
                        continue
                    handle_id = 12
                    room_id = BuildingRoom.objects.get(industry_id=industry_id, building_id=building_id, room_name=room_name).id
                    if not Electricbox.objects.filter(industry_id=industry_id, building_id=building_id, room_id=room_id, box_name=box_name).exists():
                        temp_list.append('机柜不存在')
                        temp_list.extend([ str(t) for t in df.iloc[i] ])
                        error_list.append(temp_list)
                        continue
                    if Electricbox.objects.get(room_id=room_id,
                                               building_id=building_id,
                                               box_name=box_name,
                                               industry_id=industry_id).device_num != 0:
                        temp_list.append('机柜存在设备，不可回收')
                        temp_list.extend([ str(t) for t in df.iloc[i] ])
                        error_list.append(temp_list)
                        continue
                    client_id = ElectricboxClient.objects.get(industry_id=industry_id, client_name=client_name).id
                    us = request.user.username
                    el = Electricbox.objects.get(room_id=room_id,
                                               building_id=building_id,
                                               box_name=box_name,
                                               industry_id=industry_id)
                    ElectricboxWorkorder.objects.create(room_id=room_id,
                                                       industry_id=industry_id,
                                                       building_id=building_id,
                                                       device_room=room_name,
                                                       box_name=box_name,
                                                       client_name=client_id,
                                                       power_rating=el.power_rating,
                                                       threshold_rating=el.threshold_rating,
                                                       on_state_date=el.on_state_date,
                                                       power_on_date=el.power_on_date,
                                                       down_power_date=el.down_power_date,
                                                       device_num=el.device_num,
                                                        device_u_num=el.device_u_num,
                                                       box_type=10,
                                                       handle_id=handle_id,
                                                       workorder_id=di[us])
                    # Electricbox.objects.filter(room_id=room_id,
                    #                            building_id=1,
                    #                            box_name=box_name,
                    #                            industry_id=1).delete()
                    # name_block = room_name.split('-')
                    # ContractRack.objects.filter(building='旗锐',
                    #                             room=name_block[0],
                    #                             col=name_block[1],
                    #                             rack_pos=name_block[2]).delete()
                else:
                    temp_list.append('请选择添加或删除操作')
                    temp_list.extend([ str(t) for t in df.iloc[i] ])
                    error_list.append(temp_list)
                    continue
                box_count = Electricbox.objects.filter(industry_id=industry_id, building_id=building_id, room_id=room_id).count()
                if box_count == BuildingRoom.objects.get(industry_id=industry_id, building_id=building_id, room_name=room_name).total_box_num:
                    BuildingRoom.objects.filter(industry_id=industry_id, building_id=building_id,room_name=room_name).update(volume=1)

            os.remove(settings.MEDIA_ROOT+'/electricbox/' + dirlist)
            if not error_list:
                update_device_room(industry_id, building_id)
                context['result'] = '操作成功！'
                context['form'] = form
                us = request.user.username
                context['workorder_id'] = di[us]
                return HttpResponseRedirect('/cabinetmgr/electricboxdistribute/list/' + str(di[us]) + '/' + str(industry_id))
            else:
                tb_col = list(data_xls.columns)
                tb_col.insert(0, '错误信息')
                error_list.insert(0, tb_col)
                context['error_list'] = json.dumps(error_list)
                us = request.user.username
                industry_park =get_industry_park(us)
                context['industry_park'] = industry_park
                return render(request, 'cabinetmgr/uploadelx/uploadelx_fail.list.html', context)

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

def elbox_retry_botton(request):
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
    ElectricboxWorkorder.objects.filter(workorder_id=workorder_id, industry_id=industry_id).delete()
    IDCWorkorderPlatform.objects.filter(id=workorder_id, industry_id=industry_id).update(submit=0,operate_elbox=1, workorder_status=0)
    VertifyRecord.objects.filter(workorder_id=workorder_id, operate_type=2, industry_id=industry_id).delete()
    return HttpResponseRedirect('/cabinetmgr/electricboxdistribute/list/' + str(workorder_id) + '/' + str(industry_id))

def delete_workorder_electricbox(request):
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
    ElectricboxWorkorder.objects.filter(sql).delete()
    name_dict = {'code': '00', 'desc': '回退成功!'}
    return JsonResponse(name_dict)

    # json_data = json.loads(request.GET.get('ids'))
    # id_del = json_data['ids']
    # for id_ in id_del:
    #     if ElectricboxWorkorder.objects.get(id=id_).handle_id == 11:
    #         elw = ElectricboxWorkorder.objects.get(id=id_)
    #         Electricbox.objects.filter(room_id=elw.room_id,
    #                                                    building_id=1,
    #                                                    box_name=elw.box_name,
    #                                                    industry_id=1).delete()
    #         ElectricboxWorkorder.objects.filter(id=id_).delete()
    #     else:
    #         elw = ElectricboxWorkorder.objects.get(id=id_)
    #         Electricbox.objects.create(room_id=elw.room_id,
    #                                    industry_id=1,
    #                                    building_id=1,
    #                                    device_room=elw.device_room,
    #                                    box_name=elw.box_name,
    #                                    client_name=elw.client_name,
    #                                    power_rating=elw.power_rating,
    #                                    threshold_rating=elw.threshold_rating,
    #                                    on_state_date=elw.on_state_date,
    #                                    power_on_date=elw.power_on_date,
    #                                    down_power_date=elw.down_power_date,
    #                                    device_num=elw.device_num,
    #                                    device_u_num=elw.device_u_num,
    #                                    box_type=elw.box_type)
    #         ElectricboxWorkorder.objects.filter(id=id_).delete()
    # update_device_room()
    # name_dict = {'code': '00', 'desc': '回退成功！'}
    # return JsonResponse(name_dict)

