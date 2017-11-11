#!/usr/bin/env python
# encoding: utf-8
from django.shortcuts import render
from django.http.response import HttpResponse

from cm import cm_api
import threading
import json
# Create your views here.


def recevice_json_data(request):
    
    if request.method == 'POST':
        try:
            json_data = json.loads(request.POST.items()[0][0])
            cm = threading.Thread(target=cm_api.cm_parse,args=[json_data]).start()  #资源采集数据入库
            #am = threading.Thread(target=cm_api.am_parse,args=[json_data]).start()  #告警采集数据入库
            return  HttpResponse('ok')
        except Exception,e:
            return  HttpResponse('failed:%e'%e)