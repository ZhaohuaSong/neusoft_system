#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  :
# @Date         : 2017/1/11
# @Version      : 0.0.1
# @Link         :

"默认注释"

from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView
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
from ..vanilla import CreateView
from ..cabinetmgr.models import *
from pandas import DataFrame
import copy
from public_ways import *

def electribox_input(request):
    context = {}
    if request.method == 'POST':
        form = UpLoadFileForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.cleaned_data['filename']
            destination = open(settings.MEDIA_ROOT+'/network_device/'+str(f).encode('gbk'),'wb+')
            for chunk in f.chunks():
                destination.write(chunk)
            destination.close()
            dirlist = os.listdir(settings.MEDIA_ROOT+'/network_device/')[0].decode('gbk')
            # Filename.objects.create(file_name=dirlist)
            # last_month = (datetime.date.today().replace(day=1) - datetime.timedelta(days=1)).strftime("%Y-%m")
            # timeArray = time.strptime(str(last_month), "%Y-%m")
            # #转换成时间戳
            # timestamp = time.mktime(timeArray)
            data_xls = pd.read_excel(settings.MEDIA_ROOT+'/network_device/' + dirlist,sep=',',encoding='utf-8')
            df = data_xls.loc[:]
            colns = df.columns.size#列数 2
            rowns = df.iloc[:,0].size#行数 3

            for i in range(rowns):
                bn = re.search('(\d+)\-(\w)\-(\d+)', df.iloc[i][0]).groups()
                box_name = bn[1] + '-'+ bn[0] + '-' + bn[2]
                if Electricbox.objects.filter(box_name=box_name):
                    context['box_name'] = '机架已存在：%s'% box_name
                    return render(request, 'cabinetmgr/uploadmsg/electricbox_input_fail.list.html', context)
                if not BuildingRoom.objects.get(industry_id=1, building_id=1, room_name=df.iloc[i][0]):
                    context['room_name'] = '机房不存在：%s'% df.iloc[i][0]
                    return render(request, 'cabinetmgr/uploadmsg/electricbox_input_fail.list.html', context)
                room_id = BuildingRoom.objects.get(industry_id=1, building_id=1, room_name=df.iloc[i][0]).id
                NetworkDevice.objects.create(box_id=box_id,
                                         room_id=1,
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
                box_count = Electricbox.objects.filter(puboic_sql& Q(room_id=room_id)).count()
                if box_count == BuildingRoom.objects.get(puboic_sql& Q(room_name=df.iloc[i][0])).total_box_num:
                    BuildingRoom.objects.filter(puboic_sql& Q(room_name=df.iloc[i][0])).update(volume=1)
                update_device_room()

            os.remove(settings.MEDIA_ROOT+'/network_device/' + dirlist)
            context['result'] = '操作成功！'
            context['form'] = form
            return render(request, 'cabinetmgr/upload.success.list.html', context)

        elif str(form.errors) == '<ul class="errorlist"><li>filename<ul class="errorlist"><li>1</li></ul></li></ul>':#未选择文件
            print "====================================form.is_invalid()=========================================="
            for field in form:
                print field.errors
            print "====================================form.is_invalid()=========================================="
            return render(request, 'cabinetmgr/upload.fail.list.html', context)
        elif str(form.errors) == '<ul class="errorlist"><li>filename<ul class="errorlist"><li>0</li></ul></li></ul>':#文件已存在
            return render(request, 'cabinetmgr/upload.fail.one.list.html', context)
        elif str(form.errors) == '<ul class="errorlist"><li>filename<ul class="errorlist"><li>2</li></ul></li></ul>':#文件格式不正确
            return render(request, 'cabinetmgr/upload.fail.two.list.html', context)
    elif request.method == 'GET':
        try:
            form = UpLoadFileForm
            context['form'] = form
            context['imgPath'] = ''
        except Exception as e:
            print "++++++++++++++++++++++++<<<<<<<<<<<<<<<Exception>>>>>>>>>>>>>>>>>>>>>>>>>++++++++++++++++++"
            pass
        return render(request, 'cabinetmgr/upload_file.html', context)
