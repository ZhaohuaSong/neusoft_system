#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from django import forms
from django.db.models import Q
from models import SysUser, RoleList, PermissionList
from django.core.exceptions import ObjectDoesNotExist
from models import SysUser, SysDict, SysOrg
from django.contrib.auth import authenticate
import re
from PIL import Image
from django.forms import ModelForm
from ..cabinetmgr.models import IndustryPark

class LoginForm(forms.Form):
    """
    登录表单
    :param Form:
    :return:
    """
    userid = forms.CharField(
        label=u'用户名:',
        max_length=100,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': u'用户名/邮箱/手机号', 'required': 'required', 'autofocus': ''}
        ),
    )

    pwd = forms.CharField(
        label=u'密码:',
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': u'密码', 'required': 'required'}
        )
    )

    remember_me = forms.BooleanField(
        label=u'记住密码:',
        required=False,
        widget=forms.CheckboxInput(
            attrs={'class': 'ace', }
        ),
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        self.auto_login = None
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        userid = self.cleaned_data.get('userid')
        password = self.cleaned_data.get('pwd')
        remember_me = self.cleaned_data.get('remeber_me')
        auto_login = self.cleaned_data.get('auto_login', None)

        if userid and password:
            # 判断是否邮件登录
            if re.match(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}\b', userid) != None:

                if not SysUser.objects.filter(email=userid).exists():
                    raise forms.ValidationError(u'该账号不存在')
                self.user_cache = authenticate(email=userid, password=password)

            # 判断是否手机登录
            elif re.match(r'1\d{10}', userid) != None:

                if not SysUser.objects.filter(mobile=userid).exists():
                    raise forms.ValidationError(u'该账号不存在')
                self.user_cache = authenticate(mobile=userid, password=password)

            # 用户名登录
            else:

                if not SysUser.objects.filter(username=userid).exists():
                    raise forms.ValidationError(u'该账号不存在')
                self.user_cache = authenticate(username=userid, password=password)

        if self.user_cache is None:
            raise forms.ValidationError(u'用户名、邮箱、手机号或密码错误！')

        elif not self.user_cache.is_active:
            raise forms.ValidationError(u'该帐号已被禁用！')

        if remember_me:
            self.auto_login = True;

        return self.cleaned_data

    def get_user(self):
        """
        获取用户实例
        :return:
        """
        return self.user_cache

    def get_auto_login(self):
        """
        是否勾选了自动登录
        :return:
        """
        return self.auto_login

    def get_user_is_first(self):
        """
        获取用户是否是第一次登录
        :return:
        """
        is_first = False
        if self.user_cache and self.user_cache.type == -1:
            is_first = True
            self.user_cache.type == 0
            self.user_cache.save()
        return is_first
class ForgotForm(forms.Form):
    """
    忘记密码表单
    :param Form:
    :return:
    """
    Email = forms.EmailField(
        label=u'邮箱',
        max_length=100,
        widget=forms.TextInput(
            attrs={'class': 'form-control ', 'placeholder': u'Email', 'required': '', 'autofocus': ''}
        ),
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.Email = None
        super(ForgotForm, self).__init__(*args, **kwargs)

    def clean(self):

        Email = self.cleaned_data.get('Email')

        if Email is None:  # 采用EmailField自带了邮件地址的判断,不需要正则表达式
            raise forms.ValidationError(u'邮箱格式错误！')

        if not SysUser.objects.filter(email=Email).exists():  # 判断邮件地址对应的用户是否存在
            raise forms.ValidationError(u'该账号不存在')

        return self.cleaned_data


class PermissionListForm(forms.Form):
    """
    ===============================================================================
    function：    权限管理表单
    ===============================================================================
    """
    name = forms.CharField(
        label='栏目名称',
        required=True,
        error_messages={'required': '栏目名称不能为空', },
        widget=forms.TextInput(
            attrs={'class': 'col-xs-10 col-sm-5', 'placeholder': u"栏目名称", "id": 'column_name_tag',
                   }

        )
    )
    url = forms.CharField(
        label='栏目名称',
        required=True,
        error_messages={'required': '栏目名称不能为空', },
        widget=forms.TextInput(
            attrs={'class': 'col-xs-10 col-sm-5', 'placeholder': u"栏目名称", "id": 'column_name_tag',
                   }

        )
    )
    type = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={'class': 'ace input-lg', 'name': 'type'}
        ),
    )
    id = forms.CharField(
        label='权限ID',
        required=True,
        error_messages={'required': '权限ID选择不能为空', },
        widget=forms.TextInput(
            attrs={'class': 'col-xs-10 col-sm-5 ', 'placeholder': u"权限ID选择不能为空", "id": 'auto_tag',
                   }

        )

    )

