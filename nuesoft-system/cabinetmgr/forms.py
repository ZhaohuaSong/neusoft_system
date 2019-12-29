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
import os
import public_id
import IPy
from ..sysadmin.models import SysUser
from ipsplit.ipListSplit import Split
import json

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

class CreateThresholdForm(forms.Form):
    threshold = forms.CharField(
        label='阀值',
        # required=False,
        error_messages={'required': '阀值不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"阀值", 'name': 'phone',
               }
        )
    )
    def clean(self):
        ip=None
        try:
            threshold = self.cleaned_data['threshold']
        except :
            pass
        sql = Q()
        sql = sql | Q(threshold=threshold)
        if 0!=len(Threshold.objects.filter(sql)):
            self.errors['threshold'] = '该threshold=[%s]已存在' % threshold.encode('utf-8')
            raise forms.ValidationError(u"ip不能为空")

class EditThresholdForm(forms.Form):
    threshold = forms.CharField(
        label='阀值',
        # required=False,
        error_messages={'required': '阀值不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"阀值", 'name': 'phone',
               }
        )
    )

    #设置修改的user
    def set_user(self, user):
        self.user = user

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(EditThresholdForm, self).__init__(*args, **kwargs)
        if user is not None:
            self.fields['threshold'].initial = self.user.threshold

    def clean(self):
        threshold=None
        try:
            threshold = self.cleaned_data['threshold']
        except :
            pass
        sql = Q()
        sql = sql | Q(threshold=threshold)
        if 0!=len(Threshold.objects.filter(sql)):
            self.errors['threshold'] = '该阀值=[%s]已存在' % threshold.encode('utf-8')
            raise forms.ValidationError(u"阀值不能为空")

class CreateElectricboxForm(forms.Form):
    device_room_ = forms.ModelChoiceField(
        queryset=BuildingRoom.objects.filter(industry_id=1, building_id=1),
        label=u"机房名称",
        required=True,
        widget=forms.Select(
            attrs={
                'class': 'col-xs-12 col-sm-5',  'placeholder': u"机房名称",
            }
        )
    )
    box_name = forms.CharField(
        label='机柜名称',
        # required=False,
        error_messages={'required': '机柜名称', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"机柜名称", 'name': 'phone',
               }
        )
    )
    client_name = forms.CharField(
        label='客户名称',
        required=False,
        error_messages={'required': '客户名称', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"客户名称", 'name': 'phone',
               }
        )
    )
    power_rating = forms.CharField(
        label='额定功率',
        # required=False,
        error_messages={'required': '额定功率', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"额定功率", 'name': 'phone',
               }
        )
    )
    threshold_rating = forms.CharField(
        label='阀值功率',
        # required=False,
        error_messages={'required': '阀值功率', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"阀值功率", 'name': 'phone',
               }
        )
    )
    box_type = forms.ModelChoiceField(
        queryset=SelectBox.objects.filter(Q(id=1) | Q(id=2) | Q(id=3) | Q(id=4)),
        label=u"机柜状态",
        required=True,
        widget=forms.Select(
            attrs={
               'class': 'col-xs-12 col-sm-5',  'placeholder': u"机柜状态",
            }
        )
    )
    # on_state_date = forms.DateTimeField(
    #     label='上架日期',
    #     required=False,
    #     error_messages={'required': '上架日期', },
    #     widget=forms.TextInput(
    #           attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"如：2018-09-10", 'name': 'phone',
    #            }
    #     )
    # )
    # power_on_date = forms.DateTimeField(
    #     label='加电日期',
    #     required=False,
    #     error_messages={'required': '加电日期', },
    #     widget=forms.TextInput(
    #           attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"如：2018-09-10", 'name': 'phone',
    #            }
    #     )
    # )

    def clean(self):
        box_name = self.cleaned_data['box_name']
        building_room = self.cleaned_data['room_name']
        if building_room.volume == 1:
            self.errors['room_name'] = '机房机柜已满，不可继续添加机柜'
            raise forms.ValidationError(u"机柜名不能为空")
        if 0!=len(Electricbox.objects.filter(industry_id=1, building_id=1, box_name=box_name)):
            self.errors['box_name'] = '机柜=[%s]已存在' % box_name.encode('utf-8')
            raise forms.ValidationError(u"机柜名不能为空")



