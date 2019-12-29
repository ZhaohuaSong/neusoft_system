# -*- coding: utf-8 -*-



from django.views.generic import TemplateView
from ..common.datatables.views import BaseDatatableView
from django.db.models import Q
from django.http import JsonResponse
from ..vanilla import CreateView, UpdateView
import json
from models import SysUser, SysOrg
from forms import CreateUserForm, EditUserForm
import random
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from ..zabbixmgr.constant import get_industry_park

import datetime, hashlib
from ..zabbixmgr.constant import get_industry_park
import re

class ListUser(TemplateView):
    template_name = 'sysadmin/user.list.html'

    def get(self, request, *args, **kwargs):
        us = request.user.username
        industry_park =get_industry_park(us)
        url = self.request.get_full_path()
        industry_id = int(re.findall('(\d+)$', url)[0])
        context = self.get_context_data(**kwargs)
        context['industry_park'] = industry_park
        context['industry_id'] = industry_id
        return self.render_to_response(context)

class OrgTreeData:
    # 获取机构json数据
    def get_org_data(self, org_id):
        org_id = int(org_id)
        if -2 == org_id:#获取一级机构
            org_list = SysOrg.objects.filter(parent_id=0)
            json_data_list_org = []
            select_org_id = -3#处于选中状态的机构ID
            l_org_list = []#同一级别的机构信息
            l_org_list_info = []#同一级别的机构信息+选中状态的机构ID
            for info in org_list:
                l = []#机构信息，id和name
                l.append(info.id)
                l.append(info.org_name)
                l_org_list.append(l)

            l_org_list_info.append(l_org_list)
            l_org_list_info.append(select_org_id)

            json_data_list_org.append(l_org_list_info)
            return json.dumps(json_data_list_org)
        else:#获取一级机构一级其子机构
            iSysOrg = SysOrg.objects.get(id=org_id)
            ids_parent = (iSysOrg.parent_ids + "," + str(iSysOrg.id)).split(',')
            id_select_node = ids_parent[1:]
            json_data_list_org = []
            for index in range(0, len(ids_parent)-1):
                id = ids_parent[index]#同一个级别机构选中的机构
                sys_list = SysOrg.objects.filter(parent_id=id)#同一个级别下的机构信息
                l_org_list = []#同一级别的机构信息
                l_org_list_info = []#同一级别的机构信息+选中状态的机构ID
                for info in sys_list:
                    l = []  # 机构信息，id和name
                    l.append(info.id)
                    l.append(info.org_name)
                    l_org_list.append(l)

                l_org_list_info.append(l_org_list)
                l_org_list_info.append(id_select_node[index])
                json_data_list_org.append(l_org_list_info)

            #检索自己子商户是否还有
            child_org_list = SysOrg.objects.filter(parent_id=org_id)
            l_org_list = []
            l_org_list_info = []
            for info in child_org_list:
                l = []  # 机构信息，id和name
                l.append(info.id)
                l.append(info.org_name)
                l_org_list.append(l)

            l_org_list_info.append(l_org_list)
            l_org_list_info.append(-2)
            json_data_list_org.append(l_org_list_info)

            return json.dumps(json_data_list_org)
#
class CreateUserView(CreateView, OrgTreeData):
    '''
    创建视图
    '''
    form_class = CreateUserForm
    template_name = 'sysadmin/user.add.html'

    #GET请求
    def get(self, request, *args, **kwargs):
        form = self.get_form()
        context = self.get_context_data(form=form)
        us = request.user.username
        industry_park =get_industry_park(us)
        context['industry_park'] = industry_park
        return self.render_to_response(context)

    #POST请求
    def post(self, request, *args, **kwargs):
        form = self.get_form(data=request.POST, files=request.FILES)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    #数据验证通过后执行
    def form_valid(self, form):
        self.save(form)
        return HttpResponseRedirect(reverse('sysadmin:user.list'))

    def form_invalid(self, form):
        us = self.request.user.username
        industry_park =get_industry_park(us)
        context = self.get_context_data(form=form)
        context['industry_park'] = industry_park
        return self.render_to_response(context)

    #保存
    def save(self, form):
        avatar = random.choice(range(35))
        avatar = '/static/avatar/%s.jpg' % avatar
        email = form.cleaned_data['email']
        phone = form.cleaned_data['phone']
        sex   = form.cleaned_data['sex']
        pwd   = form.cleaned_data['pwd2']
        role_id    = form.cleaned_data['role_id'].id
        username   = form.cleaned_data['username']
        industry_id   = form.cleaned_data['industry'].id
        # 生成Md5

        h = hashlib.md5()
        h.update(str(datetime.datetime.now()))
        token = h.hexdigest()

        #用户并验证
        SysUser.objects.create_user(email=email, username=username, password=pwd, sex=sex, type=-1, role_id=role_id,
                                     avatar=avatar, is_active=1, mobile=phone, industry_id=int(industry_id), token=token)
