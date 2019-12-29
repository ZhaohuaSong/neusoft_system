#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/9/11 15:52
# @Author  :
# @Site    :
# @File    : views_electricbox.py
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
from public_ways import *
from django.conf import settings
import pandas as pd
from ..zabbixmgr.constant import get_industry_park

class ElectricboxList(TemplateView):
    template_name = 'cabinetmgr/electricbox.list.html'

    def get(self, request, *args, **kwargs):
        us = request.user.username
        industry_park =get_industry_park(us)
        context = self.get_context_data(**kwargs)

        url = self.request.get_full_path()
        industry_id = int(re.findall('(\d+)$', url)[0])
        context['industry_id'] = industry_id
        context['industry_park'] = industry_park
        client_list = IDCBuilding.objects.filter(park_id=industry_id).values_list('id', 'building_name')

        nodelist = []
        no = []
        i = 1
        for cl in client_list:
            dict_obj = {}
            dict_obj['text'] = cl[1]
            dict_obj['id'] = cl[0]
            dict_obj['tags'] = ['0']
            nodelist.append(dict_obj)
            no.append(cl)
            i += 1
        # context = self.get_context_data()
        context['request'] = request
        context['treedata'] = json.dumps(nodelist)
        return self.render_to_response(context)
    # NetworkDevice.objects.all().update(industry_id=1, building_id=1)
    # room_list = list(Electricbox.objects.filter(puboic_sql).values_list('room_id', flat=True))
    # for i in range(len(room_list)):
    #     id_list = list(Electricbox.objects.filter(puboic_sql & Q(room_id=room_list[i])).values_list('id', flat=True))
    #     sql = Q()
    #     for j in id_list:
    #         sql |= Q(box_id=j)
    #     NetworkDevice.objects.filter(sql).update(room_id=room_list[i])
    # NetworkDevice.objects.all().update()
    # for br in BuildingRoom.objects.filter(industry_id=1, building_id=1):
    #     Electricbox.objects.filter(industry_id=1, building_id=1, room_id=br.id).update(device_room=br.room_name)

class ElectricboxJson(BaseDatatableView):
    '''
    Json 数据格式
    '''

    model = Electricbox
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
               'id']
    order_columns = columns

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        url = self.request.get_full_path()
        industry_id = int(re.findall('(\d+)$', url)[0])
        building_id = self._querydict.get('id', 1)
        return self.model.objects.filter(industry_id=industry_id, building_id=building_id)

    def get_json(self, response):
        data_list = response['data']
        url = self.request.get_full_path()
        industry_id = int(re.findall('(\d+)$', url)[0])
        for data in data_list:
            if ',' not in data[4]:
                try:
                    data[4]=ElectricboxClient.objects.get(id=data[4], industry_id=industry_id).client_name
                except:
                    pass
            else:
                data[4]='多客户'
            if isinstance(data[7], datetime.datetime):
                data[7]=data[7].strftime("%Y-%m-%d")
            if isinstance(data[8], datetime.datetime):
                data[8]=data[8].strftime("%Y-%m-%d")
            if isinstance(data[9], datetime.datetime):
                data[9]=data[9].strftime("%Y-%m-%d")
            try:
                data[12] = SelectBox.objects.get(type_id=data[12]).box_type
            except:
                pass
        return super(ElectricboxJson, self).get_json(response)

