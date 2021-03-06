#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from django import template
from ...sysadmin.models import SysUser,RoleList


register = template.Library()

def has_permission(value,arg):
    """
    ============================================================================
    function:
    note:   商户权限管理
    ============================================================================
    """
    iUser = SysUser.objects.get(id=value.id)
    if not iUser.is_superuser: #判断用户如果是超级管理员则具有所有权限
        if not iUser.role: #如果用户无角色，直接返回无权限
            return False

        role_permission = RoleList.objects.get(name=iUser.role)
        role_permission_list = role_permission.permission.all()

        matchUrl = []
        for x in role_permission_list:
            if arg == x.url or arg.rstrip('/') == x.url: #精确匹配，判断request.path是否与permission表中的某一条相符
                matchUrl.append(x.url)
            elif arg.startswith(x.url): #判断request.path是否以permission表中的某一条url开头
                matchUrl.append(x.url)
            else:
                pass
        if len(matchUrl) == 0:
            return False
        else:
            return True

    elif iUser.is_superuser:
        return True
    else:
        return False

register.filter('has_permission', has_permission)
