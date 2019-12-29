#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render_to_response, render
import json
from django.views.generic import TemplateView
from ..vanilla import CreateView, DeleteView, ListView, UpdateView
from ..common.datatables.views import BaseDatatableView
from models import SysUser, RoleList, PermissionList, SysOrg
from ..sysadmin.forms import PermissionListForm, EditPermissionListForm
from django.db import transaction
from ..zabbixmgr.constant import get_industry_park
import re
_logger = logging.getLogger('loggers')


@login_required
def NoPermission(request):
    print '============================'
    print request.user
    kwvars = {
        'request':request,
    }

    return render_to_response('sysadmin/permission.no.html',kwvars,request)



class NoPermissionView(TemplateView):
    template_name = 'sysadmin/permission.no.html'

class EditPermission(UpdateView):
    """
    编辑权限
    :param request:
    :return:
    """
    model = PermissionList
    # form_class = EditPermissionListForm
    # success_url = '/sysadmin/permission/list'
    template_name = 'sysadmin/permission.edit.html'

    # def get(self, request, *args, **kwargs):
    #     self.object = self.get_object()
    #     form = PermissionListForm()
    #     context = self.get_context_data(form=form)
    #     context['type'] = self.object.type
    #     return self.render_to_response(context)
    # #
    # # def post(self, request, *args, **kwargs):
    # #     self.object = self.get_object()
    # #     self.get_form().setId(self.object.id)
    # #     return super(EditPermission, self).post(request, *args, **kwargs)

    def __init__(self):
        self.change_info = []  # 更改信息列表 其元素为字典(old_id, new_id)
        super(UpdateView, self).__init__()

    def get(self, request, *args, **kwargs):
        permissionlist = self.get_object()
        result_vale_data = self.getPermissionLevel(permissionlist)
        form = EditPermissionListForm(permissionlist,None)
        context = self.get_context_data(form=form)
        context['json_data'] = json.dumps(result_vale_data)
        context['type'] = permissionlist.type
        context['request'] = request
        context['id'] = permissionlist.id
        us = request.user.username
        industry_park =get_industry_park(us)
        context['industry_park'] = industry_park
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        permissionlist = self.get_object()
        form = EditPermissionListForm(permissionlist, None, request.POST)
        form.setId(permissionlist.id)
        if form.is_valid():
            return self.form_valid(request)
        return self.form_invalid(form)
    def form_invalid(self, form):
        permissionlist = self.get_object()
        result_vale_data = self.getPermissionLevel(permissionlist)
        context = self.get_context_data(form=form)
        context['json_data'] = json.dumps(result_vale_data)
        context['type'] = permissionlist.type
        context['id'] = permissionlist.id
        return self.render_to_response(context)

    def getPermissionLevel(self, permissionlist):
        ids = permissionlist.parent_ids.split(',')
        ids.append(permissionlist.id)  # 加上自身的ID
        ids_all_list = ids[1:]  # 拆出父级目录
        bTop = permissionlist.parent_ids == '0'
        result_vale_data = []
        for index, tab_data in enumerate(ids[0:-1]):
            result_vale_list = []
            select_data_list = []
            val_data = PermissionList.objects.filter(parent_id=tab_data)
            for val_l in val_data:
                if permissionlist.id != val_l.id:
                    select_data = []
                    select_data.append(val_l.id)
                    select_data.append(val_l.name)
                    select_data_list.append(select_data)

            result_vale_list.append(select_data_list)
            if bTop:
                result_vale_list.append('-2')
            else:
                result_vale_list.append(ids_all_list[index])

            result_vale_data.append(result_vale_list)
        return result_vale_data

    def form_valid(self, request):
        self.save(request)
        return HttpResponseRedirect(reverse('sysadmin:permission.list'))

    # 根据父级ID计算出自己的ID值
    def create_new_id(self, parent_id):
        child_list_info = PermissionList.objects.filter(parent_id=parent_id)
        max_org_id = 0
        for info in child_list_info:
            id = int(info.id)
            if max_org_id < id:
                max_org_id = id

        if 0 == max_org_id:  # 说明此刻还没有下级节点
            return str(int(parent_id) * 10000 + 1)
        else:
            return str(max_org_id + 1)

    # 获取自己的ids
    def create_new_parent_ids(self, parent_id):
        if int(parent_id) == 0:
            return '0'

        info = PermissionList.objects.get(id=parent_id)
        ids = info.parent_ids
        ids = ids + ',' + str(parent_id)
        return ids

    def save(self, request):
        user = request.user
        name = request.POST.get('name', '')  # 栏目名称
        target_id = request.POST.get('id', '')  # 权限ID
        type = request.POST.get('type', '')  # 权限类型
        url = request.POST.get('url', '')  # 权限url

        permissionlist = self.get_object()  # 当前要修改的对象

        name = name.lstrip().rstrip()

        if permissionlist.id == target_id:  # 父级目录不变 更改商户号和商户名称即可

            permissionlist.name = name

            if type=="on":
                permissionlist.type=1
            else:
                permissionlist.type=0
            permissionlist.url = url
            permissionlist.save()
        else:  # 否则就是要更爱级别关系，那么 此处要更改该级别一下的所有级别ID
            new_parent_id = target_id  # 新的父级节点ID

            if -2 == int(new_parent_id):
                new_parent_id = '0'

            with transaction.atomic():
                permissionlist.name =name
                if type=="on":
                 permissionlist.type=1
                else:
                 permissionlist.type=0
                permissionlist.url = url
                self.change_org_info(new_parent_id, permissionlist)

    # 递归更新该节点的所有子节点ID以及树列表
    def change_org_info(self, new_parent_id, permissionlist):
        child_list = PermissionList.objects.filter(parent_id=permissionlist.id)

        new_self_id = self.create_new_id(new_parent_id)
        self.change_info.append((permissionlist.id, new_self_id))
        parent_ids = self.create_new_parent_ids(new_parent_id)


        sql = "UPDATE permissionlist SET id = '%s',  parent_id='%s', parent_ids='%s' WHERE id = '%s'" % (
        new_self_id, new_parent_id, parent_ids, permissionlist.id)
        try:
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute(sql)
            cursor.close()
        except:
            raise Exception('权限修改异常')

        if len(child_list) != 0:
            for info in child_list:
                self.change_org_info(new_self_id, info)




