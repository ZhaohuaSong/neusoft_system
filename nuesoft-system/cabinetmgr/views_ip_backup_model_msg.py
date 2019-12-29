#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/11/6 17:24
# @Author  :
# @Site    :
# @File    : views_clientinterfacemgr.py
# @Software: PyCharm

from django.views.generic import TemplateView
from ..common.datatables.views import BaseDatatableView
from models import *
from forms import *
from django.http import HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse
from ..vanilla.model_views import *
import json
from django.conf import settings
import pandas as pd
from django.shortcuts import render
from ..zabbixmgr.constant import get_industry_park

class IpBackupModelMSGList(TemplateView):
    template_name = 'cabinetmgr/ip_backup_model_msg.html'

    def get(self, request, *args, **kwargs):
        us = request.user.username
        industry_park =get_industry_park(us)
        context = self.get_context_data(**kwargs)

        url = self.request.get_full_path()
        industry_id = int(re.findall('(\d+)$', url)[0])
        context['industry_id'] = industry_id
        context['industry_park'] = industry_park
        return self.render_to_response(context)

class IpBackupModelMSGJson(BaseDatatableView):
    model = IpBackupModel
    columns = ['id',
               'id',
               # 'begin_ip',
               # 'end_ip',
               'unit_name',
               # 'network_name',
               'unit_type',
               'bussiness_license_num',
               'unit_property',
               'provinces',
               'city',
               'county',
               'administrative_level',
               'profession',
               'address',
               'customer_name',
               'customer_phone',
               'customer_email',
               'physical_gateway',
               'usage_mode',
               'use_time',
               'use_way',
               'report_unit',
               'source_unit',
               'redistribution_unit',
               'record_representation',
               'gateway_ip_addr',
               'source_record',
               'relate_num']
    order_columns = columns

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        url = self.request.get_full_path()
        industry_id = int(re.findall('(\d+)$', url)[0])
        return self.model.objects.filter(industry_id=industry_id)

def backup_model_msg(request):
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
            industry_id = int(re.findall('(\d+)$', url)[0])
            if colns != 24:
                temp_list.append('表格字段数不正确')
                error_list.append(temp_list)
                tb_col = list(data_xls.columns)
                tb_col.insert(0, '错误信息')
                error_list.insert(0, tb_col)
                context['error_list'] = json.dumps(error_list)
                return render(request, 'cabinetmgr/uploadipmodel/uploadipmodel_fail.list.html', context)
            for i in range(0, len(df)):
                if IpBackupModel.objects.filter(unit_name=df.iloc[i][0], industry_id=industry_id).exists():
                    temp_list.append('客户信息已添加')
                    temp_list.extend([ str(t) for t in df.iloc[i] ])
                    error_list.append(temp_list)
                    continue
                IpBackupModel.objects.create(unit_name=df.iloc[i][0],
                                             unit_type=df.iloc[i][1],
                                             bussiness_license_num=df.iloc[i][2],
                                             unit_property=df.iloc[i][3],
                                             provinces=df.iloc[i][4],
                                             city=df.iloc[i][5],
                                             county=df.iloc[i][6],
                                             administrative_level=df.iloc[i][7],
                                             profession=df.iloc[i][8],
                                             address=df.iloc[i][9],
                                             customer_name=df.iloc[i][10],
                                             customer_phone=df.iloc[i][11],
                                             customer_email=df.iloc[i][12],
                                             physical_gateway=df.iloc[i][13],
                                             usage_mode=df.iloc[i][14],
                                             use_time=df.iloc[i][15],
                                             use_way=df.iloc[i][16],
                                             report_unit=df.iloc[i][17],
                                             source_unit=df.iloc[i][18],
                                             redistribution_unit=df.iloc[i][19],
                                             record_representation=df.iloc[i][20],
                                             gateway_ip_addr=df.iloc[i][21],
                                             source_record=df.iloc[i][22],
                                             relate_num=df.iloc[i][23],
                                             industry_id=industry_id)
            os.remove(settings.MEDIA_ROOT+'/interface_workorder/' + dirlist)
            if not error_list:
                context['result'] = '操作成功！'
                context['form'] = form
                return HttpResponseRedirect('/cabinetmgr/ipbackupmodelmsg/list/')
            else:
                tb_col = list(data_xls.columns)
                tb_col.insert(0, '错误信息')
                error_list.insert(0, tb_col)
                context['error_list'] = json.dumps(error_list)
                us = request.user.username
                industry_park =get_industry_park(us)
                context['industry_park'] = industry_park
                return render(request, 'cabinetmgr/uploadipmodel/uploadipmodel_fail.list.html', context)
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

def delete_ipbackupmode(request):
    json_data = json.loads(request.GET.get('ids'))
    id_del = json_data['ids']
    sql = Q()
    for i in id_del:
        sql |= Q(id=i)
    IpBackupModel.objects.filter(sql).delete()
    name_dict = {'code': '00', 'desc': '回退成功!'}
    return JsonResponse(name_dict)
