#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  :
# @Date         : 2017/1/11
# @Version      : 0.0.1
# @Link         :

"默认注释"

from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView
import json
from django.conf import settings
import os
import xlrd

class FileListView(TemplateView):
    """
     ===============================================================================
     function：    显示文件链接列表
     developer:
     add-time      2017/2/4
     ===============================================================================
    """
    template_name = 'filemanage/file.list.html'

    def get_context_data(self, **kwargs):

        context = super(FileListView, self).get_context_data(**kwargs)

        dirlist = os.listdir(settings.MEDIA_ROOT+'/tablemap/')[0].decode('gbk')
        book = xlrd.open_workbook(settings.MEDIA_ROOT+'/tablemap/'+ dirlist, formatting_info=True)
        sheets = book.sheet_names()[1:]

        nodelist = []
        no = []
        i = 1
        for l in sheets:
            dict_obj = {}
            dict_obj['text'] = l
            dict_obj['id'] = i
            dict_obj['tags'] = ['0']
            nodelist.append(dict_obj)
            no.append(l)
            i += 1

        context['no'] = no
        context['treedata'] = json.dumps(nodelist)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return super(FileListView, self).get(request, *args, **kwargs)

    def post(self,request,*args, **kwargs):
        table_name=request.POST.get('id')
        dirlist = os.listdir(settings.MEDIA_ROOT+'/tablemap/')[0].decode('gbk')
        book = xlrd.open_workbook(settings.MEDIA_ROOT+'/tablemap/'+ dirlist, formatting_info=True)
        sheet = book.sheet_by_index(int(table_name))
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

        table = []
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
                val_dict[str(i)] = val_bgx_dict
                i += 1
            table.append(val_dict)
        return JsonResponse(json.dumps(table),safe=False)

