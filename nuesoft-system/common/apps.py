#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : apps.py
# @Software: PyCharm
# @Function: 通用App类

from django.apps import AppConfig


class CommonConfig(AppConfig):
    name = 'nuesoft-system.common'

    verbose_name = "common"

    def ready(self):
        """Override this to put in:
            Users system checks
            Users signal registration
        """
        pass

