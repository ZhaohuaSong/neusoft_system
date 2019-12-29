#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/17 10:15
# @Author  :
# @Site    :
# @File    : forms.py
# @Software: PyCharm

from django import forms
import re
from django.db.models import Q
from models import *

class AutoPingForm(forms.Form):
    ip = forms.CharField(
        label=u"请输入拨测ip",
        required=True,
        error_messages={'required': 'ip不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"请输入ip", 'name': 'phone',
               }
        )
    )

    def clean(self):
        ip=None
        try:
            ip = self.cleaned_data['ip']
        except :
            pass
        if not re.search('\d+\.\d+\.\d+\.\d+', ip):
            raise forms.ValidationError(u"ip格式不正确")

class CreateDeviceDialingForm(forms.Form):
    ip = forms.CharField(
        label='ip',
        # required=False,
        error_messages={'required': 'ip不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"ip", 'name': 'phone',
               }
        )
    )
    def clean(self):
        ip=None
        try:
            ip = self.cleaned_data['ip']
        except :
            pass
        sql = Q()
        sql = sql | Q(ip=ip)
        if 0!=len(DialingIp.objects.filter(sql)):
            self.errors['ip'] = '该ip=[%s]已存在' % ip.encode('utf-8')
            raise forms.ValidationError(u"ip不能为空")

class EditDeviceDialingForm(forms.Form):
    ip = forms.CharField(
        label='ip',
        # required=False,
        error_messages={'required': 'ip不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"ip", 'name': 'phone',
               }
        )
    )

    #设置修改的user
    def set_user(self, user):
        self.user = user

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(EditDeviceDialingForm, self).__init__(*args, **kwargs)
        if user is not None:
            self.fields['ip'].initial = self.user.ip

    def clean(self):
        ip=None
        try:
            ip = self.cleaned_data['ip']
        except :
            pass
        sql = Q()
        sql = sql | Q(ip=ip)
        if 0!=len(DialingIp.objects.filter(sql)):
            self.errors['ip'] = '该ip=[%s]已存在' % ip.encode('utf-8')
            raise forms.ValidationError(u"ip不能为空")
