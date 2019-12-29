#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging
from django.contrib.auth import login, logout
from forms import LoginForm
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from models import SysUser, SysLog, RoleList
from django.db.models import Q
from forms import ForgotForm
from django.core.urlresolvers import reverse
from django.conf import settings
from ..common.page_context import *

_logger = logging.getLogger('loggers')



def login_(request):
    """
    登录
    :param request:
    :return:
    """
    context = {}
    # sys_platform = SysPlatform.objects.get(merchant_code=sysconst.MERCHANT_CODE)
    # context['name'] = sys_platform.name
    # context['logo_path'] = sys_platform.logo_path

    if request.method == 'POST':
        form = LoginForm(request, request.POST)
        forgotForm= ForgotForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()  # 获取用户实例
            if user:
                request.session['user_id'] = user.id
                login(request, user)
                if form.get_auto_login():  # set session
                    request.session.set_expiry(None)
                return HttpResponseRedirect(reverse('zabbixmgr:outtrafficchartshow.list'))
        context['form'] = form
        context['forgotForm'] = forgotForm
    else:
        form = LoginForm()
        forgotForm= ForgotForm()
        context['form'] = form
        context['forgotForm'] = forgotForm

    return render(request, 'login_2.html', context)


def logout_(request):
    """
    注销退出
    :param request:
    :return:
    """
    logout(request)
    return HttpResponseRedirect('/login/')

def main_page(request):
    context={}


    # sys_platform = SysPlatform.objects.get(merchant_code=sysconst.MERCHANT_CODE);
    # context['merchant_code']=sys_platform.merchant_code
    # context['name']=sys_platform.name
    # context['logo_path']=sys_platform.logo_path
    # context['type']=request.GET.get('type','')
    # print context
    return render(request, 'home.html', context)

def globar_setting(request):
    return {'MEDIA_URL': settings.MEDIA_URL}


def syslog_list_search(request):

    page_items = 10  # 页面数据条数
    current_page = request.POST.get('page', 1)  # 默认第一页
    try:
        current_page = int(current_page)
    except:
        current_page = 1

    search_context = request.POST.get('query')
    if search_context is not None and len(search_context) != 0:  #
        object_list = None
        sql = Q(user_name__icontains=search_context) | Q(user_mobile__icontains=search_context) | Q(user_role_name__icontains=search_context) | Q(
            sys_org_name__contains=search_context) | Q(handle_url__contains=search_context) | Q(sys_timestamp__contains=search_context)
        object_list = SysLog.objects.filter(sql)
        context = PageContext(current_page, page_items).get_context(object_list)
        context['search_context'] = search_context
        return render(request, 'sysadmin/syslog.list.html', context)
    else:
        return HttpResponseRedirect(reverse('sysadmin:syslog_list'))
