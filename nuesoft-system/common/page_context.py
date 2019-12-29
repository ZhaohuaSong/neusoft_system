#!/usr/bin/env python
# -*- coding: utf-8 -*-
#返回模板文件需要的数据以及翻页各种信息

from ..sysadmin.models import SysUser
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

#基类
class PageContextBase(object):
    def __init__(self, current_page, page_items):
        '''
        ============================================================================
        function: __init__参数
        note: current_page:当前页码  page_items：每页多少条数据
        note:
        ============================================================================
        '''

        self.page_items     = page_items  #每页多少条数据
        self.current_page   = current_page  #当前页码
        self.page_numbers   = 5  #翻页最多显示多少个页标签
        pass

    #提供唯一接口
    def get_context(self, object_list):
        '''
        ============================================================================
        function: get_context
        note: 返回数据list以及翻页信息  子类需要实现__format_data方法做自己的逻辑

        ============================================================================
        '''
        context = {}
        page_items = self.page_items
        current_page = self.current_page
        paginator = Paginator(object_list, page_items)
        data_nums = paginator._get_count()  # 获取数据条数量
        try:
            contacts = paginator.page(current_page)
        except PageNotAnInteger:  #
            contacts = paginator.page(1)
        except EmptyPage:  # 超出了范围
            contacts = paginator.page(paginator.num_pages)

        self.format_data(contacts.object_list)

        page_range = paginator.page_range  # 页码链表
        firt_page = min(page_range)
        last_page = max(page_range)

        # 显示左右范围内四页内容
        range = self.page_numbers
        start = 1
        end = range
        if current_page - range / 2 > 0:
            if max(page_range) - current_page >= range / 2:  # 取左右各两页内容
                start = (current_page - range / 2) - 1
                end = current_page + range / 2
            else:
                start = max(page_range) - range
                if start < 0: start = 0
                end = max(page_range)
        else:
            start = 0
            end = range

        page_range = page_range[start:end]

        context['max_page'] = last_page#总共多少页
        context['data_nums'] = data_nums  # 总共多少条数据
        context['first_page'] = firt_page #第一页的页码
        context['last_page'] = last_page #最后一页的页码
        context['page_range'] = page_range  # 经过逻辑处理后的页码链表
        context['current_page'] = current_page #当前页码
        context['page_objects'] = contacts #当前页数据


        return context

    #子类根据自己需要实现需求
    def format_data(self, object_list):
        '''
        ============================================================================
        function: format_data
        note: 子类可实现这个方法去修饰数据
        ============================================================================
        '''
        pass



# 映射数据
class PageContext(PageContextBase):
    def __init__(self, current_page, page_items):
        super(PageContext, self).__init__(current_page, page_items)

    # 实现基类的方法
    def format_data(self, object_list):
        i = (self.current_page - 1) * (int)(self.page_items)  # 索引
        for data in object_list:
            i = i + 1
            data.index = i