class EditElectricboxForm(forms.Form):
    device_room = forms.ModelChoiceField(
        queryset=BuildingRoom.objects.filter(industry_id=1, building_id=1),
        label=u"机房名称",
        required=True,
        widget=forms.Select(
            attrs={
                'class': 'col-xs-12 col-sm-5',  'placeholder': u"机房名称",
            }
        )
    )
    box_name = forms.CharField(
        label='机柜名称',
        # required=False,
        error_messages={'required': '机柜名称', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"机柜名称", 'name': 'phone',
               }
        )
    )
    client_name = forms.CharField(
        label='客户名称',
        required=False,
        error_messages={'required': '客户名称', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"客户名称", 'name': 'phone',
               }
        )
    )
    power_rating = forms.CharField(
        label='额定功率',
        # required=False,
        error_messages={'required': '额定功率', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"额定功率", 'name': 'phone',
               }
        )
    )
    threshold_rating = forms.CharField(
        label='阀值功率',
        # required=False,
        error_messages={'required': '阀值功率', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"阀值功率", 'name': 'phone',
               }
        )
    )
    box_type = forms.ModelChoiceField(
        queryset=SelectBox.objects.filter(Q(id=1) | Q(id=2) |Q(id=3) | Q(id=4)),
        label=u"机柜状态",
        required=True,
        widget=forms.Select(
            attrs={
               'class': 'col-xs-12 col-sm-5',  'placeholder': u"机柜状态",
            }
        )
    )
    # on_state_date = forms.DateTimeField(
    #     label='上架日期',
    #     required=False,
    #     error_messages={'required': '上架日期', },
    #     widget=forms.TextInput(
    #           attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"如：2018-09-10", 'name': 'phone',
    #            }
    #     )
    # )
    # power_on_date = forms.DateTimeField(
    #     label='加电日期',
    #     required=False,
    #     error_messages={'required': '加电日期', },
    #     widget=forms.TextInput(
    #           attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"如：2018-09-10", 'name': 'phone',
    #            }
    #     )
    # )

    #设置修改的user
    def set_user(self, user):
        self.user = user

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(EditElectricboxForm, self).__init__(*args, **kwargs)
        if user is not None:
            self.fields['device_room'].initial = self.user.device_room
            self.fields['box_name'].initial = self.user.box_name
            self.fields['client_name'].initial = self.user.client_name
            self.fields['power_rating'].initial = self.user.power_rating
            self.fields['threshold_rating'].initial = self.user.threshold_rating
            # self.fields['on_state_date'].initial = self.user.on_state_date
            # self.fields['power_on_date'].initial = self.user.power_on_date
            self.fields['box_type'].initial = self.user.box_type

    # def clean(self):
    #     ip=None
    #     try:
    #         box_name = self.cleaned_data['box_name']
    #     except :
    #         pass
    #     sql = Q()
    #     sql = sql | Q(box_name=box_name)
    #     if 0!=len(Electricbox.objects.filter(sql & Q(industry_id=1) & Q(building_id=1))):
    #         self.errors['box_name'] = '机柜=[%s]已存在' % box_name.encode('utf-8')
    #         raise forms.ValidationError(u"机柜名不能为空")

class UpLoadFileForm(forms.Form):
    """
    文件上传表单
    :param Form:
    :return:
    """

    filename = forms.FileField(label=u'文件上传',
                             required=False,
                             widget=forms.FileInput(
                                 attrs={'class': 'col-xs-10 col-sm-10', 'placeholder': u'文件上传', 'id': 'id_image',
                                        'name': 'image'}))


    def __init__(self, *args, **kwargs):
        super(UpLoadFileForm, self).__init__(*args, **kwargs)

    # def clean_filename(self):
    #     filename = self.cleaned_data['filename']
    #     if filename:
    #         if filename != self.fields['filename'].initial:
    #             if Filename.objects.filter(file_name=filename).count() is not 0:
    #                 raise forms.ValidationError("0")
    #             if str(os.path.splitext(str(filename))[1]) != '.xls' and str(os.path.splitext(str(filename))[1]) != '.xlsx':
    #                 raise forms.ValidationError("2")
    #     else:
    #         raise forms.ValidationError("1")
    #     return filename

class EditIndustryParkSourceForm(forms.Form):
    park = forms.CharField(
        label='机楼',
        # required=False,
        error_messages={'required': '机楼不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"机楼", 'name': 'phone',
               }
        )
    )
    type = forms.CharField(
        label='类型',
        # required=False,
        error_messages={'required': '类型不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"类型", 'name': 'phone',
               }
        )
    )
    attribute = forms.CharField(
        label='属性',
        # required=False,
        error_messages={'required': '属性不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"属性", 'name': 'phone',
               }
        )
    )
    electric_cap = forms.IntegerField(
        label='外电容量（KVA)',
        # required=False,
        error_messages={'required': '外电容量（KVA)不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"外电容量（KVA)", 'name': 'phone',
               }
        )
    )
    power = forms.IntegerField(
        label='使用功率',
        # required=False,
        error_messages={'required': '使用功率不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"使用功率", 'name': 'phone',
               }
        )
    )
    total_box = forms.IntegerField(
        label='总计划建设机架数',
        # required=False,
        error_messages={'required': '总计划建设机架数不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"总计划建设机架数", 'name': 'phone',
               }
        )
    )

        #设置修改的user
    def set_user(self, user):
        self.user = user

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(EditIndustryParkSourceForm, self).__init__(*args, **kwargs)
        if user is not None:
            self.fields['park'].initial = self.user.park
            self.fields['type'].initial = self.user.type
            self.fields['attribute'].initial = self.user.attribute
            self.fields['electric_cap'].initial = self.user.electric_cap
            self.fields['power'].initial = self.user.power
            self.fields['total_box'].initial = self.user.total_box