class CreatePermission(CreateView):
    '''
    创建交易类型视图
    '''
    model = PermissionList
    form_class = PermissionListForm
    # success_url = '/sysadmin/permission/list'
    template_name = 'sysadmin/permission.add.html'

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        context = self.get_context_data(form=form)
        us = request.user.username
        industry_park =get_industry_park(us)
        context['industry_park'] = industry_park
        return self.render_to_response(context)

      # 重写
    def post(self, request, *args, **kwargs):
        tag = request.POST.get('tag')
        if tag == "0":  # 获取该机构的附属机构列表

            return self.get_next_org_list(request)
        else:
            form = self.get_form(data=request.POST, files=request.FILES)
            if form.is_valid():
                return self.form_valid(request)
            return self.form_invalid(form)


    # 获取权限列表
    def get_next_org_list(self, request):
        parent_id = request.POST.get('parent_id')
        select_parent_data = PermissionList.objects.filter(parent_id__exact=parent_id);

        select_data_list = []
        for data in select_parent_data:
            select_data_list_object = []
            select_data_list_object.append(data.id)
            select_data_list_object.append(data.name)
            select_data_list.append(select_data_list_object)

        return HttpResponse(json.dumps({"select_data_list": select_data_list}))

    # 重写
    def form_valid(self, request):
        self.save(request)
        return HttpResponseRedirect(reverse('sysadmin:permission.list'))

    # 保存添加
    def save(self, request):
        name = request.POST.get('name', '')  # 权限名称
        target_id = request.POST.get('id', '')  # 权限ID
        # column_sort = request.POST.get('column_sort', '')  # 排序号号
        type = request.POST.get('type', '')  # 权限类型
        url = request.POST.get('url', '')  # 权限url
        user = request.user
        ##去空格
        name =name.lstrip().rstrip()
        # column_sort = column_sort.lstrip().rstrip()

        ################################################################################
        # 整理parend_id和分支链表 和生成新节点的ID new_id
        bTop = False  # 是否创建的是顶级商户

        # 整理出来parent_id
        if int(target_id) == -2:
            parend_id = '0'
            bTop = True
        else:
            parend_id = target_id

        # 生成新ID以及父级目录
        child_list_info = PermissionList.objects.filter(parent_id=parend_id)
        max_org_id = 0
        for info in child_list_info:
            id = int(info.id)
            if max_org_id < id:
                max_org_id = id

        if bTop is False:  # 非顶级栏目
            parent_info = PermissionList.objects.get(id=parend_id)
            parents_ids = parent_info.parent_ids + "," + parend_id

            if max_org_id == 0:  # 说明当前是该父节点的第一个孩子节点
                new_id = int(parend_id) * 10000 + max_org_id + 1
            else:
                new_id = max_org_id + 1
        else:  # 顶级商户
            parents_ids = '0'
            new_id = max_org_id + 1
        ################################################################################
        info = PermissionList()
        info.id = new_id
        info.name =name
        info.parent_id = parend_id
        info.url=url
        if type=="on":
            info.type=1
        else:
            info.type=0
        info.parent_ids = parents_ids
        info.save()