class EditPermissionListForm(forms.Form):
    """
    ===============================================================================
    function：    权限管理表单
    ===============================================================================
    """

    name = forms.CharField(
        label='栏目名称',
        required=True,
        error_messages={'required': '栏目名称不能为空', },
        widget=forms.TextInput(
            attrs={'class': 'col-xs-10 col-sm-5', 'placeholder': u"栏目名称", "id": 'column_name_tag',
                   }

        )
    )
    url = forms.CharField(
        label='栏目名称',
        required=True,
        error_messages={'required': '栏目名称不能为空', },
        widget=forms.TextInput(
            attrs={'class': 'col-xs-10 col-sm-5', 'placeholder': u"栏目名称", "id": 'column_name_tag',
                   }

        )
    )
    type = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={'class': 'ace input-lg', 'name': 'type'}
        ),
    )
    id = forms.CharField(
        label='权限ID',
        required=True,
        error_messages={'required': '权限ID选择不能为空', },
        widget=forms.TextInput(
            attrs={'class': 'col-xs-10 col-sm-5 ', 'placeholder': u"权限ID选择不能为空", "id": 'auto_tag',
                   }

        )

    )


    def __init__(self, PermissionList=None, login_user_org_id=None, *args, **kwargs):
        # self.iColumn = iColumn
        super(EditPermissionListForm, self).__init__(*args, **kwargs)
        # 下面字段操作都是给表单数据初始化
        self.fields['id'].initial = PermissionList.id
        self.fields['name'].initial = PermissionList.name
        self.fields['type'].initial = PermissionList.type
        self.fields['url'].initial = PermissionList.url

    def setId(self, id):
      EditPermissionListForm.id=id

    def clean(self):
        name=None
        url=None
        try:
            name = self.cleaned_data['name']
            url = self.cleaned_data.get('url')
        except Exception as e:
            pass
        sql = Q()
        sql = sql | Q(name=name)|Q(url=url)
        if url!=None and name!=None and 0!=len(PermissionList.objects.filter(sql).exclude(id=EditPermissionListForm.id)):
                try:
                     if PermissionList.objects.get(name=name)is not None:
                         self.errors['name'] = '该权限名称=[%s]已存在' % name.encode('utf-8')
                     else:
                         self.errors['url'] = 'URL或权限名称=[%s]已存在' % url.encode('utf-8')
                except:
                    self.errors['url'] = '该URL=[%s]已存在' % url.encode('utf-8')

                raise forms.ValidationError(u"权限名称不能为空")

