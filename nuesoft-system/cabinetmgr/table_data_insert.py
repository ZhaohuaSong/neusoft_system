#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/10/14 11:28
# @Author  :
# @Site    :
# @File    : data_import.py
# @Software: PyCharm

import os
import xlrd
import pandas as pd
from models import *
import re
import datetime
from django.conf import settings
from django.db.models import Sum, Q

def down_power_date_update():
    '''
    机柜最后一台设备下架时间
    :return:
    '''
    fn = '9月旗锐机房机柜设备清单及用电量汇总表20181011服务台V1.xlsx'.decode('utf-8')
    pd_excel = pd.read_excel('C:\\Users\\Administrator\\Desktop\\qirui\\' + fn, sheetname=1, encoding='utf-8')
    el = list(Electricbox.objects.all().values_list('box_name', flat=True))
    for i in el:
         #Electricbox.objects.filter(box_name=i).update(device_num=len(pe)) #计算机柜内部设备数量
        pe = pd_excel[pd_excel['机柜编号'.decode('utf-8')]==i]
        print len(pe), i

        li = pe['设备下架时间'.decode('utf-8')].values.tolist()
        try:
            l = max(li)
            if isinstance(l, datetime.datetime):
                print i
                Electricbox.objects.filter(box_name=i).update(down_power_date=l)
        except:
            pass

def box_device_insert():
    '''
    机柜内部设备导入
    :return:
    '''
    fn = '9月旗锐机房机柜设备清单及用电量汇总表20181011服务台V1.xlsx'.decode('utf-8')
    pd_excel = pd.read_excel('C:\\Users\\Administrator\\Desktop\\qirui\\' + fn, sheetname=1, encoding='utf-8')
    box_name = list(Electricbox.objects.all().values_list('box_name', flat=True))
    box_id = list(Electricbox.objects.all().values_list('id', flat=True))

    s = 0
    for i in box_name:
        pe = pd_excel[pd_excel['机柜编号'.decode('utf-8')]==i]

        on_state_date = pe['设备上架时间'.decode('utf-8')].values.tolist()
        power_on_date = pe['设备加电时间'.decode('utf-8')].values.tolist()
        down_power_date = pe['设备下架时间'.decode('utf-8')].values.tolist()
        device_code = pe['设备型号'.decode('utf-8')].values.tolist()
        device_type = pe['设备类型'.decode('utf-8')].values.tolist()
        start_u_num = pe['起始u数'.decode('utf-8')].values.tolist()
        end_u_num = pe['结束U数'.decode('utf-8')].values.tolist()
        device_num = pe['数量'.decode('utf-8')].values.tolist()
        device_statute = pe['设备状态'.decode('utf-8')].values.tolist()
        power_num = pe['设备电源数'.decode('utf-8')].values.tolist()
        device_alternating = pe['电源交流'.decode('utf-8')].values.tolist()
        device_threshold_rt = pe['铭牌功率（W）'.decode('utf-8')].values.tolist()
        network_device = []

        for j in range(len(on_state_date)):
            if not isinstance(pe.iloc[j,4], datetime.datetime): #上架日期
                pl = None
            else:
                if ':' in str(pe.iloc[j,4]):
                    pl = pe.iloc[j,4]
                else:
                    pl = None
            if not isinstance(power_on_date[j], datetime.datetime): #上电日期
                pod = None
            else:
                if ':' in str(power_on_date[j]):
                    pod = power_on_date[j]
                else:
                    pod = None
            if not isinstance(down_power_date[j], datetime.datetime): #下电日期
                dpd = None
            else:
                if ':' in str(down_power_date[j]):
                    dpd = down_power_date[j]
                else:
                    dpd = None
            if isinstance(device_threshold_rt[j], float): #额定功率
                if str(device_threshold_rt[j]) == 'nan':
                    dtr = None
                else:
                    dtr = device_threshold_rt[j]
            else:
                dtr = None
            if isinstance(start_u_num[j], float): #起始u数
                sun = None
            else:
                try:
                    sun = int(start_u_num[j])
                except:
                    sun = None
            if isinstance(end_u_num[j], float): #结束u数
                eun = None
            else:
                try:
                    eun = int(end_u_num[j])
                except:
                    eun = None
            if isinstance(device_code[j], float): #设备型号
                dcd = None
            else:
                dcd = device_code[j]
            if isinstance(device_type[j], float): #设备类型
                dtp = None
            else:
                dtp = device_type[j]
            if isinstance(device_num[j], float): #设备数量
                if str(device_num[j]) == 'nan':
                    dn = None
                else:
                    dn = int(device_num[j])
            else:
                dn = None
            if isinstance(device_statute[j], float): #设备状态
                dst = None
            else:
                dst = device_statute[j]
            if isinstance(power_num[j], float): #设备电源数
                pn = None
            else:
                pn = power_num[j]
            if isinstance(device_alternating[j], float): #电源交流
                dat = None
            else:
                dat = device_alternating[j]
            if sun is None or eun is None:
                total_u_num = None
            else:
                total_u_num = eun - sun + 1

            nd = NetworkDevice(box_id=box_id[s],
                               on_state_date=pl,
                      power_on_date=pod,
                      down_power_date=dpd,
                      device_code=dcd,
                      device_type=dtp,
                      start_u_num=sun,
                      end_u_num=eun,
                      total_u_num=total_u_num,
                      device_num=dn,
                      device_status=dst,
                      power_num=pn,
                      device_alternating=dat,
                      device_threshold_rt=dtr)
            network_device.append(nd)
        NetworkDevice.objects.bulk_create(network_device)
        s += 1