class CreateIndustryParkSourceForm(forms.Form):
    park = forms.CharField(
        label='机楼',
        # required=False,
        error_messages={'required': '机楼不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"机楼", 'name': 'phone',
               }
        )
    )
    type = forms.CharField(
        label='类型',
        # required=False,
        error_messages={'required': '类型不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"类型", 'name': 'phone',
               }
        )
    )
    attribute = forms.CharField(
        label='属性',
        # required=False,
        error_messages={'required': '属性不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"属性", 'name': 'phone',
               }
        )
    )
    electric_cap = forms.IntegerField(
        label='外电容量（KVA)',
        # required=False,
        error_messages={'required': '外电容量（KVA)不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"外电容量（KVA)", 'name': 'phone',
               }
        )
    )
    power = forms.IntegerField(
        label='使用功率',
        # required=False,
        error_messages={'required': '使用功率不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"使用功率", 'name': 'phone',
               }
        )
    )
    total_box = forms.IntegerField(
        label='总计划建设机架数',
        # required=False,
        error_messages={'required': '总计划建设机架数不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"总计划建设机架数", 'name': 'phone',
               }
        )
    )

class CreateIndustryParkForm(forms.Form):
    park = forms.CharField(
        label='园区名称',
        # required=False,
        error_messages={'required': '园区名称不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"园区名称", 'name': 'phone',
               }
        )
    )
    bandwidth = forms.IntegerField(
        label='园区带宽',
        # required=False,
        error_messages={'required': '园区带宽不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"园区带宽", 'name': 'phone',
               }
        )
    )

    def clean(self):
        park = self.cleaned_data['park']
        if IndustryPark.objects.filter(park=park).exists():
            self.errors['park'] = '园区已存在'
            raise forms.ValidationError('园区已存在')

class EditIndustryParkForm(forms.Form):
    park = forms.CharField(
        label='园区名称',
        # required=False,
        error_messages={'required': '园区名称不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"园区名称", 'name': 'phone',
               }
        )
    )
    bandwidth = forms.IntegerField(
        label='园区带宽',
        # required=False,
        error_messages={'required': '园区带宽不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"园区带宽", 'name': 'phone',
               }
        )
    )
    def set_user(self, user):
        self.user = user

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(EditIndustryParkForm, self).__init__(*args, **kwargs)
        if user is not None:
            self.fields['park'].initial = self.user.park
            self.fields['bandwidth'].initial = self.user.bandwidth

    # def clean(self):
    #     park = self.cleaned_data['park']
    #     if IndustryPark.objects.filter(park=park).exists():
    #         self.errors['park'] = '园区已存在'
    #         raise forms.ValidationError('园区已存在')

class CreateIndustryBuildingForm(forms.Form):
    park = forms.ModelChoiceField(
        queryset=IndustryPark.objects.all(),
        label='园区名称',
        # required=False,
        error_messages={'required': '园区名称不能为空', },
        widget=forms.Select(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"园区名称", 'name': 'phone',
               }
        )
    )
    building = forms.CharField(
        label='机楼名称',
        # required=False,
        error_messages={'required': '机楼名称不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"机楼名称", 'name': 'phone',
               }
        )
    )

    def clean(self):
        park_id = self.cleaned_data['park'].id
        building = self.cleaned_data['building']
        if IDCBuilding.objects.filter(park_id=park_id, building_name=building).exists():
            self.errors['building'] = '机楼已存在'
            raise forms.ValidationError('机楼已存在')

class EditIndustryBuildingForm(forms.Form):
    park = forms.ModelChoiceField(
        queryset=IndustryPark.objects.all(),
        label='园区名称',
        # required=False,
        error_messages={'required': '园区名称不能为空', },
        widget=forms.Select(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"园区名称", 'name': 'phone',
               }
        )
    )
    building = forms.CharField(
        label='机楼名称',
        # required=False,
        error_messages={'required': '机楼名称不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"机楼名称", 'name': 'phone',
               }
        )
    )

    def set_user(self, user):
        self.user = user

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(EditIndustryBuildingForm, self).__init__(*args, **kwargs)
        if user is not None:
            # self.fields['park'].initial = self.user.park
            self.fields['building'].initial = self.user.building_name

    # def clean(self):
    #     park_id = self.cleaned_data['park'].id
    #     building = self.cleaned_data['building']
    #     if IDCBuilding.objects.filter(park_id=park_id, building_name=building).exists():
    #         self.errors['building'] = '机楼已存在'
    #         raise forms.ValidationError('机楼已存在')

class EditDeviceRoomForm(forms.Form):
    check_box_power = forms.CharField(
        label='验收机柜功率',
        # required=False,
        error_messages={'required': '验收机柜功率不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"验收机柜功率", 'name': 'phone',
               }
        )
    )
    design_box_power = forms.CharField(
        label='设计负载功率',
        # required=False,
        error_messages={'required': '设计负载功率不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"设计负载功率", 'name': 'phone',
               }
        )
    )
    sign_box_power = forms.CharField(
        label='签约负载功率',
        # required=False,
        error_messages={'required': '签约负载功率不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"签约负载功率", 'name': 'phone',
               }
        )
    )

        #设置修改的user
    def set_user(self, user):
        self.user = user

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(EditDeviceRoomForm, self).__init__(*args, **kwargs)
        if user is not None:
            self.fields['check_box_power'].initial = self.user.check_box_power
            self.fields['design_box_power'].initial = self.user.design_box_power
            self.fields['sign_box_power'].initial = self.user.sign_box_power