class CreateUserForm(forms.Form):
    """
    ===============================================================================
    function：    管理员增加用户
    ===============================================================================
    """
    sys_org_id = forms.CharField(
        label='父级名称',
        # required=True,
        error_messages={'required': '父级名称不能为空',},
        widget=forms.TextInput(
              attrs={'class': 'col-xs-10 col-sm-5 ', 'placeholder': u"用户名", 'name': 'sys_org_id',"id":'auto_tag', 'value':-2
               }

        )

    )
    username = forms.CharField(
        max_length=20,
        label='用户名',
        # required=True,
        error_messages={'required': '用户名不能为空',},
        widget=forms.TextInput(
              attrs={'class': 'col-xs-10 col-sm-5', 'placeholder': u"登录用户名，长度不超过20字符", 'name': 'username','length': '10',
               }
        )
    )

    email = forms.EmailField(
        label=u'邮箱',
        max_length=100,
        error_messages={'required': '邮箱不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-10 col-sm-5', 'placeholder': u'Email', 'name': 'email',
               }

        )

    )

    phone = forms.CharField(
        label='联系号码',
        # required=False,
        error_messages={'required': '电话不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-10 col-sm-5',  'placeholder': u"手机号码", 'name': 'phone',
               }
        )
    )

    sex = forms.ChoiceField(
        label=u"性别",
        error_messages={'required': '请选择性别，必选项', },
        initial = 1,
        required=False,
        choices=(
            (1, "男性"),
            (0, "女性"),
        ),

        widget=forms.RadioSelect(
            attrs={'class': 'col-xs-10 col-sm-5',
                   'class': 'am-radio-inline ',
                   'placeholder': u"用户的性别",
                    'name': 'sex',
                   }
        )
    )

    pwd1 = forms.CharField(
        label=u'密码',
        error_messages={'required': '密码不能为空',},
        widget=forms.PasswordInput(
              attrs={'class': 'col-xs-10 col-sm-5',  'placeholder': u'密码', 'name': 'pwd1',
               }

        )
    )

    pwd2 = forms.CharField(
        label=u'重复密码',
        error_messages={'required': '重复密码', },
        widget=forms.PasswordInput(
              attrs={'class': 'col-xs-10 col-sm-5',  'placeholder': u'再输入一次密码', 'name': 'pwd2',
               }
        )
    )
    industry = forms.ModelChoiceField(
        label=u'IDC园区',
        queryset=IndustryPark.objects.all(),
        error_messages={'required': '园区不能为空', },
        widget=forms.Select(
              attrs={'class': 'col-xs-10 col-sm-5',  'placeholder': u'请选择园区', 'name': 'pwd2',
               }
        )
    )

    role_id = forms.ModelChoiceField(
        queryset=RoleList.objects.all(),
        label=u"用户角色",
        required=True,

        widget=forms.Select(
            attrs={
                'placeholder': u"用户角色",
            }
        )
    )

    def clean(self):
        username=None
        try:
            username = self.cleaned_data['username']
        except :
            pass
        sql = Q()
        sql = sql | Q(username=username)
        if 0!=len(SysUser.objects.filter(sql)):
            self.errors['username'] = '该用户名=[%s]已存在' % username.encode('utf-8')
            raise forms.ValidationError(u"用户名不能为空")

    def clean_email(self):
        # 验证输入的电子邮件是否合法
        email = self.cleaned_data['email']
        pattern = re.compile(r"^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+(.[a-zA-Z0-9_-])+")
        try:
            SysUser.objects.get(email=email)
        except ObjectDoesNotExist:
            if email:
                if pattern.match(email):  # 如果验证失败的话就会返回none
                    return email
                else:
                    raise forms.ValidationError('请输入正确的邮箱地址！')
            else:
                pass
        raise forms.ValidationError('该邮箱已存在！')

    def clean_phone(self):
        # 验证输入电话号码的合法性
        phone = self.cleaned_data['phone']
        pattern = re.compile(r"^0?(13[0-9]|15[012356789]|17[013678]|18[0-9]|14[57])[0-9]{8}$")  # 设置正则验证
        if phone:
            if pattern.match(phone):  # 如果验证失败的话就会返回none
                if 0 != len(SysUser.objects.filter(mobile=phone)):
                    raise forms.ValidationError('该手机号已经被注册！')
                return phone
            else:
                raise forms.ValidationError('请输入正确的手机或座机号码！')
        else:
            pass

    def clean_pwd2(self):
        # 验证密码的合法性
        pwd1 = self.cleaned_data['pwd1']
        pwd2 = self.cleaned_data['pwd2']
        if pwd1 != pwd2:
            raise forms.ValidationError(u'两次输入密码不一致')
        if pwd2 == pwd1 and len(pwd1) < 6:
            raise forms.ValidationError(u'密码不能小于6位')

        return pwd2

