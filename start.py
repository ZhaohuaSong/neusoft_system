#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/9 15:25
# @Author  :
# @Site    :
# @File    : start.py
# @Software: PyCharm5
# @Function:

import os
import sys

def start(port):
    os.system('python manage.py runserver 0.0.0.0:'+str(port))

if __name__ == '__main__':
    s = 0
    if len(sys.argv) == 1:
        port = 8080
    elif len(sys.argv) == 2:
        port = sys.argv[1]
    start(port)

