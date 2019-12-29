#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/13 9:15
# @Author  :
# @Site    :
# @File    : ping.py
# @Software: PyCharm
from subprocess import *


p = Popen('ping www.baidu.com',
  stdout=PIPE,
  stderr=PIPE,
  shell=True
  )
p.wait()
out = p.stdout.read()
l = out.split('\n')
for i in l:
    print i.decode('gbk')
