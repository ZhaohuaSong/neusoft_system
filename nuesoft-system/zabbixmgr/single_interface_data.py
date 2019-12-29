#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/11/15 16:18
# @Author  :
# @Site    :
# @File    : single_interface_data.py
# @Software: PyCharm

from models import *

class FiveMinData():

    def get_data(self):
        fiv_data = OneminDatas.objects.filter(client_id=1)