def electribox_add(request):
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
                    room_name = df.iloc[i][2]
                    box_name = df.iloc[i][3]
                    power_rating = df.iloc[i][4]
                    threshold_rating = df.iloc[i][5]
                    if colns != 7:
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
                    if not BuildingRoom.objects.filter(building_id=building_id, industry_id=industry_id,room_name=room_name).exists():
                        temp_list.append('机房不存在')
                        temp_list.extend([ str(t) for t in df.iloc[i] ])
                        error_list.append(temp_list)
                        continue
                    if BuildingRoom.objects.get(building_id=building_id, industry_id=industry_id, room_name=room_name).volume == 1:
                        temp_list.append('机房已满')
                        temp_list.extend([ str(t) for t in df.iloc[i] ])
                        error_list.append(temp_list)
                        continue
                    if Electricbox.objects.filter(building_id=building_id, industry_id=industry_id,box_name=box_name).exists():
                        temp_list.append('机架已存在')
                        temp_list.extend([ str(t) for t in df.iloc[i] ])
                        error_list.append(temp_list)
                        continue

                    if str(box_name) == 'nan' or str(power_rating) == 'nan' or str(threshold_rating) == 'nan':
                        temp_list.append('字段不能为空')
                        temp_list.extend([ str(t) for t in df.iloc[i] ])
                        error_list.append(temp_list)
                        continue
                    try:
                        dr_sign_box_power_usage = Electricbox.objects.filter(building_id=building_id, industry_id=industry_id, device_room=room_name).values('room_id').annotate(sum_power=Sum('power_rating')).values('sum_power')[0]['sum_power']
                        dr_sign_box_power = DeviceRoom.objects.get(puboic_sql & Q(room=room_name)).sign_box_power
                        if float(dr_sign_box_power_usage) == float(dr_sign_box_power) or float(dr_sign_box_power_usage) + float(power_rating) > float(dr_sign_box_power):
                            temp_list.append('分配负载功率超过签约负载功率，不可添加机柜')
                            temp_list.extend([ str(t) for t in df.iloc[i] ])
                            error_list.append(temp_list)
                            continue
                    except:
                        pass
                    room_id = BuildingRoom.objects.get(industry_id=industry_id, building_id=building_id, room_name=room_name).id
                    Electricbox.objects.create(room_id=room_id,
                                               industry_id=industry_id,
                                               building_id=building_id,
                                               device_room=room_name,
                                               box_name=box_name,
                                               power_rating=float(power_rating),
                                               threshold_rating=float(threshold_rating),
                                               device_num=0,
                                               device_u_num=0,
                                               box_type=50)
                    if industry_id != 4:
                        name_block = box_name.split('-')
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
                                                        rack_power=power_rating,
                                                        rack_status='否')

                else:
                    temp_list.append('请选择添加操作')
                    temp_list.extend([ str(t) for t in df.iloc[i] ])
                    error_list.append(temp_list)
                    continue
                box_count = Electricbox.objects.filter(industry_id=industry_id, building_id=building_id, room_id=room_id).count()
                if box_count == BuildingRoom.objects.get(industry_id=industry_id, building_id=building_id, room_name=room_name).total_box_num:
                    BuildingRoom.objects.filter(industry_id=industry_id, building_id=building_id, room_name=room_name).update(volume=1)

            os.remove(settings.MEDIA_ROOT+'/electricbox/' + dirlist)
            if not error_list:
                update_device_room(industry_id, building_id)
                context['result'] = '操作成功！'
                context['form'] = form
                return HttpResponseRedirect('/cabinetmgr/electricbox/list/' + str(industry_id))
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

class CreateElectricbox(CreateView):
    model = Electricbox
    template_name = 'cabinetmgr/electricbox.add.html'
    form_class = CreateElectricboxForm

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def form_valid(self, form):
        self.save(form)
        return HttpResponseRedirect(reverse('cabinetmgr:electricbox.list'))

    def save(self, form):
        room_id = form.cleaned_data['room_name'].id
        device_room = form.cleaned_data['device_room'].room_name
        box_name = form.cleaned_data['box_name']
        client_name = form.cleaned_data['client_name']
        power_rating = form.cleaned_data['power_rating']
        threshold_rating = form.cleaned_data['threshold_rating']
        # on_state_date = form.cleaned_data['on_state_date']
        # power_on_date = form.cleaned_data['power_on_date']
        box_type = form.cleaned_data['box_type'].type_id
        Electricbox.objects.create(room_id=room_id,
                                   industry_id=1,
                                   building_id=1,
                                   device_room=device_room,
                                   box_name=box_name,
                                   client_name=client_name,
                                   power_rating=power_rating,
                                   threshold_rating=threshold_rating,
                                   # on_state_date=on_state_date,
                                   # power_on_date=power_on_date,
                                   box_type=box_type)
        box_count = Electricbox.objects.filter(puboic_sql& Q(room_id=room_id)).count()
        if box_count == BuildingRoom.objects.get(puboic_sql& Q(room_name=device_room)).total_box_num:
            BuildingRoom.objects.filter(puboic_sql& Q(room_name=device_room)).update(volume=1)
        update_device_room()

class EditElectricbox(UpdateView):
    '''
    编辑视图
    '''
    form_class = EditElectricboxForm
    template_name = 'cabinetmgr/electricbox.edit.html'
    model = Electricbox

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
        return HttpResponseRedirect(reverse('cabinetmgr:electricbox.list'))

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

def electricbox_batches_delete(request):
    '''
    批量删除
    :param request:
    :return:
    '''
    json_data = json.loads(request.GET.get('ids'))
    id_del = json_data['ids']
    if len(id_del) > 1:
        name_dict = {'code': '00', 'desc': '不可批量删除设备!'}
        return JsonResponse(name_dict)
    elif not Electricbox.objects.get(id=id_del[0]).device_num:

        Electricbox.objects.filter(industry_id=1, building_id=1, id=id_del[0]).delete()
        name_dict = {'code': '00', 'desc': '删除成功!'}
        update_device_room()
        # el = Electricbox.objects.get(puboic_sql & Q(id=id_del[0]))
        # BuildingRoom.objects.filter(puboic_sql & Q(id=el.room_id)).update(volume=0, total_box_num=el.total_box_num-1)
        return JsonResponse(name_dict)
    else:
        name_dict = {'code': '00', 'desc': '机柜内部还有设备，不可删除!'}
        return JsonResponse(name_dict)