class CreateNetworkDeviceForm(forms.Form):
    on_state_date = forms.DateTimeField(
        label='上架日期',
        # required=False,
        error_messages={'required': '上架日期', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"如：2018-09-10", 'name': 'on_state_date',
               }
        )
    )
    power_on_date = forms.DateTimeField(
        label='加电日期',
        required=False,
        error_messages={'required': '加电日期', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"如：2018-09-10", 'name': 'power_on_date',
               }
        )
    )
    start_u_num = forms.IntegerField(
        label='起始u数',
        # required=False,
        error_messages={'required': '起始u数不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"起始u数", 'name': 'start_u_num',
               }
        )
    )
    end_u_num = forms.IntegerField(
        label='结束u数',
        # required=False,
        error_messages={'required': '结束u数不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"结束u数", 'name': 'end_u_num',
               }
        )
    )
    device_code = forms.CharField(
        label='设备型号',
        # required=False,
        error_messages={'required': '设备型号不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"设备型号", 'name': 'device_code',
               }
        )
    )
    device_type = forms.CharField(
        label='设备类型',
        # required=False,
        error_messages={'required': '设备类型不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"设备类型", 'name': 'device_type',
               }
        )
    )
    device_status = forms.ModelChoiceField(
        queryset=SelectBox.objects.filter(type_id=1),
        label=u"设备状态",
        required=True,

        widget=forms.Select(
            attrs={
                'class': 'col-xs-12 col-sm-5',  'placeholder': u"请选择",
            }
        )
    )
    power_num = forms.ModelChoiceField(
        queryset=SelectBox.objects.filter(type_id=2),
        label=u"设备电源数",
        required=True,

        widget=forms.Select(
            attrs={
                'class': 'col-xs-12 col-sm-5',  'placeholder': u"请选择",
            }
        )
    )
    device_alternating = forms.CharField(
        label='电源交流',
        # required=False,
        error_messages={'required': '电源交流不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"电源交流", 'name': 'device_alternating',
               }
        )
    )
    device_threshold_rt = forms.DecimalField(
        label='设备名牌功率',
        # required=False,
        error_messages={'required': '设备名牌功率不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"设备名牌功率", 'name': 'device_threshold_rt',
               }
        )
    )
    device_num = forms.IntegerField(
        label='设备数量',
        # required=False,
        error_messages={'required': '设备数量不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"设备数量", 'name': 'device_num',
               }
        )
    )

    def clean(self):
        u_na = public_id.rq.user.username
        box_id = public_id.di[u_na]
        try:
            on_sd = self.cleaned_data['on_state_date']
        except:
            self.errors['on_state_date'] = '时间格式不正确'
            raise forms.ValidationError('时间格式不正确')
        try:
            po_dt = self.cleaned_data['power_on_date']
        except:
            self.errors['power_on_date'] = '时间格式不正确'
            raise forms.ValidationError('时间格式不正确')

        if on_sd > po_dt:
            self.errors['power_on_date'] = '加电时间不可小于上架时间'
            raise forms.ValidationError('加电时间不可小于上架时间')

        s_un = self.cleaned_data['start_u_num']
        e_un = self.cleaned_data['end_u_num']

        if s_un > e_un:
            self.errors['start_u_num'] = '起始u数不可大于结束u数'
            raise forms.ValidationError('起始u数不能大于结束u数')

        if NetworkDevice.objects.filter(Q(industry_id=1) & Q(building_id=1) & Q(box_id=box_id) & Q(start_u_num=s_un)).exists():
            self.errors['start_u_num'] = 'u数已经存在，请选择其他u数'
            raise forms.ValidationError('u数已经存在，请选择其他u数')

        if NetworkDevice.objects.filter(Q(industry_id=1) & Q(building_id=1) & Q(box_id=box_id) & Q(end_u_num=e_un)).exists():
            self.errors['end_u_num'] = 'u数已经存在，请选择其他u数'
            raise forms.ValidationError('u数已经存在，请选择其他u数')

