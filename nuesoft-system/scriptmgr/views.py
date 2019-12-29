#!/usr/bin/env python
# -*- coding: utf-8 -*-


from django.views.generic import TemplateView
from django.http import JsonResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from ..vanilla import CreateView
from models import *
from forms import *
import json
import os

def getFile():
    '''
    :return: 文件名列表
    '''
    path = 'D:\\pythonPJ\\pyvirtualenv\\nuesoft-system\\nuesoft-system\\media\\uploadfiles'
    # path = '/root/git/smartnet/'
    fileList = []
    files = os.listdir(path)
    for f in files:
        if(os.path.isfile(path + '/' + f)):
            fileList.append(f)
    return fileList

class scriptManager(TemplateView):
    template_name = 'scriptmgr/script.list.html'
    def get_context_data(self, **kwargs):
        context = super(scriptManager, self).get_context_data(**kwargs)
        filename_list = getFile()
        nodelist = []
        no = []
        i = 1
        for l in filename_list:
            dict_obj = {}
            dict_obj['text'] = l
            dict_obj['id'] = i
            dict_obj['tags'] = ['0']
            nodelist.append(dict_obj)
            no.append(l)
            i += 1

        context['no'] = no
        context['treedata'] = json.dumps(nodelist)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return super(scriptManager, self).get(request, *args, **kwargs)

    def post(self,request,*args, **kwargs):
        path =  'D:\\pythonPJ\\pyvirtualenv\\nuesoft-system\\nuesoft-system\\media\\uploadfiles'
        file_name = request.POST.get('file_name')
        test = TestFileParam.objects.get(file_name=file_name)
        table_ip = json.loads(test.ip_addr)
        table_param = json.loads(test.param)
        print table_ip, table_param
        data = []
        for ip in table_ip:

            for par in table_param:
                i = 0
                block = {}
                o_s = os.popen('python %s %s %s' % (path+file_name, ip, par))
                result =  o_s.read()
                block[str(i)] = result
                i += 1
                data.append(block)
        return JsonResponse(json.dumps(data),safe=False)

class CreateParamView(CreateView):
    # te = ['192.168.164.202']
    # TestFileParam.objects.filter(file_name='test_c2960.py').update(ip_addr=json.dumps(te))
    form_class = CreateParamForm
    template_name = 'zabbixmgr/testfile.add.html'

    #GET请求
    def get(self, request, *args, **kwargs):
        form = self.get_form()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    #POST请求
    def post(self, request, *args, **kwargs):
        form = self.get_form(data=request.POST, files=request.FILES)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    #数据验证通过后执行
    def form_valid(self, form):
        self.save(form)
        return HttpResponseRedirect(reverse('zabbixmgr:script.list'))

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    #保存
    def save(self, form):
        file_name = form.cleaned_data['file_name']
        ip_addr = form.cleaned_data['ip_addr']
        param = form.cleaned_data['param']

        test = TestFileParam.objects.get(file_name=file_name)
        table_ip = json.loads(test.ip_addr)
        ip_excit = False

        for ip in table_ip:
            if ip == ip_addr:
                ip_excit = True
        if ip_excit is False:
            table_ip.append(ip_addr)
            TestFileParam.objects.filter(file_name=file_name).update(ip_addr=json.dumps(table_ip))

        if test.type == '1':
            table_param = json.loads(test.param)
            param_excit = False
            for par in table_param:
                if par == param:
                    param_excit = True
            if param_excit is False:
                table_param.append(param)
                TestFileParam.objects.filter(file_name=file_name).update(param=json.dumps(table_param))