#编辑用户信息
class EditUserView(UpdateView, OrgTreeData):
    model = SysUser
    form_class = EditUserForm
    template_name = 'sysadmin/user.edit.html'

    #获取当前用户参数
    def get(self, request, *args, **kwargs):
        us = request.user.username
        industry_park =get_industry_park(us)
        url = self.request.get_full_path()
        industry_id = int(re.findall('(\d+)/$', url)[0])
        self.object = self.get_object()
        form = EditUserForm(self.object, None)
        context = self.get_context_data(form=form)
        context['industry_park'] = industry_park
        context['industry_id'] = industry_id
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form(data=request.POST, files=request.FILES)
        form.set_user(self.object)

        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    # 数据验证通过后执行
    def form_valid(self, form):
        self.save(form)
        return HttpResponseRedirect(reverse('sysadmin:user.list'))

    def save(self, form):
        email = form.cleaned_data['email']
        phone = form.cleaned_data['phone']
        sex = form.cleaned_data['sex']
        role_id = form.cleaned_data['role_id'].id
        username = form.cleaned_data['username']

        user = self.object
        user.email = email
        user.username = username
        user.mobile = phone
        user.sex = sex
        user.role_id = role_id
        user.save()

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

class UsereJson(BaseDatatableView):
    '''
    Json 数据格式
    '''
    model = SysUser
    columns = ['id', 'id', 'username',  'email', 'mobile', 'is_active', 'role.name', 'id']
    order_columns = ['id', 'id', 'username',  'email', 'mobile', 'is_active', 'role.name', 'id']

    #GET请求入口
    def get(self, request, *args, **kwargs):
        self.user = request.user
        return super(UsereJson, self).get(request, *args, **kwargs)
    def filter_queryset(self, qs):
        #搜索数据集
            search = self._querydict.get('search[value]', None)
            col_data = self.extract_datatables_column_data()

            q = Q()
            # if 0!=len(search):
            #     org_list = SysOrg.objects.filter(org_name__contains=search)
            #     for org in org_list:
            #         q = q|Q(sys_org_id = org.id)

            for col_no, col in enumerate(col_data):
                if search and col['searchable']:
                    q |= Q(**{'{0}__icontains'.format(self.columns[col_no].replace('.', '__')): search})
                if col['search.value']:
                    qs = qs.filter(
                        **{'{0}__icontains'.format(self.columns[col_no].replace('.', '__')): col['search.value']})
            qs = qs.filter(q)

            #1、在用户列表中屏蔽掉自己
            qs = qs.exclude(username=self.user.username)

            # 去除超级管理员的
            qs = qs.exclude(is_superuser = True)

            #2、如果是超级用户，那么直接返回
            if self.user.is_superuser:
                return qs


            return qs


def user_batches_delete(request):
    '''
    批量删除
    :param request:
    :return:
    '''
    json_data = json.loads(request.GET.get('ids'))
    list_id_del = json_data['ids']
    sql = Q()
    for id in list_id_del:
        sql = sql | Q(id=id)
    SysUser.objects.filter(sql).delete()
    name_dict = {'code': '00', 'desc': '删除成功!'}
    return JsonResponse(name_dict)



