#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls import url
from ..sysadmin import  views
from views_permission import *
from views_syslog import SyslogJson,SysLogList
from views_user import ListUser, user_batches_delete, UsereJson, CreateUserView, EditUserView
from views_role import ListRole, CreateRoleView, role_batches_delete,EditRoleView, RoleJson

urlpatterns = [

    #登录管理
    url(r'^login/$', views.login_, name='login'),  # 登录
    # url(r'^forgotpw/$', views.forgot_, name='forgotpw'),  # 忘记密码
    url(r'^logout/$', views.logout_, name='logout'),  # 退出
    url(r'^home$',views.main_page,name='home'),#主页

    #权限管理
    url(r'^sysadmin/permission/list/\d+$', Permissionlist.as_view(), name='permission.list'),  # 权限列表
    url(r'^sysadmin/permission/data$', PermissionJson.as_view(), name='permission.data'),  # 权限列表数据
    url(r'^sysadmin/permission/list/add$', CreatePermission.as_view(), name='permission.add'),  # 增加权限
    url(r'^sysadmin/permission/list/edit/(?P<pk>\d+)/$', EditPermission.as_view(), name='permission.edit'),  # 编辑权限
    url(r'^sysadmin/permission/delete$', permission_batches_delete, name='permission.delete'),#删除权限

    #无权限通知
    url(r'^error$', NoPermissionView.as_view(), name='permission.no'),  # 无权限通知
    url(r'^sysadmin/permission/treeview$', Permissiontreeview, name="permission.treeview"),

    #角色管理
    url(r'^sysadmin/role/list/\d+$', ListRole.as_view(), name="role.list"),  # 显示列表
    url(r'^sysadmin/role/delete$', role_batches_delete, name="role.delete"),  # 删除
    url(r'^sysadmin/role/data$', RoleJson.as_view(), name="role.data"),  # 获取数据
    url(r'^sysadmin/role/list/add$', CreateRoleView.as_view(), name='role.list.add'), #增加新用户
    url(r'^sysadmin/role/list/edit/(?P<pk>\d+)/$', EditRoleView.as_view(), name='role.list.edit'),#用户编辑

    #日志管理
    url(r'^sysadmin/syslog/list/\d+$', SysLogList.as_view(), name='syslog_list'),  # 操作记录页面
    url(r'^sysadmin/syslog/jsonlist/$', SyslogJson.as_view(), name='syslog_jsonlist'),  # 操作记录
    url(r'^sysadmin/syslog/list/search/$', views.syslog_list_search, name='syslog_list_search'),#操作记录查询

    #用户管理
    url(r'^sysadmin/user/list/\d+$', ListUser.as_view(), name="user.list"),  # 显示列表
    url(r'^sysadmin/user/data$', UsereJson.as_view(), name="user.data"),  # 获取数据
    url(r'^sysadmin/user/delete$', user_batches_delete, name="user.delete"),  # 删除
    url(r'^sysadmin/user/list/add$', CreateUserView.as_view(), name='user.add'),  # 增加新用户
    url(r'^sysadmin/user/list/edit/(?P<pk>\d+)/$', EditUserView.as_view(), name='user.edit'),  # 编辑权限

]
