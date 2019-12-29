#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import forms
from django.db.models import Q
from models import *
import os
import re
import chardet

class DiffChartForm(forms.Form):
    """
    ===============================================================================
    function：    管理员增加用户
    ===============================================================================
    """
    role_id = forms.ChoiceField(label='时间选择',
          required=True,
          widget=forms.Select(
              attrs={
                  'id': 'form-field-select-1',
                  'name': 'role_id',
                  'class': 'select2  form-control',
              }
          ),
          )

    def __init__(self, *args, **kwargs):
        super(DiffChartForm, self).__init__(*args, **kwargs)
        #初始化报文发送触发类型
        # choices = [('', '----------')] + list(TriggerType.objects.all().values_list("trigger_id", "trigger_name"))
        # self.fields['app_triggertype'].choices = choices
        self.fields['role_id'].choices = ((0, u'1小时'), (1, u'2小时'),(1, u'1天'))

class CreateNetworkInterfaceGroupForm(forms.Form):
    name = forms.CharField(
        label='端口组名',
        # required=False,
        error_messages={'required': '组名不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"端口组名", 'name': 'phone',
               }
        )
    )
    def clean(self):
        name=None
        try:
            name = self.cleaned_data['name']
        except :
            pass
        sql = Q()
        sql = sql | Q(group_name=name)
        # if 0!=len(NetworkInterfaceGroup.objects.using('zabbixdb').filter(sql)):
        if 0!=len(NetworkInterfaceGroup.objects.filter(sql)):
            self.errors['name'] = '该用组名=[%s]已存在' % name.encode('utf-8')
            raise forms.ValidationError(u"组名不能为空")

class EditNetworkInterfaceGroupForm(forms.Form):
    name = forms.CharField(
        label='端口组名',
        # required=False,
        error_messages={'required': '组名不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"端口组名", 'name': 'phone',
               }
        )
    )

    #设置修改的user
    def set_user(self, user):
        self.user = user

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(EditNetworkInterfaceGroupForm, self).__init__(*args, **kwargs)
        if user is not None:
            self.fields['name'].initial = self.user.group_name

    def clean(self):
        name=None
        try:
            name = self.cleaned_data['name']
        except :
            pass
        sql = Q()
        sql = sql | Q(group_name=name)
        if 0!=len(NetworkInterfaceGroup.objects.filter(sql)):
            self.errors['name'] = '该用组名=[%s]已存在' % name.encode('utf-8')
            raise forms.ValidationError(u"组名不能为空")

class CreateNetworkInterfaceForm(forms.Form):

    name = forms.ModelChoiceField(
        queryset=AllNetworkInterface.objects.all(),
        label=u"主机端口",
        required=True,
        error_messages={'required': '端口已存在该组',},

        widget=forms.Select(
            attrs={
                'placeholder': u"主机端口",
            }
        )
    )

    group_name = forms.ModelChoiceField(
        queryset=NetworkInterfaceGroup.objects.all(),
        label=u"组名",
        required=True,

        widget=forms.Select(
            attrs={
                'placeholder': u"请选择",
            }
        )
    )

    def clean(self):
        all_network_interface_name = self.cleaned_data['name'].name
        type = self.cleaned_data['group_name'].id

        try:
            NetworkInterface.objects.get(Q(name=all_network_interface_name) & Q(type=type))
            self.errors['name'] = '该用户名=[%s]已存在该组' % self.cleaned_data['name'].name.encode('utf-8')
            raise forms.ValidationError(u"用户名不能为空")
        except:
            pass

class CreateClientInterfaceMgrForm(forms.Form):
    client_name = forms.CharField(
        label=u"流量分析端口组名",
        required=True,
        error_messages={'required': '组名不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"流量分析端口组名", 'name': 'phone',
               }
        )
    )
    def clean(self):
        client_name=None
        try:
            client_name = self.cleaned_data['client_name']
        except :
            pass
        sql = Q()
        sql = sql | Q(client_name=client_name)
        if 0!=len(ClientGroup.objects.filter(sql)):
            self.errors['client_name'] = '该用组名=[%s]已存在' % client_name.encode('utf-8')
            raise forms.ValidationError(u"组名不能为空")

