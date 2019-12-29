#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/9/27 10:46
# @Author  :
# @Site    :
# @File    : cpu_data.py
# @Software: PyCharm5
# @Function:

from models import Interface, Items, History, ProcessorLoadItemid
import time
from django.db.models import Q

class CpuData():
    hs_id = []
    cpu_data = {}
    def get_hostid(self):
        '''
        获取正常运行主机hostid
        :return:
        '''
        self.hs_id = []
        interface = Interface.objects.using('zabbixdb').all()
        for i in interface:
            if i.hostid.available == 1:
                self.hs_id.append(i.hostid.hostid)

    def get_cpu_itemid(self):
        '''
        获取主机cpu load itemid
        :return:
        '''
        self.cpu_itemid_1 = []; self.cpu_itemid_5 = []; self.cpu_itemid_15 = []
        self.get_hostid()
        for hostid in self.hs_id:
            self.cpu_itemid_1.append(Items.objects.using('zabbixdb').get(Q(hostid=hostid) & Q(name='Processor load (1 min average per core)')).itemid)
            self.cpu_itemid_5.append(Items.objects.using('zabbixdb').get(Q(hostid=hostid) & Q(name='Processor load (5 min average per core)')).itemid)
            self.cpu_itemid_15.append(Items.objects.using('zabbixdb').get(Q(hostid=hostid) & Q(name='Processor load (15 min average per core)')).itemid)

    def get_cpu_load(self, cpu_itemid, args):
        '''
        cpu 负荷分组
        :param cpu_itemid:
        :return:
        '''
        self.val = []; self.itemid = []; self.level_1 = 0; self.level_2 = 0; self.level_3 = 0; self.level_4 = 0; self.level_5 = 0
        self.get_cpu_itemid()
        data = []
        for ited in cpu_itemid:
            delay = int(time.time()-120)
            self.history = History.objects.using('zabbixdb').filter(Q(clock__gte=delay) & Q(itemid=ited))
            for hist in self.history:
                if hist.itemid == ited:
                    if len(data) == 0:
                        data.append(hist.value)
                        data.append(ited)
                    elif len(data) != 0:
                        if data[1] < hist.clock:
                            data[0] = hist.value
                            data[1] = ited
            self.val.append(data[0])
            self.itemid.append(data[1])

        insert_data = []
        i = 0
        for v in self.val:
            type = 0
            if v >= 0 and v < 0.5:
                self.level_1 += 1
                type = args
            elif v >= 0.5 and v < 1:
                self.level_2 += 1
                type = 1+args
            elif v >= 1 and v < 1.5:
                self.level_3 += 1
                type = 2+args
            elif v >= 1.5 and v < 2:
                self.level_4 += 1
                type = 3+args
            else:
                self.level_5 += 1
                type = 4+args
            pro = ProcessorLoadItemid(type=type, itemid=self.itemid[i])
            insert_data.append(pro)
            i += 1
        try:
            ProcessorLoadItemid.objects.bulk_create(insert_data)
        except:
            pass

        temp = []
        temp.append(self.level_1)
        temp.append(self.level_2)
        temp.append(self.level_3)
        temp.append(self.level_4)
        temp.append(self.level_5)
        return temp

    def get_cpu_data(self):
        '''
        3个时段cpu负荷
        :return:
        '''
        self.get_cpu_itemid()
        ProcessorLoadItemid.objects.all().delete()
        self.cpu_data['data_1'] = self.get_cpu_load(self.cpu_itemid_1, 0)
        self.cpu_data['data_5'] = self.get_cpu_load(self.cpu_itemid_5, 5)
        self.cpu_data['data_15'] = self.get_cpu_load(self.cpu_itemid_15, 10)