def device_u_num_update():
    '''
    机柜u数更新
    :return:
    '''
    fn = '9月旗锐机房机柜设备清单及用电量汇总表20181011服务台V1.xlsx'.decode('utf-8')
    pd_excel = pd.read_excel('C:\\Users\\Administrator\\Desktop\\qirui\\' + fn, sheetname=1, encoding='utf-8')
    el = list(Electricbox.objects.all().values_list('box_name', flat=True))
    for i in el:
        pe = pd_excel[pd_excel['机柜编号'.decode('utf-8')]==i]
        s_u = pe['起始u数'.decode('utf-8')].values.tolist()
        e_u = pe['结束U数'.decode('utf-8')].values.tolist()
        t_u = 0
        for j in range(len(s_u)):
            if isinstance(e_u[j], float):
                pass
            else:
                try:
                    t_u += int(str(e_u[j])) - int(str(s_u[j])) + 1
                except:
                    pass
        Electricbox.objects.filter(box_name=i).update(device_u_num=t_u)

def unactivate_box_insert():
    '''
    导入未分配或未用电机柜
    :return:
    '''
    name_list = ['旗锐IDC 201机房',
                 '旗锐IDC 202机房',
                 '旗锐IDC 203机房',
                 '旗锐IDC 301机房',
                 '旗锐IDC 302机房',
                 '旗锐IDC 303机房',
                 '旗锐IDC 402机房',
                 '旗锐IDC 403机房']
    for j in range(1, 9):
        dirlist = os.listdir(settings.MEDIA_ROOT+'/tablemap/')[0].decode('gbk')
        book = xlrd.open_workbook(settings.MEDIA_ROOT+'/tablemap/'+ dirlist, formatting_info=True)
        sheet = book.sheet_by_index(int(j))
        rows, cols = sheet.nrows, sheet.ncols

        first_row = 0
        first_col = 0
        last_row = 0
        last_col = 0
        for row in range(rows):
            for col in range(cols):
                thecell = sheet.cell(row, col)
                if thecell.value == 'A':
                    first_row = row
                    first_col = col
                    break
        for col in range(first_col, cols, 2):
            thecell = sheet.cell(first_row, col)
            if  thecell.value == '':
                last_col = col-1
                break
        i = 1
        for row in range(first_row, rows):
            thecell = sheet.cell(rows-i, first_col)
            i += 1
            if '加电□ 上架□' in thecell.value.encode('utf-8') or\
                '加电☑ 上架☑' in thecell.value.encode('utf-8') or\
                '加电□ 上架☑' in thecell.value.encode('utf-8') or\
                '加电□ 上架□' in thecell.value.encode('utf-8'):
                last_row = rows-i+1
                break

        el_list = []
        for row in range(first_row, last_row+1):
            val_dict = {}
            i = 0
            for col in range(first_col, last_col+1):
                val_bgx_dict = {}
                xfx = sheet.cell_xf_index(row, col)
                xf = book.xf_list[xfx]
                bgx = xf.background.pattern_colour_index
                value = sheet.cell(row, col).value
                val_bgx_dict[str(0)] = value
                val_bgx_dict[str(1)] = bgx
                if bgx == 10 or bgx == 50 or bgx == 13 or bgx== 40 or bgx==44:
                    if '-'in sheet.cell(row-1, col).value:
                        sr = re.search('(\d+)\-(\w+)\-(\d+)', sheet.cell(row-1, col).value).groups()
                        b_name = sr[1] + '-' + sr[0] + '-' + sr[2]
                        if not Electricbox.objects.filter(box_name=b_name).exists():
                            el = Electricbox(device_room=name_list[j-1],
                                                   room_id=j,
                                                   box_name=b_name,
                                                   client_name=sheet.cell(row-1, col-1).value,
                                                   box_type=bgx)
                            el_list.append(el)
                # elif bgx == 64 and sheet.cell(row, col).value == '':
                #     print
                #     if  '加电□ 上架□' in sheet.cell(row+1, col).value.encode('utf-8') or\
                #         '加电☑ 上架☑' in sheet.cell(row+1, col).value.encode('utf-8') or\
                #         '加电□ 上架☑' in sheet.cell(row+1, col).value.encode('utf-8') or\
                #         '加电□ 上架□' in sheet.cell(row+1, col).value.encode('utf-8'):
                #         el = Electricbox(device_room=name_list[j-1],
                #                                room_id=j,
                #                                box_name='',
                #                                client_name=sheet.cell(row-1, col-1).value,
                #                                box_type=bgx)
                #         el_list.append(el)

                i += 1
        Electricbox.objects.bulk_create(el_list)