class CreateGroupclientPortForm(forms.Form):
    port_name = forms.CharField(
        label=u"端口",
        required=True,
        error_messages={'required': '端口不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"端口", 'name': 'phone',
               }
        )
    )
    ip = forms.CharField(
        label=u"ip",
        required=True,
        error_messages={'required': 'ip', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"ip", 'name': 'phone',
               }
        )
    )
    bandwidth = forms.CharField(
        label=u"带宽",
        required=True,
        error_messages={'required': '带宽', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"带宽", 'name': 'phone',
               }
        )
    )
    client_name = forms.ModelChoiceField(
        queryset=ClientGroup.objects.all(),
        label=u"用户名",
        required=True,

        widget=forms.Select(
            attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"请选择", 'name': 'phone',
               }
        )
    )
    def clean(self):
        ip = self.cleaned_data['ip']
        if not re.match('\d+\.\d+\.\d+\.\d+', ip):
            self.errors['ip'] = 'ip格式错误'
            raise forms.ValidationError('ip格式错误')
        if not Hosts.objects.using('zabbixdb').get(host=ip).hostid:
            self.errors['ip'] = 'ip不存在'
            raise forms.ValidationError('ip不存在')
        host_id = Hosts.objects.using('zabbixdb').get(host=ip).hostid
        port_name = self.cleaned_data['port_name']
        if SheetsInterface.objects.filter(port_name=port_name).exists():
            self.errors['port_name'] = '端口已分配'
            raise forms.ValidationError('端口已分配')
        if not  Items.objects.using('zabbixdb').filter(Q(hostid=host_id)\
                                                          & Q(key_field__contains='net.if.in[ifHCInOctets')\
                                                          & Q(name__contains='Interface %s'% port_name)\
                                                          & Q(flags=4)):
            self.errors['port_name'] = '端口不存在'
            raise forms.ValidationError('端口不存在')

class EditClientGroupPortForm(forms.Form):
    port_name = forms.CharField(
        label=u"端口",
        required=True,
        error_messages={'required': '端口不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"端口", 'name': 'phone',
               }
        )
    )
    ip = forms.CharField(
        label=u"ip",
        required=True,
        error_messages={'required': 'ip', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"ip", 'name': 'phone',
               }
        )
    )
    bandwidth = forms.CharField(
        label=u"带宽",
        required=True,
        error_messages={'required': '带宽', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"带宽", 'name': 'phone',
               }
        )
    )
    client_name = forms.ModelChoiceField(
        queryset=ClientGroup.objects.all(),
        label=u"用户名",
        required=True,

        widget=forms.Select(
            attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"请选择", 'name': 'phone',
               }
        )
    )

    def set_user(self, user):
        self.user = user

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(EditClientGroupPortForm, self).__init__(*args, **kwargs)
        if user is not None:
            self.fields['port_name'].initial = self.user.port_name
            self.fields['ip'].initial = self.user.ip
            self.fields['bandwidth'].initial = self.user.bandwidth
            # self.fields['client_name'].initial = self.user.client_name

    def clean(self):
        ip = self.cleaned_data['ip']
        if not re.match('\d+\.\d+\.\d+\.\d+', ip):
            self.errors['ip'] = 'ip格式错误'
            raise forms.ValidationError('ip格式错误')
        if not Hosts.objects.using('zabbixdb').get(host=ip).hostid:
            self.errors['ip'] = 'ip不存在'
            raise forms.ValidationError('ip不存在')
        host_id = Hosts.objects.using('zabbixdb').get(host=ip).hostid
        port_name = self.cleaned_data['port_name']
        if SheetsInterface.objects.filter(port_name=port_name).exists():
            self.errors['port_name'] = '端口已分配'
            raise forms.ValidationError('端口已分配')
        if not  Items.objects.using('zabbixdb').filter(Q(hostid=host_id)\
                                                          & Q(key_field__contains='net.if.in[ifHCInOctets')\
                                                          & Q(name__contains='Interface %s'% port_name)\
                                                          & Q(flags=4)):
            self.errors['port_name'] = '端口不存在'
            raise forms.ValidationError('端口不存在')

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
