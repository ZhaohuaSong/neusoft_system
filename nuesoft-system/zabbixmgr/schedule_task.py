#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/10/30 14:58
# @Author  :
# @Site    :
# @File    : schedule_task.py
# @Software: PyCharm

import time
from apscheduler.scheduler import Scheduler
# sched = Scheduler()
#
# @sched.interval_schedule(days=1, start_date='2018-6-27 9:48')
#
# def mytask():
#     print 'kobe'
#
# sched.start()
#
# while 1:
#     time.sleep(3600)
#     print 'kkkk'
from interval_datas import CreateIntervalDatas
def scheduler_task():
    # time.sleep(600)
    cr = CreateIntervalDatas()
    cr.context_data()

# sched.start()
import schedule
schedule.every().day.at("00:10").do(scheduler_task)
while True:
    schedule.run_pending()
    time.sleep(1)
    print 'kkkkkkkkkkk'