class EditNetworkDeviceForm(forms.Form):
    on_state_date = forms.DateTimeField(
        label='上架日期',
        # required=False,
        error_messages={'required': '上架日期', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"如：2018-09-10", 'name': 'on_state_date',
               }
        )
    )
    power_on_date = forms.DateTimeField(
        label='加电日期',
        required=False,
        error_messages={'required': '加电日期', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"如：2018-09-10", 'name': 'power_on_date',
               }
        )
    )
    start_u_num = forms.IntegerField(
        label='起始u数',
        # required=False,
        error_messages={'required': '起始u数不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"起始u数", 'name': 'start_u_num',
               }
        )
    )
    end_u_num = forms.IntegerField(
        label='结束u数',
        # required=False,
        error_messages={'required': '结束u数不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"结束u数", 'name': 'end_u_num',
               }
        )
    )
    device_code = forms.CharField(
        label='设备型号',
        # required=False,
        error_messages={'required': '设备型号不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"设备型号", 'name': 'device_code',
               }
        )
    )
    device_type = forms.CharField(
        label='设备类型',
        # required=False,
        error_messages={'required': '设备类型不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"设备类型", 'name': 'device_type',
               }
        )
    )
    device_status = forms.ModelChoiceField(
        queryset=SelectBox.objects.filter(type_id=1),
        label=u"设备状态",
        required=True,

        widget=forms.Select(
            attrs={
                'class': 'col-xs-12 col-sm-5',  'placeholder': u"请选择",
            }
        )
    )
    power_num = forms.ModelChoiceField(
        queryset=SelectBox.objects.filter(type_id=2),
        label=u"设备电源数",
        required=True,

        widget=forms.Select(
            attrs={
                'class': 'col-xs-12 col-sm-5',  'placeholder': u"请选择",
            }
        )
    )
    device_alternating = forms.CharField(
        label='电源交流',
        # required=False,
        error_messages={'required': '电源交流不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"电源交流", 'name': 'device_alternating',
               }
        )
    )
    device_threshold_rt = forms.DecimalField(
        label='设备名牌功率',
        # required=False,
        error_messages={'required': '设备名牌功率不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"设备名牌功率", 'name': 'device_threshold_rt',
               }
        )
    )
    device_num = forms.IntegerField(
        label='设备数量',
        # required=False,
        error_messages={'required': '设备数量不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"设备数量", 'name': 'device_num',
               }
        )
    )

            #设置修改的user
    def set_user(self, user):
        self.user = user

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(EditNetworkDeviceForm, self).__init__(*args, **kwargs)
        if user is not None:
            self.fields['on_state_date'].initial = self.user.on_state_date
            self.fields['power_on_date'].initial = self.user.power_on_date
            # self.fields['down_power_date'].initial = self.user.down_power_date
            self.fields['device_num'].initial = self.user.device_num
            self.fields['start_u_num'].initial = self.user.start_u_num
            self.fields['end_u_num'].initial = self.user.end_u_num
            self.fields['device_code'].initial = self.user.device_code
            self.fields['device_type'].initial = self.user.device_type
            self.fields['device_status'].initial = self.user.device_status
            self.fields['power_num'].initial = self.user.power_num
            self.fields['device_alternating'].initial = self.user.device_alternating
            self.fields['device_threshold_rt'].initial = self.user.device_threshold_rt

    def clean(self):
        u_na = public_id.rq.user.username
        box_id = public_id.di[u_na]
        try:
            on_sd = self.cleaned_data['on_state_date']
        except:
            self.errors['on_state_date'] = '时间格式不正确'
            raise forms.ValidationError('时间格式不正确')
        try:
            po_dt = self.cleaned_data['power_on_date']
        except:
            self.errors['power_on_date'] = '时间格式不正确'
            raise forms.ValidationError('时间格式不正确')
        if on_sd > po_dt:
            self.errors['power_on_date'] = '加电时间不可小于上架时间'
            raise forms.ValidationError('加电时间不可小于上架时间')
        nd_ = NetworkDeviceWorkorder.objects.get(id=box_id)
        box_id = nd_.box_id
        min_on_time = min(list(NetworkDevice.objects.filter(industry_id=1, building_id=1, box_id=box_id).values_list('on_state_date', flat=True)))
        min_pd_time = min(list(NetworkDevice.objects.filter(industry_id=1, building_id=1,box_id=box_id).values_list('power_on_date', flat=True)))
        el_os_date = Electricbox.objects.get(id=box_id).on_state_date
        el_po_date = Electricbox.objects.get(id=box_id).power_on_date
        if on_sd < min_on_time and on_sd < el_os_date: #上架日期比最早上架日期小可修改
            Electricbox.objects.filter(id=box_id).update(on_state_date=on_sd)
        # else:
        #     self.errors['on_state_date'] = '不可修改上架时间'
        #     raise forms.ValidationError('不可修改上架时间')
        if po_dt <= min_pd_time and po_dt <= el_po_date: #加电日期比最早加电日期小可修改
            Electricbox.objects.filter(id=box_id).update(power_on_date=on_sd)
        # else:
        #     self.errors['power_on_date'] = '不可修改加电时间'
        #     raise forms.ValidationError('不可修改加电时间')

        s_un = self.cleaned_data['start_u_num']
        e_un = self.cleaned_data['end_u_num']
        if s_un > e_un:
            self.errors['start_u_num'] = '起始u数不可大于结束u数'
            raise forms.ValidationError('起始u数不能大于结束u数')

        # if NetworkDevice.objects.filter(Q(industry_id=1) & Q(building_id=1) & Q(box_id=box_id) & Q(start_u_num=s_un)).exists():
        #     self.errors['start_u_num'] = 'u数已经存在，请选择其他u数'
        #     raise forms.ValidationError('u数已经存在，请选择其他u数')
        #
        # if NetworkDevice.objects.filter(Q(industry_id=1) & Q(building_id=1) & Q(box_id=box_id) & Q(end_u_num=e_un)).exists():
        #     self.errors['end_u_num'] = 'u数已经存在，请选择其他u数'
        #     raise forms.ValidationError('u数已经存在，请选择其他u数')

