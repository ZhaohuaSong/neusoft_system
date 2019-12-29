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
from ..zabbixmgr.constant import get_industry_park

allFileNum = 0
global fname
page = 0

#返回信息
#20：文件不存在
#21：没有输入查询条件
#22：无匹配列
#23：列数太多
#24：当前块无匹配信息
#-1：继续
#1：完成

#获取文件名列表
def printPath():
    """
     ===============================================================================
     function：    获取文件名列表
     developer:
     add-time      2017/1/17
     ===============================================================================
    """
    level = 1
    path = settings.MEDIA_ROOT+'/uploadfiles'
    global allFileNum
    '''''
    打印一个目录下的所有文件夹和文件
    '''
    # 所有文件夹，第一个字段是次目录的级别
    dirList = []
    # 所有文件
    fileList = []
    # 返回一个列表，其中包含在目录条目的名称(google翻译)
    files = os.listdir(path)
    # print files
    # 先添加目录级别
    dirList.append(str(level))
    for f in files:
        if(os.path.isdir(path + '/' + f)):
            # 排除隐藏文件夹。因为隐藏文件夹过多
            if(f[0] == '.'):
                pass
            else:
                # 添加非隐藏文件夹
                dirList.append(f)
        if(os.path.isfile(path + '/' + f)):
            # 添加文件
            fileList.append(f)
    return fileList

#获取路径文件名列表
def GetFileList(dir, fileList):
    """
     ===============================================================================
     function：    获取路径名+文件名列表
     developer:
     add-time      2017/1/17
     ===============================================================================
    """



    newDir = dir
    if os.path.isfile(dir):
        fileList.append(dir)
        # print fileList
    elif os.path.isdir(dir):
        for s in os.listdir(dir):
            #如果需要忽略某些文件夹，使用以下代码
            #if s == "xxx":
                #continue
            # print s
            newDir=os.path.join(dir,s)
            # print newDir
            GetFileList(newDir, fileList)
    return fileList

def UpLoadFileConfig(request):
    '''
    ============================================================================
    developer:
    add-time:   2016.12.19
    note:       文件上传
    ============================================================================
    '''
    context = {}
    if request.method == 'POST':
        form = UpLoadFileForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.cleaned_data['filename']
            destination = open(settings.MEDIA_ROOT+'/uploadfiles/'+str(f).encode('gbk'),'wb+')
            for chunk in f.chunks():
                destination.write(chunk)
            destination.close()
            dirlist = os.listdir(settings.MEDIA_ROOT+'/uploadfiles/')[0].decode('gbk')
            error_list = []
            try:
                timestrArry = re.findall('(\d+)年(\d+)月', dirlist.encode('utf-8'))[0]
                timestr = timestrArry[0] + '-' + timestrArry[1]
                # Filename.objects.create(file_name=dirlist)
                # last_month = (datetime.date.today().replace(day=1) - datetime.timedelta(days=1)).strftime("%Y-%m")
                timeArray = time.strptime(str(timestr), "%Y-%m")
                #转换成时间戳
                timestamp = time.mktime(timeArray)
                if HistoryPower.objects.filter(clock=timestamp).exists():
                    HistoryPower.objects.filter(clock=timestamp).delete()
            except:
                temp_list = []
                temp_list.append('表名不正确')
                error_list.append(temp_list)
                tb_col = []
                tb_col.insert(0, '错误信息')
                error_list.insert(0, tb_col)
                context['error_list'] = json.dumps(error_list)
                return render(request, 'cabinetmgr/uploadifc/uploadifc_fail.list.html', context)
            data_xls = pd.read_excel(settings.MEDIA_ROOT+'/uploadfiles/' + dirlist,sep=',',encoding='utf-8', sheetname=2)
            df = data_xls.loc[:,[data_xls.columns[0],data_xls.columns[2],data_xls.columns[8]]]
            historypower = []
            for i in range(1, len(df)-1):
                bn = df.iloc[i][0].split('-')
                try:
                    b = int(bn[1])
                    box_name = bn[1] + '-' + bn[0] + '-' + bn[2]
                except:
                    temp_list = []
                    temp_list.append('机柜编号不正确')
                    temp_list.extend([ str(t) for t in df.iloc[i] ])
                    error_list.append(temp_list)
                    continue

                url = request.path
                industry_id = int(re.findall('(\d+)$', url)[0])
                try:
                    el = Electricbox.objects.get(building_id=1, industry_id=industry_id, box_name=box_name)
                    if df.iloc[i][2] < el.threshold_rating:
                        level = 1
                    elif df.iloc[i][2] >= el.threshold_rating and df.iloc[i][2] < el.power_rating:
                        level = 2
                    else:
                        level = 3
                    hp =  HistoryPower(boxid=el.id,
                                                room_id=el.room_id,
                                                building_id=1,
                                                industry_id=industry_id,
                                            value=round(float(df.iloc[i][2]), 2),
                                            level=level,
                                            clock=timestamp)
                    historypower.append(hp)
                except:
                    temp_list = []
                    temp_list.append('机柜不存在或功率不存在')
                    temp_list.extend([ str(t) for t in df.iloc[i] ])
                    error_list.append(temp_list)
                    continue

            HistoryPower.objects.bulk_create(historypower)

            os.remove(settings.MEDIA_ROOT+'/uploadfiles/' + dirlist)
            if not error_list:
                context['result'] = '操作成功！'
                context['form'] = form
                return render(request, 'cabinetmgr/upload.success.list.html', context)
            else:
                tb_col = list(df.columns)
                tb_col.insert(0, '错误信息')
                error_list.insert(0, tb_col)
                context['error_list'] = json.dumps(error_list)
                us = request.user.username
                industry_park =get_industry_park(us)
                context['industry_park'] = industry_park
                return render(request, 'cabinetmgr/uploadifc/uploadifc_fail.list.html', context)

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
        us = request.user.username
        industry_park =get_industry_park(us)
        context['industry_park'] = industry_park
        return render(request, 'cabinetmgr/upload_file.html', context)
