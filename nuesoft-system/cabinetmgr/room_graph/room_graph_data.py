#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    :
# @Author  : ljh
# @Site    :
# @File    : room_graph_data.py
# @Software: PyCharm

import os, xlrd
from django.conf import settings
import re
from ..models import *
from django.db.models import Q

class RoomGraphData():
    def __init__(self, room_id, building_id, industry_id):
        self.room_id = room_id
        self.building_id = building_id
        self.industry_id = industry_id

        graph_file = IDCBuilding.objects.get(park_id=self.industry_id, building_id=self.building_id).room_graph_file
        self.book = xlrd.open_workbook(settings.MEDIA_ROOT+'/tablemap/' + graph_file, formatting_info=True)
        room_name = BuildingRoom.objects.get(id=self.room_id).room_name
        self.sheet = self.book.sheet_by_name(room_name)

    def set_row_col(self):

        rows, cols = self.sheet.nrows, self.sheet.ncols
        first_row = 0
        first_col = 0
        last_row = 0
        last_col = 0
        for row in range(rows):
            for col in range(cols):
                thecell = self.sheet.cell(row, col)
                if thecell.value == 'first':
                    first_row = row + 1
                    first_col = col
                    break
        for col in range(first_col, cols):
            thecell = self.sheet.cell(first_row-1, col)

            if  thecell.value == 'last_col':
                last_col = col-1
                break
        for row in range(first_row, rows):
            thecell = self.sheet.cell(row, first_col)
            if thecell.value == 'last_row':
                last_row = row-1
                break
        return first_col, first_row, last_col, last_row

    def create_data(self, box_list, table):
        sql = Q()
        for bn in box_list:
            sql |= Q(box_name=bn)
        bcb_data_li = list(Electricbox.objects.filter(sql & Q(room_id=self.room_id) & Q(building_id=self.building_id) & Q(industry_id=self.industry_id)).values_list('box_name',
                                                                                                                        'client_name',
                                                                                                                        'box_type',
                                                                                                                        'id',
                                                                                                                        'on_state_date',
                                                                                                                        'power_on_date',
                                                                                                                        'down_power_date'))
        for row_data in table:
            for key in row_data:
                if '-' in row_data[key]['0']:
                    box_exist = False
                    for i in range(len(bcb_data_li)):
                        if row_data[key]['0'] == bcb_data_li[i][0]:
                            box_exist = True
                            break
                    if box_exist:
                        try:
                            row_data[key]['2'] = bcb_data_li[i][3]
                        except:
                            row_data[key]['2'] = None
                        try:
                            row_data[key]['3'] = bcb_data_li[i][4].strftime('%Y-%m-%d')
                        except:
                            row_data[key]['3'] = bcb_data_li[i][4]
                        try:
                            row_data[key]['4'] = bcb_data_li[i][5].strftime('%Y-%m-%d')
                        except:
                            row_data[key]['4'] = bcb_data_li[i][5]
                        try:
                            row_data[key]['5'] = bcb_data_li[i][6].strftime('%Y-%m-%d')
                        except:
                            row_data[key]['5'] = bcb_data_li[i][6]
                        try:
                            cl_name = ElectricboxClient.objects.get(id=bcb_data_li[i][1]).client_name
                        except:
                            cl_name = '无'
                        row_data[key]['6'] = cl_name
                        bcb_data_li.pop(i)
                    if not bcb_data_li:
                        break
        return table

    def qirui_data_list(self):
        first_col, first_row, last_col, last_row = self.set_row_col()

        table = []
        box_list = []
        for row in range(first_row, last_row+1):
            val_dict = {}
            i = 0
            is_road = False
            for col in range(first_col, last_col+1):
                val_bgx_dict = {}
                xfx = self.sheet.cell_xf_index(row, col)
                xf = self.book.xf_list[xfx]
                bgx = xf.background.pattern_colour_index
                value = self.sheet.cell(row, col).value
                if re.search('\d+\-\w+\-\d+', str(value)):
                # if '-' in value:
                    box_list.append(value)

                if not is_road:
                # if '-' in value or '□' in value or '☑' in value or '列头柜' in value or '机房立柱' in value or re.search('^[A-Z]', value):
                    val_bgx_dict['0'] = value
                    val_bgx_dict['1'] = bgx
                    is_road = True
                else:
                    if row == first_row:
                        val_bgx_dict['0'] = '过道'
                        val_bgx_dict['1'] = ''
                    else:
                        val_bgx_dict['0'] = ''
                        val_bgx_dict['1'] = ''
                    is_road = False
                val_bgx_dict['2'] = ''
                val_bgx_dict['3'] = ''
                val_bgx_dict['4'] = ''
                val_bgx_dict['5'] = ''
                val_bgx_dict['6'] = ''
                val_dict[str(i)] = val_bgx_dict
                i += 1
            table.append(val_dict)

        return self.create_data(box_list, table)

    def huaxinyuan_G3_data_list(self):
        first_col, first_row, last_col, last_row = self.set_row_col()

        table = []
        box_list = []
        for row in range(first_row, last_row+1):
            val_dict = {}
            i = 0
            is_road = False
            for col in range(first_col, last_col+1):
                val_bgx_dict = {}
                xfx = self.sheet.cell_xf_index(row, col)
                xf = self.book.xf_list[xfx]
                bgx = xf.background.pattern_colour_index
                value = self.sheet.cell(row, col).value
                # if re.search('\d+\-\w+\-\d+', str(value)):
                if '-' in value:
                    box_list.append(value)

                # if not is_road:
                if '-' in value or '□' in value or '☑' in value or '列头柜' in value or '机房立柱' in value or re.search('^[A-Z]', value):
                    val_bgx_dict['0'] = value
                    val_bgx_dict['1'] = bgx
                    is_road = True
                else:
                    if col == first_col and not self.sheet.cell(row, first_col+1).value:
                        val_bgx_dict['0'] = '过道'
                        val_bgx_dict['1'] = ''
                    else:
                        val_bgx_dict['0'] = ''
                        val_bgx_dict['1'] = ''
                    is_road = False
                val_bgx_dict['2'] = ''
                val_bgx_dict['3'] = ''
                val_bgx_dict['4'] = ''
                val_bgx_dict['5'] = ''
                val_bgx_dict['6'] = ''
                val_dict[str(i)] = val_bgx_dict
                i += 1
            table.append(val_dict)

        return self.create_data(box_list, table)

    def huaxinyuan_G6_data_list(self):
        first_col, first_row, last_col, last_row = self.set_row_col()

        table = []
        box_list = []
        for row in range(first_row, last_row+1):
            val_dict = {}
            i = 0
            is_road = False
            for col in range(first_col, last_col+1):
                val_bgx_dict = {}
                xfx = self.sheet.cell_xf_index(row, col)
                xf = self.book.xf_list[xfx]
                bgx = xf.background.pattern_colour_index
                value = self.sheet.cell(row, col).value
                # if re.search('\d+\-\w+\-\d+', str(value)):
                if '-' in value:
                    box_list.append(value)

                # if not is_road:
                if '-' in value:
                    val_bgx_dict['0'] = value
                    val_bgx_dict['1'] = bgx
                    is_road = True
                else:
                    if col == first_col and not self.sheet.cell(row, first_col+1).value:
                        val_bgx_dict['0'] = '过道'
                        val_bgx_dict['1'] = ''
                    else:
                        val_bgx_dict['0'] = ''
                        val_bgx_dict['1'] = ''
                    is_road = False
                val_bgx_dict['2'] = ''
                val_bgx_dict['3'] = ''
                val_bgx_dict['4'] = ''
                val_bgx_dict['5'] = ''
                val_bgx_dict['6'] = ''
                val_dict[str(i)] = val_bgx_dict
                i += 1
            table.append(val_dict)

        return self.create_data(box_list, table)