class CreateIpDistributeForm(forms.Form):

    ip = forms.CharField(
        label='ip',
        # required=False,
        error_messages={'required': 'ip不能为空', },
        widget=forms.Textarea(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"ip格式如：183.240.112.192/29，183.240.112.200/29", 'name': 'ip',
               }
        )
    )
    operate_id = forms.ModelChoiceField(
        queryset=SelectBox.objects.filter(type_id=3),
        label='ip分配',
        # required=False,
        widget=forms.Select(
            attrs={
                'class': 'col-xs-12 col-sm-5',  'placeholder': u"请选择",
            }
        )
    )

    def clean(self):
        ip_bord = self.cleaned_data['ip']
        ip_list = ip_bord.split(',')
        for ip in ip_list:
            if not re.search('\d+\.\d+\.\d+\.\d+\/\d+', ip):
                self.errors['ip'] = 'ip格式错误'
                raise forms.ValidationError('ip格式错误')
            try:
                IPy.IP(ip).len()
            except:
                self.errors['ip'] = 'ip格式错误'
                raise forms.ValidationError('ip格式错误')

        operate_id = self.cleaned_data['operate_id']
        if operate_id.box_type == '添加ip':
            for ip in ip_list:
                ip = re.search('(\d+\.\d+\.\d+)', ip).groups()[0]
                if not IpLibrary.objects.filter(industry_id=1, all_ip__contains=ip).exists():
                    self.errors['ip'] = 'ip不属于管辖范围'
                    raise forms.ValidationError('ip不属于管辖范围')
            for ip in ip_list:
                if IpAddress.objects.filter(industry_id=1, ip_addr=ip).exists():
                    self.errors['ip'] = 'ip:%s 已存在' %ip
                    raise forms.ValidationError('ip已存在')

def get_industry_id(request):
    username = request.user.username
    industry_id = SysUser.objects.get(username=username).industry_id
    return ElectricboxClient.objects.filter(industry_id=industry_id)

class IDCWorkorderPlatformForm(forms.Form):
    workorder_name = forms.CharField(
        label='工单号',
        # required=False,
        error_messages={'required': '工单号不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"工单号", 'name': 'workorder_name',
               }
        )
    )
    client_name = forms.ModelChoiceField(
        queryset=ElectricboxClient.objects.all(),
        label='客户名称',
        # required=False,
        widget=forms.Select(
            attrs={
                'class': 'col-xs-12 col-sm-5',  'placeholder': u"请选择",
            }
        )
    )

    operate_ip = forms.ModelChoiceField(
        queryset=SelectBox.objects.filter(type_id=4),
        label='ip分配',
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'col-xs-12 col-sm-5',  'placeholder': u"请选择",
            }
        )
    )
    operate_elbox = forms.ModelChoiceField(
        queryset=SelectBox.objects.filter(type_id=5),
        label='机柜分配',
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'col-xs-12 col-sm-5',  'placeholder': u"请选择",
            }
        )
    )
    operate_device = forms.ModelChoiceField(
        queryset=SelectBox.objects.filter(type_id=6),
        label='设备分配',
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'col-xs-12 col-sm-5',  'placeholder': u"请选择",
            }
        )
    )
    operate_interface = forms.ModelChoiceField(
        queryset=SelectBox.objects.filter(type_id=7),
        label='端口分配',
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'col-xs-12 col-sm-5',  'placeholder': u"请选择",
            }
        )
    )
    operate_record = forms.CharField(
        label='工单明细',
        # required=False,
        error_messages={'required': '工单明细不能为空', },
        widget=forms.Textarea(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"工单明细", 'name': 'workorder_name',
               }
        )
    )

    def __init__(self, *args, **kwargs):
        super(IDCWorkorderPlatformForm, self).__init__(*args, **kwargs)

    def clean(self):
        workorder_name = self.cleaned_data['workorder_name']

        if IDCWorkorderPlatform.objects.filter(workorder_name=workorder_name).exists():
            self.errors['workorder_name'] = '工单号已存在'
            raise forms.ValidationError('工单号已存在')
        operate_ip = self.cleaned_data['operate_ip']
        operate_elbox = self.cleaned_data['operate_elbox']
        operate_device = self.cleaned_data['operate_device']
        operate_interface = self.cleaned_data['operate_interface']
        if not operate_ip and not operate_elbox and not operate_device and not operate_interface:
            self.errors['operate_interface'] = '请选择其中一项操作内容'
            raise forms.ValidationError('请选择其中一项操作内容')

class CreateOrgCheckForm(forms.Form):

    result = forms.ChoiceField(
        label=u"审核结果",
        required=True,
        error_messages={'required': '请选择审核结果，必选项', },
        choices=(
            (1, "通过"),
            (0, "不通过"),

        ),
        widget=forms.RadioSelect(
            attrs={
                'class': 'col-xs-20 col-sm-20',
                'class': 'am-radio-inline',
                'placeholder': u"审核结果",
                'name': 'result',
            }
        )
    )
    content = forms.CharField(
        label=u'审核备注',
        required=False,
        initial=None,
        widget=forms.Textarea(
            attrs={
                'id': 'id_result',
                'class': 'form-control js-pattern-key',
                'style': 'border:1px solid ;border-color:#D5D5D5; width:100%;height:2% ;padding:1%  ',
                'data-validation-message': "请输入审核内容",
                'placeholder': u"审核不通过，必须写明原因",
            }
        )
    )

    workorder_id = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'name': 'workorder_id', 'class': 'col-xs-12',
               }
    ), )

    def __init__(self, *args, **kwargs):
        super(CreateOrgCheckForm, self).__init__(*args, **kwargs)

    def clean(self):
        result = self.cleaned_data['result']
        content = self.cleaned_data['content']
        if int(result) == 0 and str(content) == '':
            self.errors['content'] = '请填写原因'
            raise forms.ValidationError('请填写原因')

