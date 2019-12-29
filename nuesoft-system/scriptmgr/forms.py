#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import forms
from models import TestFileParam
import os
import re
import chardet

class CreateParamForm(forms.Form):
    # class Meta:
    #     model = TestFileParam
    #     fields = ['test_file_param']

    file_name = forms.ChoiceField(
        # queryset=TestFileParam.objects.all().values_list("file_name"),
        label=u"文件名",
        required=True,

        widget=forms.Select(
            attrs={'class': 'col-xs-10 col-sm-5',  'placeholder': u"文件名", 'name': 'file_name',
            }
        )
    )

    ip_addr = forms.CharField(
        label='ip地址',
        # required=False,
        error_messages={'required': 'ip地址', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-10 col-sm-5',  'placeholder': u"ip地址", 'name': 'ip_addr',
               }
        )
        )

    param = forms.CharField(
        label='参数',
        # required=False,
        error_messages={'required': '参数', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-10 col-sm-5',  'placeholder': u"参数", 'name': 'param',
               }
        )
        )

    def clean(self):
        ip_addr = self.cleaned_data['ip_addr']
        if self.is_valid_ip(ip_addr) is False:
            raise forms.ValidationError(u"IP地址不合法")


    # 正则匹配IP
    def is_valid_ip(self, ip):
        if re.match(r"^\s*\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\s*$", ip): return True
        return False

    def __init__(self, *args, **kwargs):
        super(CreateParamForm, self).__init__(*args, **kwargs)
        self.fields['file_name'].choices = [('', '----------')] + list(TestFileParam.objects.all().values_list("file_name", "file_name"))


