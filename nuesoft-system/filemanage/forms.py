#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/1/15
# @Author  :
# @Site    :
# @File    : forms.py
# @Software: PyCharm
# @Function: 表单类

from django import forms
from models import Filename, FilePathName, FileUpload
import os
from django.db.models import Q
import chardet

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

    def clean_filename(self):
        filename = self.cleaned_data['filename']
        if filename:
            if filename != self.fields['filename'].initial:
                if Filename.objects.filter(file_name=filename).count() is not 0:
                    raise forms.ValidationError("0")
                if str(os.path.splitext(str(filename))[1]) != '.xls' and str(os.path.splitext(str(filename))[1]) != '.xlsx':
                    raise forms.ValidationError("2")
        else:
            raise forms.ValidationError("1")
        return filename

class DeleteFileConfigForm(forms.Form):
    """
    文件删除表单
    :param Form:
    :return:
    """
    class Meta:
        model = FileUpload
        fields = ['file_standard_name']

    file_standard_name = forms.ModelChoiceField(label='文件名',
                                      queryset=FileUpload.objects.all().values_list("file_standard_name", flat=True),
                                      to_field_name="file_standard_name",
                                      required=True,
                                      widget=forms.Select(
                                          attrs={
                                              'id': 'form-field-select-1',
                                              'name': 'tmk_flag',
                                              'class': 'select2  form-control',}
                                      ),
                                      )

class CreateIndustryParkSourceForm(forms.Form):
    building = forms.CharField(
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

class EditIndustryParkSourceForm(forms.Form):
    building = forms.CharField(
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
            self.fields['building'].initial = self.user.building
            self.fields['type'].initial = self.user.type
            self.fields['attribute'].initial = self.user.attribute
            self.fields['electric_cap'].initial = self.user.electric_cap
            self.fields['power'].initial = self.user.power
            self.fields['total_box'].initial = self.user.total_box

