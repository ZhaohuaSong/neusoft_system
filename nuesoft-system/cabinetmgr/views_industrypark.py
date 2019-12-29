#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/10/2 12:30
# @Author  :
# @Site    :
# @File    : industrypark_source_views.py
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
from django.db.models import F
import json
import os
from subprocess import *
from ..zabbixmgr.constant import get_industry_park
from django.conf import settings
import pandas as pd

class IndustryParkList(TemplateView):
    template_name = 'cabinetmgr/industrypark.list.html'

    def get(self, request, *args, **kwargs):
        us = request.user.username
        industry_park =get_industry_park(us)
        context = self.get_context_data(**kwargs)
        context['industry_park'] = industry_park
        return self.render_to_response(context)

class IndustryParkJson(BaseDatatableView):
    '''
    Json 数据格式
    '''
    model = IndustryPark
    columns = ['id', 'id', 'park', 'bandwidth']
    order_columns = columns

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return self.model.objects.all()

class CreateIndustryPark(CreateView):

    form_class = CreateIndustryParkForm
    template_name = 'cabinetmgr/industrypark.add.html'

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        us = request.user.username
        industry_park =get_industry_park(us)
        context = self.get_context_data(form=form)
        context['industry_park'] = industry_park
        return self.render_to_response(context)

    #数据验证通过后执行
    def form_valid(self, form):
        self.save(form)
        return HttpResponseRedirect(reverse('cabinetmgr:industrypark.list'))

    def form_invalid(self, form):
        us = self.request.user.username
        industry_park =get_industry_park(us)
        context = self.get_context_data(form=form)
        context['industry_park'] = industry_park
        return self.render_to_response(context)

    #保存
    def save(self, form):
        industry_park = IndustryPark()
        park = form.cleaned_data['park']
        bandwidth = form.cleaned_data['bandwidth']
        industry_park.park = park
        industry_park.bandwidth = bandwidth
        industry_park.save()
        industry_id = IndustryPark.objects.get(park=park).id
        IndustryPark.objects.filter(id=industry_id).update(industry_id=industry_id)

class EditIndustryPark(UpdateView):
    '''
    编辑视图
    '''
    form_class = EditIndustryParkForm
    template_name = 'cabinetmgr/industrypark.edit.html'
    model = IndustryPark

    #获取当前用户参数
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = EditIndustryParkForm(self.object, None)
        context = self.get_context_data(form=form)
        us = self.request.user.username
        industry_park =get_industry_park(us)
        context['industry_park'] = industry_park
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form(data=request.POST, files=request.FILES)
        form.set_user(self.object)

        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    #数据验证通过后执行
    def form_valid(self, form):
        self.save(form)
        return HttpResponseRedirect(reverse('cabinetmgr:industrypark.list'))

    def save(self, form):
        park = form.cleaned_data['park']
        bandwidth = form.cleaned_data['bandwidth']
        industry_park = self.object
        industry_park.park = park
        industry_park.bandwidth = bandwidth
        industry_park.save()


def delete_industryparksource(request):
    '''
    批量删除
    :param request:
    :return:
    '''
    json_data = json.loads(request.GET.get('ids'))
    list_id_del = json_data['ids']
    if len(list_id_del) > 1:
        name_dict = {'code': '00', 'desc': '不可同时删除多个园区!'}
        return JsonResponse(name_dict)
    if Electricbox.objects.filter(industry_id=list_id_del[0]).exists() or IDCBuilding.objects.filter(park_id=list_id_del[0]).exists():
        name_dict = {'code': '00', 'desc': '园区业务未结束!'}
        return JsonResponse(name_dict)
    IndustryPark.objects.filter(id=list_id_del[0]).delete()
    name_dict = {'code': '00', 'desc': '删除成功!'}
    return JsonResponse(name_dict)