def activate_box_insert():
    '''
    已加电机柜导入
    :return:
    '''
    fn = '9月旗锐机房机柜设备清单及用电量汇总表20181011服务台V1.xlsx'.decode('utf-8')
    pd_excel = pd.read_excel('C:\\Users\\Administrator\\Desktop\\qirui\\' + fn, sheetname=2, encoding='utf-8')
    col = [pd_excel.columns[0], pd_excel.columns[1] , pd_excel.columns[2], pd_excel.columns[3], pd_excel.columns[4], pd_excel.columns[7]]
    pd_col = pd_excel.loc[:,col]
    el_list = []
    for i in range(1, len(pd_col)):
        # print 'kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk'
        # print QRIDCRoom.objects.get(room_name=pd_col.iloc[i, 2]).id
        # print pd_col.iloc[i, 2]
        # print pd_col.iloc[i, 0]
        # print pd_col.iloc[i, 1]
        # print pd_col.iloc[i, 5]
        # print pd_col.iloc[i,5] - 0.2
        # print pd_col.iloc[i, 3], type(pd_col.iloc[i, 3])
        # print pd_col.iloc[i, 4]
        # print 'lllllllllllllllllllllllllllllllllll'
        if isinstance(pd_col.iloc[i,3], unicode):
            osd = None
        else:
            osd = pd_col.iloc[i,3]
        el = Electricbox(room_id=QRIDCRoom.objects.get(room_name=pd_col.iloc[i, 2]).id,
                         device_room=pd_col.iloc[i, 2],
                         box_name=pd_col.iloc[i,0],
                         client_name=pd_col.iloc[i,1],
                         power_rating=pd_col.iloc[i,5],
                         threshold_rating=pd_col.iloc[i,5] - 0.2,
                         on_state_date=osd,
                         power_on_date=pd_col.iloc[i,4],
                         box_type=40,
                         industry_id=1,
                         building_id=1)
        el_list.append(el)
    Electricbox.objects.bulk_create(el_list)