class CreateIDCClientForm(forms.Form):
    client_name = forms.CharField(
        label=u"工单客户名称",
        required=True,
        error_messages={'required': '名称不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"工单客户名称", 'name': 'phone',
               }
        )
    )

    def get_industry_id(self, industry_id):
        self.industry_id = industry_id

    def clean(self):
        client_name=None
        try:
            client_name = self.cleaned_data['client_name']
        except :
            pass
        if ElectricboxClient.objects.filter(client_name=client_name, industry_id=self.industry_id).exists():
            self.errors['client_name'] = '该客户=[%s]已存在' % client_name.encode('utf-8')
            raise forms.ValidationError(u"客户不能为空")

class EditIDCClientForm(forms.Form):
    client_name = forms.CharField(
        label=u"工单客户名称",
        required=True,
        error_messages={'required': '名称不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"工单客户名称", 'name': 'phone',
               }
        )
    )
    def set_user(self, user):
        self.user = user

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(EditIDCClientForm, self).__init__(*args, **kwargs)
        if user is not None:
            self.fields['client_name'].initial = self.user.client_name

    def get_industry_id(self, industry_id):
        self.industry_id = industry_id

    def clean(self):
        ip=None
        try:
            client_name = self.cleaned_data['client_name']
        except :
            pass
        if ElectricboxClient.objects.filter(client_name=client_name, industry_id=self.industry_id).exists():
            self.errors['box_name'] = '客户=[%s]已存在' % client_name.encode('utf-8')
            raise forms.ValidationError(u"客户名不能为空")

class CreateIPmgrForm(forms.Form):
    industry_ip = forms.CharField(
        label=u"园区ip",
        required=True,
        error_messages={'required': '园区ip不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"园区ip", 'name': 'phone',
               }
        )
    )

    handle = forms.ChoiceField(
        label=u"操作",
        error_messages={'required': '请选择类型，必选项', },
        initial = 1,
        required=False,
        choices=(
            (1, "添加"),
            (0, "删除"),
        ),

        widget=forms.RadioSelect(
            attrs={'class': 'col-xs-10 col-sm-5',
                   'class': 'am-radio-inline ',
                   'placeholder': u"操作类型",
                    'name': 'sex',
                   }
        )
    )

    def get_industry_id(self, industry_id):
        self.industry_id = industry_id

    def clean(self):
        industry_ip = self.cleaned_data['industry_ip']
        handle = self.cleaned_data['handle']
        if not re.match('\d+\.\d+\.\d+\.\d+', industry_ip) and not re.match('\d+\.\d+\.\d+\.\d+\-\d+\.\d+\.\d+\.\d+', industry_ip):
            self.errors['industry_ip'] = 'ip格式不正确'
            raise forms.ValidationError(u"ip格式不正确")

        instance = Split([industry_ip]) #must be list
        upload_ip_list = instance.getAllIpList()
        ip_library = json.loads(IpLibrary.objects.get(industry_id=self.industry_id).all_ip)
        local_ip = Split(ip_library)
        local_ip_list = local_ip.getAllIpList()
        if int(handle) == 1 and IpLibrary.objects.filter(industry_id=self.industry_id).exists():
            ip_set = set(upload_ip_list) & set(local_ip_list)
            if ip_set:
                self.errors['industry_ip'] = 'ip已存在：%s'% ip_set
                raise forms.ValidationError(u"ip已存在")
        if int(handle) == 0 and IpLibrary.objects.filter(industry_id=self.industry_id).exists():
            for ip in upload_ip_list:
                if ip not in local_ip_list:
                    self.errors['industry_ip'] = 'ip不已存在;%s' % upload_ip_list
                    raise forms.ValidationError(u"ip不已存在")
        elif int(handle) == 0 and not IpLibrary.objects.filter(industry_id=self.industry_id).exists():
            self.errors['industry_ip'] = 'ip不已存在'
            raise forms.ValidationError(u"ip不已存在")


