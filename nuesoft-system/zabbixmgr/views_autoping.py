#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/14 11:02
# @Author  :
# @Site    :
# @File    : views_autoping.py
# @Software: PyCharm

from django.views.generic import TemplateView
from ..common.datatables.views import BaseDatatableView
from models import *
from forms import *
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from ..vanilla.model_views import *
from subprocess import *
import json
from constant import get_industry_park

class AutoPing(CreateView):
    form_class = AutoPingForm
    template_name = 'dialing/auto_ping.html'

    def autoping(self, ip):
        p = Popen('ping %s' % ip,
          stdout=PIPE,
          stderr=PIPE,
          shell=True
          )
        p.wait()
        out = p.stdout.read()
        l = out.split('\n')
        li = {}
        for i in range(len(l)):
            li[str(i)] = l[i].decode('gbk')
        return li

    def form_valid(self,form):
        ip = form.cleaned_data['ip']
        context = self.autoping(ip)
        return render(self.request, 'dialing/autoping.list.html', {'con': context})

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return self.render_to_response(context)