def device_num_update():
    '''
    机柜内部设备数量更新
    :return:
    '''
    fn = '9月旗锐机房机柜设备清单及用电量汇总表20181011服务台V1.xlsx'.decode('utf-8')
    pd_excel = pd.read_excel('C:\\Users\\Administrator\\Desktop\\qirui\\' + fn, sheetname=1, encoding='utf-8')
    el = list(Electricbox.objects.all().values_list('box_name', flat=True))
    for i in el:
        pe = pd_excel[pd_excel['机柜编号'.decode('utf-8')]==i]
        device_num = pe['数量'.decode('utf-8')].values.tolist()
        dn = 0
        for de in device_num:
            try:
                dn += int(de)
            except:
                pass
        Electricbox.objects.filter(box_name=i).update(device_num=dn)

def update_device_room_table():
    '''
    更新表device_room
    :return:
    '''
    puboic_sql = Q(industry_id=1) & Q(building_id=1)
    el = Electricbox.objects.filter(puboic_sql).values('room_id').annotate(sum_power=Sum('power_rating')).values('room_id', 'sum_power')
    for i in el:
        #机架总数=BuildingRoom
        #已装机=13 + 40
        #预占=10
        #可预占=50
        total = BuildingRoom.objects.get(puboic_sql& Q(id=i['room_id'])).total_box_num
        set_box = Electricbox.objects.filter(puboic_sql & Q(room_id=i['room_id']), Q(box_type=40)).count() #已上架加电
        will_set_box = Electricbox.objects.filter(puboic_sql & Q(room_id=i['room_id']), Q(box_type=10)).count() #已分配未加电未上架
        # not_set_box = Electricbox.objects.filter(puboic_sql & Q(room_id=i['room_id']), Q(box_type=50)).count() #未分配
        standby_box = Electricbox.objects.filter(puboic_sql & Q(room_id=i['room_id']), Q(box_type=13)).count()
        not_set_box = total-(set_box+will_set_box+standby_box)
        room = Electricbox.objects.filter(puboic_sql & Q(room_id=i['room_id']), Q(box_type=40))[0].device_room
        DeviceRoom.objects.create(
                                room=room,
                                room_id=i['room_id'],
                                building_id=1,
                                industry_id=1,
                              major='IDC机房',
                              total_box=total,
                              activate_box=set_box + standby_box,
                              unactivate_box=will_set_box,
                              unuse_box=not_set_box,
                              room_usage=round((float(set_box+standby_box))/float(total), 2),
                              check_box_power=3,
                              design_box_power=780,
                              sign_box_power=100,
                              destribute_box_power=i['sum_power'],
                              sign_box_power_usage=i['sum_power']/100
                              )
        total_box = list(DeviceRoom.objects.filter(puboic_sql).values_list('total_box', flat=True))
        activate_box = list(DeviceRoom.objects.filter(puboic_sql).values_list('activate_box', flat=True))
        unactivate_box = list(DeviceRoom.objects.filter(puboic_sql).values_list('unactivate_box', flat=True))
        unuse_box = list(DeviceRoom.objects.filter(puboic_sql).values_list('unuse_box', flat=True))
        IndustryPark.objects.filter(id=1).update(built=sum(total_box),
                                         activate=sum(activate_box)+sum(unactivate_box),
                                         unactivate=sum(unuse_box),
                                         usage_box=round(float(sum(activate_box)+sum(unactivate_box))/float(sum(total_box)), 2))
