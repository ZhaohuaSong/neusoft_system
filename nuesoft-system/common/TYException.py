#!/usr/bin/env python
# -*- coding: utf-8 -*-

#异常类
class EMsgException(Exception):
    #参数：信息，解决方案列表
    #msg:字符串
    #resolvent_list：列表
    def __init__(self, msg, resolvent_list):
        self.message = msg
        self.resolvent_list = resolvent_list