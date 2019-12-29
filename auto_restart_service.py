#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/23 9:14
# @Author  :
# @Site    :
# @File    : auto_restart_service.py
# @Software: PyCharm

import os
import subprocess
import time
from multiprocessing import Process


def main():
    while True:
        p = subprocess.Popen("python start.py")
        #p=os.system("python manage.py runserver 0.0.0.0:8000")
        time.sleep(60*60*24)
        #p.terminate()
        #cmd = "taskkill /F /pid:"+str(p.pid)
        cmd="kill8000.bat"
        os.system(cmd)
main()