class EditUserForm(forms.Form):
    """
      ===============================================================================
      function：    管理员修改用户
      ===============================================================================
    """

    username = forms.CharField(
        label='用户名',
        max_length=20,
        # required=True,
        error_messages={'required': '用户名不能为空',},
        widget=forms.TextInput(
              attrs={'class': 'col-xs-10 col-sm-5', 'placeholder': u"登录用户名，长度不超过20字符", 'name': 'appl_id',
               }

        )

    )

    email = forms.EmailField(
        label=u'邮箱',
        max_length=100,
        error_messages={'required': '邮箱不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-10 col-sm-5', 'placeholder': u'Email', 'name': 'appl_id',
               }

        )

    )

    phone = forms.CharField(
        label='联系号码',
        # required=False,
        error_messages={'required': '电话不能为空', },
        widget=forms.TextInput(
              attrs={'class': 'col-xs-10 col-sm-5',  'placeholder': u"手机号码", 'name': 'appl_id',
               }

        )


    )

    sex = forms.ChoiceField(
        label=u"性别",
        choices=(
            (1, "男性"),
            (0, "女性"),
        ),

        widget=forms.RadioSelect(
            attrs={'class': 'col-xs-10 col-sm-5',
                   'class': 'am-radio-inline ',
                   'placeholder': u"用户的性别",
                    'name': 'appl_id',
                   }
        )
    )

    role_id = forms.ModelChoiceField(
        queryset=RoleList.objects.all(),
        label=u"用户角色",
        required=True,

        widget=forms.Select(
            attrs={
                'placeholder': u"用户角色",
            }
        )
    )

    #设置修改的user
    def set_user(self, user):
        self.user = user

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(EditUserForm, self).__init__(*args, **kwargs)
        #下面字段操作都是给表单数据初始化
        if user is not None:
            self.fields['username'].initial = user.username
            self.fields['email'].initial = user.email
            self.fields['phone'].initial = user.mobile
            self.fields['role_id'].initial = user.role_id
            self.fields['sex'].initial = user.sex

    def clean_username(self):
        # 验证用户名是否重复
        username = self.cleaned_data['username']
        if username == self.user.username:
            # 判断用户名是否等于初始值,如果是直接不验证
            return username
        else:
            try:
                SysUser.objects.get(username=username)
                raise forms.ValidationError('该用户名已存在！')
            except ObjectDoesNotExist:
                return username


    def clean_email(self):
        # 验证输入的电子邮件是否合法
        email = self.cleaned_data['email']
        if email == self.user.email:
            # 判断email是否等于初始值,如果是直接不验证
            return email
        else:
            try:
                SysUser.objects.get(email=email)
                raise forms.ValidationError('该邮箱已存在！')
            except ObjectDoesNotExist:
                return email


    def clean_phone(self):
        # 验证输入电话号码的合法性
        phone = self.cleaned_data['phone']
        pattern = re.compile(r"^0?(13[0-9]|15[012356789]|17[013678]|18[0-9]|14[57])[0-9]{8}$")  # 设置正则验证
        if phone:
            if pattern.match(phone):  # 如果验证失败的话就会返回none
                return phone
            else:
                raise forms.ValidationError('请输入正确的手机号码！')
        else:
            pass

from django.utils.html import force_text, format_html
#from itertools import chain
class RoleSelectMultiple(forms.SelectMultiple):

    def render_options(self, selected_choices):
        # Normalize to strings.
        selected_choices = set(force_text(v) for v in selected_choices)
        output = []
        for option_value, option_label in self.choices:
            try:
                if 1 == PermissionList.objects.get(id=option_value).type:
                    continue
            except:
                pass
            if isinstance(option_label, (list, tuple)):
                output.append(format_html('<optgroup label="{}">', force_text(option_value)))
                for option in option_label:
                    output.append(self.render_option(selected_choices, *option))
                output.append('</optgroup>')
            else:
                output.append(self.render_option(selected_choices, option_value, option_label))
        return '\n'.join(output)

class RoleListForm(forms.ModelForm):
    """
    ===============================================================================
    function：    角色管理表单
    ===============================================================================
    """

    class Meta:
        model = RoleList
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control','placeholder': u'角色名称'}),
            'permission': RoleSelectMultiple(
                attrs={'class': 'form-control', 'placeholder': u'URL','size': '10', 'multiple': 'multiple'}
            ),

            # 'permission' : forms.CheckboxSelectMultiple(choices=[(x.id,x.name) for x in PermissionList.objects.all()]),
        }
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(RoleListForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = u'名 称'
        self.fields['name'].error_messages = {'required': u'请输入角色名称'}
        self.fields['permission'].label = u'URL'
        self.fields['permission'].required = False



    def clean(self):
        name = self.cleaned_data['name']
        try:#编辑的时候用到
            if self.initial['name'] == name:
                return
        except:
            pass

        if name!=None and 0!=len(RoleList.objects.filter(name=name)):
              self.errors['name'] = '该角色名称已存在'
              raise forms.ValidationError(u"该角色名称已存在")