class CreateIpInsertModeMSGForm(forms.Form):
    uit_name = forms.CharField(
        label=u"单位名称",
        required=True,
        error_messages={'required': '名称不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"单位名称", 'name': 'phone',
               }
        )
    )
    unit_type = forms.CharField(
        label=u"单位分类",
        required=True,
        error_messages={'required': '单位分类不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"单位分类", 'name': 'phone',
               }
        )
    )
    bussiness_license_num = forms.CharField(
        label=u"经营许可证编号",
        required=True,
        error_messages={'required': '经营许可证编号不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"经营许可证编号", 'name': 'phone',
               }
        )
    )
    unit_property = forms.CharField(
        label=u"单位性质",
        required=True,
        error_messages={'required': '单位性质不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"单位性质", 'name': 'phone',
               }
        )
    )
    provinces = forms.CharField(
        label=u"所属省份",
        required=True,
        error_messages={'required': '所属省份不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"所属省份", 'name': 'phone',
               }
        )
    )
    city = forms.CharField(
        label=u"所属地市",
        required=True,
        error_messages={'required': '所属地市不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"所属地市", 'name': 'phone',
               }
        )
    )
    county = forms.CharField(
        label=u"所属区县",
        required=True,
        error_messages={'required': '所属区县不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"所属区县", 'name': 'phone',
               }
        )
    )
    administrative_level = forms.CharField(
        label=u"单位行政级别",
        required=True,
        error_messages={'required': '单位行政级别不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"单位行政级别", 'name': 'phone',
               }
        )
    )
    profession = forms.CharField(
        label=u"行业分类",
        required=True,
        error_messages={'required': '行业分类不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"行业分类", 'name': 'phone',
               }
        )
    )
    address = forms.CharField(
        label=u"详细地址",
        required=True,
        error_messages={'required': '详细地址不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"详细地址", 'name': 'phone',
               }
        )
    )
    customer_name = forms.CharField(
        label=u"客户联系人",
        required=True,
        error_messages={'required': '客户联系人不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"客户联系人", 'name': 'phone',
               }
        )
    )
    customer_phone = forms.CharField(
        label=u"客户联系电话",
        required=True,
        error_messages={'required': '客户联系电话不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"客户联系电话", 'name': 'phone',
               }
        )
    )
    customer_email = forms.CharField(
        label=u"客户联系邮箱",
        required=True,
        error_messages={'required': '客户联系邮箱不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"客户联系邮箱", 'name': 'phone',
               }
        )
    )
    physical_gateway = forms.CharField(
        label=u"网关物理位置",
        required=True,
        error_messages={'required': '网关物理位置不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"网关物理位置", 'name': 'phone',
               }
        )
    )
    usage_mode = forms.CharField(
        label=u"使用方式",
        required=True,
        error_messages={'required': '使用方式不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"使用方式", 'name': 'phone',
               }
        )
    )
    use_time = forms.CharField(
        label=u"分配使用时间",
        required=True,
        error_messages={'required': '分配使用时间不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"分配使用时间", 'name': 'phone',
               }
        )
    )
    gateway_ip_addr = forms.CharField(
        label=u"网关ip地址",
        required=True,
        error_messages={'required': '网关ip地址不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"网关ip地址", 'name': 'phone',
               }
        )
    )
    bussiness_type = forms.CharField(
        label=u"业务类型",
        required=True,
        error_messages={'required': '业务类型不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"业务类型", 'name': 'phone',
               }
        )
    )
    usage_status = forms.CharField(
        label=u"使用状态",
        required=True,
        error_messages={'required': '使用状态不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"使用状态", 'name': 'phone',
               }
        )
    )
    supervisor_status = forms.CharField(
        label=u"管理状态",
        required=True,
        error_messages={'required': '管理状态不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"管理状态", 'name': 'phone',
               }
        )
    )
    machine_room = forms.CharField(
        label=u"机房",
        required=True,
        error_messages={'required': '机房不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"机房", 'name': 'phone',
               }
        )
    )
    device_name = forms.CharField(
        label=u"设备名称",
        required=True,
        error_messages={'required': '设备名称不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"设备名称", 'name': 'phone',
               }
        )
    )
    loopbak_addr = forms.CharField(
        label=u"loopbak地址",
        required=True,
        error_messages={'required': 'loopbak地址不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"loopbak地址", 'name': 'phone',
               }
        )
    )
    access_port_msg = forms.CharField(
        label=u"接入端口名称",
        required=True,
        error_messages={'required': '接入端口名称不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"接入端口名称", 'name': 'phone',
               }
        )
    )
    in_charge_department = forms.CharField(
        label=u"移动负责部门",
        required=True,
        error_messages={'required': '移动负责部门不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"移动负责部门", 'name': 'phone',
               }
        )
    )
    in_charge_person = forms.CharField(
        label=u"移动负责人",
        required=True,
        error_messages={'required': '移动负责人不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"移动负责人", 'name': 'phone',
               }
        )
    )
    in_charge_phone = forms.CharField(
        label=u"移动负责人电话",
        required=True,
        error_messages={'required': '移动负责人电话不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"移动负责人电话", 'name': 'phone',
               }
        )
    )
    in_charge_email = forms.CharField(
        label=u"移动负责人邮箱",
        required=True,
        error_messages={'required': '移动负责人邮箱不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"移动负责人邮箱", 'name': 'phone',
               }
        )
    )
    remark = forms.CharField(
        label=u"移动负责人邮箱",
        required=True,
        error_messages={'required': '移动负责人邮箱不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"移动负责人邮箱", 'name': 'phone',
               }
        )
    )
    subnet_mask = forms.CharField(
        label=u"移动负责人邮箱",
        required=True,
        error_messages={'required': '移动负责人邮箱不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"移动负责人邮箱", 'name': 'phone',
               }
        )
    )
    in_charge_email = forms.CharField(
        label=u"移动负责人邮箱",
        required=True,
        error_messages={'required': '移动负责人邮箱不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-12 col-sm-5',  'placeholder': u"移动负责人邮箱", 'name': 'phone',
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
        if 0!=len(ElectricboxClient.objects.filter(sql)):
            self.errors['client_name'] = '该客户=[%s]已存在' % client_name.encode('utf-8')
            raise forms.ValidationError(u"客户不能为空")