class Permissionlist(TemplateView):
    template_name = 'sysadmin/permission.list.html'

    def get(self, request, *args, **kwargs):
        us = request.user.username
        industry_park =get_industry_park(us)
        url = self.request.get_full_path()
        industry_id = int(re.findall('(\d+)$', url)[0])
        context = self.get_context_data(**kwargs)
        context['industry_park'] = industry_park
        context['industry_id'] = industry_id
        return self.render_to_response(context)

class PermissionJson(BaseDatatableView):

    model = PermissionList
    columns = ['id', 'id', 'name', 'url', 'type', 'id']
    order_columns = ['id', 'id', 'name', 'type', 'url']
    def filter_queryset(self, qs):
        id  = self._querydict.get('id')
        print id
        if 0==len(id):#默认
            return super(PermissionJson, self).filter_queryset(qs).all()
        elif id == '-11':
            return super(PermissionJson, self).filter_queryset(qs)
        elif (id == '0'):#也是默认
            return super(PermissionJson, self).filter_queryset(qs).all()
            #return super(CommercialJson, self).filter_queryset(qs).filter(Q(parent_id=id) | Q(id=id))
        else:
            return super(PermissionJson, self).filter_queryset(qs).filter(Q(parent_id=id) | Q(id=id))


def permission_batches_delete(request):
    '''
    批量删除
    :param request:
    :return:
    '''
    json_data = json.loads(request.GET.get('ids'))
    # print json_data
    list_id_del = json_data['ids']
    # print list_id_del
    sql=Q()
    sql_org_parent_id = Q()  # 要删除的机构查看是否有存在子目录
    for id in list_id_del:
        sql = sql | Q(id=id)
        sql_org_parent_id = sql_org_parent_id | Q(parent_id=id)

    if 0 != len(PermissionList.objects.filter(sql_org_parent_id)):
        name_dict = {'code': '01', 'desc': '该选中的权限下存在子级不能删除！需先删除其下子级后才能删除！'}
    else:
        PermissionList.objects.filter(sql).delete()
        name_dict = {'code': '00', 'desc': '删除成功'}

    return JsonResponse(name_dict)


def Permissiontreeview(request):
    if request.method == 'GET':
        parent_id = request.GET.get('parent_id')
        search_value = request.GET.get('search_value')
        vo = TreeRespVO()
        # if search_value:
        #     tree_nodes = SysOrg.objects.all().filter(org_name__contains=search_value)
        # else:
        sys_org_list = PermissionList.objects.all()
        tree_nodes = get_tree_nodes_ds(sys_org_list, "0")  # 获取树形结构
        # data_list = get_tree_nodes(nodes, "0")
        # print tree_nodes
        vo.setData(tree_nodes)
        # print vo.__dict__
        data = json.dumps(vo.__dict__)
        jsondata = json.loads(data)
        print jsondata['data']
    return HttpResponse(json.dumps(jsondata['data']))
def get_tree_nodes_ds(list, pid):
    '''
    生成数据源 Q
    :param list:
    :return:
    '''
    nodeList = []
    for sys_org in list:
        if str(sys_org.parent_id) == pid:
            tree_node = TreeNode()
            tree_node.id = sys_org.id
            tree_node.pid = sys_org.parent_id
            tree_node.name = sys_org.name
            child_list = get_tree_nodes_ds(list, str(sys_org.id))
            tree_node.children = child_list
            nodeList.append(tree_node.dict())
    return nodeList
class TreeNode:
    def __int__(self, id=None, pid=None, children=None):
        self.id = id
        self.pid = pid
        self.children = children
        self.name = ""
    def dict(self):
        return {'id': self.id, 'name': self.name, 'pid': self.pid, 'children': self.children}
class TreeRespVO:
    data = object

    def __init__(self, data=None):
        self.data = data

    def setData(self, parm):
        self.data = parm