class IndustryBuildingList(TemplateView):
    template_name = 'cabinetmgr/industrybuilding.list.html'

    def get(self, request, *args, **kwargs):
        us = request.user.username
        industry_park =get_industry_park(us)
        context = self.get_context_data(**kwargs)
        context['industry_park'] = industry_park
        return self.render_to_response(context)

class IndustryBuildingJson(BaseDatatableView):
    '''
    Json 数据格式
    '''

    model = IDCBuilding
    columns = ['id', 'id', 'park_id', 'building_name', 'room_graph_file', 'id']
    order_columns = columns

    def get_json(self, response):
        data_list = response['data']
        for data in data_list:
            data[2] = IndustryPark.objects.get(id=data[2]).park
        return super(IndustryBuildingJson, self).get_json(response)

class CreateIndustryBuilding(CreateView):

    form_class = CreateIndustryBuildingForm
    template_name = 'cabinetmgr/industrybuilding.add.html'

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        us = request.user.username
        industry_park =get_industry_park(us)
        context = self.get_context_data(form=form)
        context['industry_park'] = industry_park
        return self.render_to_response(context)

    #数据验证通过后执行
    def form_valid(self, form):
        self.save(form)
        return HttpResponseRedirect(reverse('cabinetmgr:industrybuilding.list'))

    def form_invalid(self, form):
        us = self.request.user.username
        industry_park =get_industry_park(us)
        context = self.get_context_data(form=form)
        context['industry_park'] = industry_park
        return self.render_to_response(context)

    #保存
    def save(self, form):
        idc_building = IDCBuilding()
        building = form.cleaned_data['building']
        industry_id = form.cleaned_data['park'].id
        if IDCBuilding.objects.filter(park_id=industry_id).exists():
            building_id = max(list(IDCBuilding.objects.filter(industry_id=industry_id).values_list('building_id', flat=True))) + 1
        else:
            building_id = 1
        idc_building.building_name = building
        idc_building.park_id = industry_id
        idc_building.building_id = building_id
        idc_building.save()

class EditIndustryBuilding(UpdateView):
    '''
    编辑视图
    '''
    form_class = EditIndustryBuildingForm
    template_name = 'cabinetmgr/industrybuilding.edit.html'
    model = IDCBuilding

    #获取当前用户参数
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = EditIndustryBuildingForm(self.object, None)
        context = self.get_context_data(form=form)
        us = self.request.user.username
        industry_park =get_industry_park(us)
        context['industry_park'] = industry_park
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form(data=request.POST, files=request.FILES)
        form.set_user(self.object)

        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    #数据验证通过后执行
    def form_valid(self, form):
        self.save(form)
        return HttpResponseRedirect(reverse('cabinetmgr:industrybuilding.list'))

    def save(self, form):
        building = form.cleaned_data['building']
        industry_building = self.object
        industry_building.building = building
        industry_building.save()

