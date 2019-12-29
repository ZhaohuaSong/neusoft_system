#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/10/29 15:22
# @Author  :
# @Site    :
# @File    : public_ways.py
# @Software: PyCharm


from forms import *
from django.db.models import Sum

puboic_sql = Q(industry_id=1) & Q(building_id=1)


def update_device_room(industry_id, building_id):
    '''
    更新device_room表
    :return:
    '''
    puboic_sql = Q(industry_id=industry_id) & Q(building_id=building_id)
    el = Electricbox.objects.filter(industry_id=industry_id, building_id=building_id).values('room_id').annotate(sum_power=Sum('power_rating')).values('room_id', 'sum_power')
    dr_sign_box_power = list(DeviceRoom.objects.filter(industry_id=industry_id, building_id=building_id).values_list('sign_box_power', flat=True))
    j = 0
    for i in el:
        #机架总数=BuildingRoom
        #已装机=13 + 40
        #预占=10
        #可预占=50
        total = BuildingRoom.objects.get(puboic_sql& Q(id=i['room_id'])).total_box_num
        set_box = Electricbox.objects.filter(puboic_sql & Q(room_id=i['room_id']), Q(box_type=40)).count() #已上架加电
        will_set_box = Electricbox.objects.filter(puboic_sql & Q(room_id=i['room_id']), Q(box_type=10)).count() #已分配未加电未上架
        not_use = Electricbox.objects.filter(puboic_sql & Q(room_id=i['room_id']), Q(box_type=50)).count() #未分配
        standby_box = Electricbox.objects.filter(puboic_sql & Q(room_id=i['room_id']), Q(box_type=13)).count() #已分配已上架未加电
        not_set_box = total-(set_box+will_set_box+standby_box)
        if total != (set_box+will_set_box+standby_box+not_use):
            volume = 0
        else:
            volume = 1
        BuildingRoom.objects.filter(puboic_sql& Q(id=i['room_id'])).update(volume=volume)
        room = BuildingRoom.objects.get(puboic_sql& Q(id=i['room_id'])).room_name
        # room = Electricbox.objects.filter(puboic_sql & Q(room_id=i['room_id']), Q(box_type=40))[0].device_room
        DeviceRoom.objects.filter(puboic_sql & Q(room_id=i['room_id'])).update(
                                room=room,
                              major='IDC机房',
                              total_box=total,
                              activate_box=set_box + standby_box,
                              unactivate_box=will_set_box,
                              unuse_box=not_use,
                              room_usage=round((float(set_box+standby_box))/float(total), 2),
                              destribute_box_power=i['sum_power'],
                              sign_box_power_usage=i['sum_power']/dr_sign_box_power[j]
                              )
        j += 1
    total_box = list(DeviceRoom.objects.filter(puboic_sql).values_list('total_box', flat=True))
    activate_box = list(DeviceRoom.objects.filter(puboic_sql).values_list('activate_box', flat=True))
    unactivate_box = list(DeviceRoom.objects.filter(puboic_sql).values_list('unactivate_box', flat=True))
    unuse_box = list(DeviceRoom.objects.filter(puboic_sql).values_list('unuse_box', flat=True))
    IndustryPark.objects.filter(id=industry_id).update(built=sum(total_box),
                                     activate=sum(activate_box),
                                     unactivate=sum(total_box)-sum(activate_box),
                                     usage_box=round(float(sum(activate_box)+sum(unactivate_box))/float(sum(total_box)), 2))