def idc_room_add(request):

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
            if colns != 5:
                temp_list.append('表格字段数不正确')
                error_list.append(temp_list)
                tb_col = list(data_xls.columns)
                tb_col.insert(0, '错误信息')
                error_list.insert(0, tb_col)
                context['error_list'] = json.dumps(error_list)
                return render(request, 'cabinetmgr/uploadip/uploadip_fail.list.html', context)

            for i in range(0, len(df)):
                industry_name = df.iloc[i][0]
                building_name = df.iloc[i][1]
                room_name = df.iloc[i][2]
                total_box = df.iloc[i][3]
                handle = df.iloc[i][4]
                if not IndustryPark.objects.filter(park=industry_name).exists():
                    temp_list.append('园区不存在')
                    temp_list.extend([ str(t) for t in df.iloc[i] ])
                    error_list.append(temp_list)
                    continue
                if not IDCBuilding.objects.filter(building_name=building_name).exists():
                    temp_list.append('机楼不存在')
                    temp_list.extend([ str(t) for t in df.iloc[i] ])
                    error_list.append(temp_list)
                    continue
                if int(total_box) == 0:
                    temp_list.append('机柜数量不可为0')
                    temp_list.extend([ str(t) for t in df.iloc[i] ])
                    error_list.append(temp_list)
                    continue

                industry_id = IndustryPark.objects.get(park=industry_name).id
                building_id = IDCBuilding.objects.get(building_name=building_name).id
                if handle == '添加':
                    if BuildingRoom.objects.filter(room_name=room_name, building_id=building_id, industry_id=industry_id).exists():
                        temp_list.append('机房已存在')
                        temp_list.extend([ str(t) for t in df.iloc[i] ])
                        error_list.append(temp_list)
                        continue

                    BuildingRoom.objects.create(room_name=room_name,
                                                 building_id=building_id,
                                                 industry_id=industry_id,
                                                 total_box_num=int(total_box),
                                                 volume=0)
                    room_id = BuildingRoom.objects.get(industry_id=industry_id, building_id=building_id, room_name=room_name).id
                    DeviceRoom.objects.create(room=room_name,
                                              total_box=int(total_box),
                                              activate_box=0,
                                              unactivate_box=0,
                                              unuse_box=total_box,
                                              room_usage=0,
                                              check_box_power=3,
                                              design_box_power=780,
                                              sign_box_power=650,
                                              destribute_box_power=0,
                                              sign_box_power_usage=0,
                                              room_id=room_id,
                                              building_id=building_id,
                                              industry_id=industry_id)
                if handle == '删除':
                    if not BuildingRoom.objects.filter(room_name=room_name).exists():
                        temp_list.append('机房不存在')
                        temp_list.extend([ str(t) for t in df.iloc[i] ])
                        error_list.append(temp_list)
                        continue

                    if Electricbox.objects.filter(industry_id=industry_id, building_id=building_id, device_room=room_name).exists():
                        temp_list.append('机房存在机柜')
                        temp_list.extend([ str(t) for t in df.iloc[i] ])
                        error_list.append(temp_list)
                        continue

                    BuildingRoom.objects.filter(room_name=room_name,
                                                 building_id=building_id,
                                                 industry_id=industry_id,
                                                 total_box_num=int(total_box),
                                                 volume=0).delete()

            os.remove(settings.MEDIA_ROOT+'/ipworkorder/' + dirlist)
            if not error_list:
                context['result'] = '操作成功！'
                context['form'] = form
                return HttpResponseRedirect('/cabinetmgr/industrybuilding/list')
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

def room_graph_file(request):

    context = {}
    if request.method == 'POST':
        form = UpLoadFileForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.cleaned_data['filename']
            url = request.get_full_path()
            idc_build_id = int(re.findall('(\d+)\/$', url)[0])
            if IDCBuilding.objects.get(id=idc_build_id).room_graph_file == f:
                os.remove(settings.MEDIA_ROOT+'/tablemap/' + f)
            IDCBuilding.objects.filter(id=idc_build_id).update(room_graph_file=f)
            destination = open(settings.MEDIA_ROOT+'/tablemap/'+str(f).encode('gbk'),'wb+')
            for chunk in f.chunks():
                destination.write(chunk)
            destination.close()
            context['result'] = '操作成功！'
            context['form'] = form
            return HttpResponseRedirect('/cabinetmgr/industrybuilding/list')
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

def delete_idcbuilding(request):
    '''
    批量删除
    :param request:
    :return:
    '''
    json_data = json.loads(request.GET.get('ids'))
    list_id_del = json_data['ids']
    if len(list_id_del) > 1:
        name_dict = {'code': '00', 'desc': '不可同时删除多个几楼!'}
        return JsonResponse(name_dict)

    if Electricbox.objects.filter(building_id=list_id_del[0]).exists() or IDCBuilding.objects.filter(park_id=list_id_del[0]).exists():
        name_dict = {'code': '00', 'desc': '园区业务未结束!'}
        return JsonResponse(name_dict)
    IndustryPark.objects.filter(id=list_id_del[0]).delete()
    name_dict = {'code': '00', 'desc': '删除成功!'}
    return JsonResponse(name_dict)
