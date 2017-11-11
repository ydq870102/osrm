#!/usr/bin/env python
# encoding: utf-8
from django.shortcuts import render
from django.template.context_processors import request
from django.http.response import HttpResponse
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from api import *
from cm.models import *
from django.db.models import Q
import time

# Create your views here.


@defend_attack
def Login(request):
    '''
    @登录方法
    '''
    error = ''
    for i,value in request.session.items():
        print i,value
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('asset'), locals())
    if request.method == 'GET':
        return render_to_response('login.html', locals())
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('asset'), locals())
                else:
                    error = '用户未激活'
            else:
                error = '用户名或密码错误'
        else:
            error = '用户名或密码错误'
    return render_to_response('login.html', locals())

def Logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

@require_role()
def index(request):
    '''
    @首页
    '''
    return HttpResponseRedirect(reverse('asset'))

@require_role()
def asset(request):
    '''
    @主机
    '''
    keyword = request.GET.get('keyword', '')
    object_list = host.objects.all().order_by('ipaddr')
    if keyword:
        object_list = host.objects.filter(Q(label_cn__icontains=keyword) | Q(ipaddr__icontains=keyword)|Q(private_ipaddr__icontains=keyword))
    
    object_list, p, objects, page_range, current_page, show_first, show_end = pages(object_list, request)

    return render_to_response('host.html', locals())

@require_role()
def asset_perfor(request):
    '''
    @主机
    '''
    return render_to_response('host_perfor.html', locals())

@require_role()
def asset_del(request):
    '''
    @主机删除
    '''
    if request.method == "GET":
        host_ids = request.GET.get('id', '')
        host_id_list = host_ids.split(',')
    elif request.method == "POST":
        host_ids = request.POST.get('id', '')
        host_id_list = host_ids.split(',')
    else:
        return HttpResponse('错误请求')

    for host_cuid in host_id_list:
        print host_cuid
        host_obj = get_object(host, cuid=host_cuid)
        host_obj.delete()
    return HttpResponse('删除成功')

@require_role()
def asset_add(request):
    '''
    @主机新增
    '''
    error = ''
    msg = ''
    if request.method == "POST":
        label_cn = request.POST.get('label_cn','')
        alias = request.POST.get('alias','')
        ipaddr = request.POST.get('ipaddr','')
        private_ipaddr = request.POST.get('private_ipaddr','')
        os_version = request.POST.get('os_version','')
        vendor = request.POST.get('vendor','')
        related_system_cn = request.POST.get('related_system_cn','')
        
        if host.objects.filter(Q(label_cn=label_cn) | Q(ipaddr=ipaddr)):
            error = u'主机名或IP已存在'
        else:
            try:
                host(related_system_cn = related_system_cn,
                     label_cn = label_cn,
                     alias = alias,
                     ipaddr = ipaddr,
                     private_ipaddr = private_ipaddr,
                     os_version = os_version,
                     vendor = vendor,
                     cuid = get_cuid('CM_HOST')
                     ).save()
                msg = u'主机添加成功' 
            except Exception,e:
                error = e
            
        return render_to_response('host_add.html', locals())
    elif request.method == "GET":
        return render_to_response('host_add.html', locals())

@require_role()
def asset_edit(request):
    '''
    @主机编辑
    '''
    error = ''
    msg = ''
    cuid = request.GET.get('cuid','')
    object_list = get_object(host,cuid=cuid)
    if request.method == "GET":
        return render_to_response('host_edit.html', locals())
    
    elif request.method == "POST":
        cuid = request.GET.get('cuid','')
        label_cn = request.POST.get('label_cn','')
        alias = request.POST.get('alias','')
        ipaddr = request.POST.get('ipaddr','')
        private_ipaddr = request.POST.get('private_ipaddr','')
        os_version = request.POST.get('os_version','')
        vendor = request.POST.get('vendor','')
        related_system_cn = request.POST.get('related_system_cn','')
        
        if host.objects.filter(Q(label_cn=label_cn) & Q(ipaddr=ipaddr) & ~Q(cuid=cuid)):
            error = u'主机名或IP已存在'
        else:
            try:
                get_update_object(host,cuid=cuid).update(related_system_cn = related_system_cn,
                                   label_cn = label_cn,
                                   alias = alias,
                                   ipaddr = ipaddr,
                                   private_ipaddr = private_ipaddr,
                                   os_version = os_version,
                                   vendor = vendor,
                                   last_modify_time = time.strftime(ISOTIMEFORMAT, time.localtime(time.time()))
                                   )
                msg = u'主机修改成功' 
            except Exception,e:
                error = e
        return render_to_response('host_edit.html', locals())

@require_role()    
def asset_detail(request):
    '''
    @主机详情
    '''
    error = ''
    msg = ''
    cuid = request.GET.get('cuid','')
    if not cuid:
        return render_to_response('index.html')
    host_info = get_object(host,cuid=cuid)
    memory_info = get_object(current_memory,related_host_cuid=host_info)
    cpu_info = get_object(current_cpu,related_host_cuid=host_info)
    disk_info = get_any_object(current_disk,related_host_cuid=host_info)
    if disk_info:
        disk_total = 0
        for line in disk_info:
            disk_total =convert_to_byte(line.device_total) + disk_total
        disk_total = convert_bytes(disk_total)
    else:
        disk_total =None
    if request.method == "GET":
        
        return render_to_response('host_detail.html', locals())
    
@require_role()    
def database_list(request):
    '''
    @数据库
    '''
    keyword = request.GET.get('keyword', '')
    object_list = database.objects.all().order_by('ipaddr')
    if keyword:
        object_list = database.objects.filter(Q(label_cn__icontains=keyword) | Q(ipaddr__icontains=keyword))
    
    object_list, p, objects, page_range, current_page, show_first, show_end = pages(object_list, request)

    return render_to_response('database.html', locals())

@require_role()
def database_del(request):
    '''
    @数据库删除
    '''
    if request.method == "GET":
        database_ids = request.GET.get('id', '')
        database_id_list = database_ids.split(',')
    elif request.method == "POST":
        database_ids = request.POST.get('id', '')
        database_id_list = database_ids.split(',')
    else:
        return HttpResponse('错误请求')

    for database_cuid in database_id_list:
        database_obj = get_object(database, cuid=database_cuid)
        database_obj.delete()
    return HttpResponse('删除成功')

@require_role()
def database_add(request):
    '''
    @数据库新增
    '''
    error = ''
    msg = ''
    if request.method == "POST":
        cuid = request.GET.get('cuid','')
        label_cn = request.POST.get('label_cn','')
        port = request.POST.get('port','')
        ipaddr = request.POST.get('ipaddr','')
        sid = request.POST.get('sid','')
        service_name = request.POST.get('service_name','')
        user_name = request.POST.get('user_name','')
        passwd = request.POST.get('passwd','')
        
        try:
            database(   
                    label_cn = label_cn,
                    port = port,
                    ipaddr = ipaddr,
                    sid = sid,
                    service_name = service_name,
                    passwd = passwd,
                    cuid = get_cuid('CM_DATABASE'),
                    user_name = user_name
                    ).save()
            msg = u'数据库添加成功' 
        except Exception,e:
            error = e
            
        return render_to_response('database_add.html', locals())
    elif request.method == "GET":
        return render_to_response('database_add.html', locals())

@require_role()    
def database_edit(request):
    '''
    @数据库编辑
    '''
    error = ''
    msg = ''
    cuid = request.GET.get('cuid','')
    if not cuid:
        return render_to_response('index.html')
    object_list = get_object(database,cuid=cuid)
    if request.method == "GET":
        
        return render_to_response('database_edit.html', locals())
    
    elif request.method == "POST":
        cuid = request.GET.get('cuid','')
        label_cn = request.POST.get('label_cn','')
        port = request.POST.get('port','')
        ipaddr = request.POST.get('ipaddr','')
        sid = request.POST.get('sid','')
        service_name = request.POST.get('service_name','')
        user_name = request.POST.get('user_name','')
        passwd = request.POST.get('passwd','')
        
        try:
            get_update_object(database,cuid=cuid).update(   
                                                  label_cn = label_cn,
                                                  port = port,
                                                  ipaddr = ipaddr,
                                                  sid = sid,
                                                  service_name = service_name,
                                                  passwd = passwd,
                                                  cuid = cuid,
                                                  user_name = user_name,
                                                  )
            msg = u'数据库修改成功' 
        except Exception,e:
            error = e
        return render_to_response('database_edit.html', locals())
    
@require_role()    
def process_list(request):
    '''
    @应用
    '''
    error = ''
    msg = ''
    keyword = request.GET.get('keyword', '')
    object_list = process.objects.all().order_by('label_cn')
    if keyword:
        object_list = process.objects.filter(Q(label_cn__icontains=keyword) | Q(alias__icontains=keyword))
    
    object_list, p, objects, page_range, current_page, show_first, show_end = pages(object_list, request)

    return render_to_response('process.html', locals())

@require_role()
def process_del(request):
    '''
    @应用删除
    '''
    if request.method == "GET":
        process_ids = request.GET.get('id', '')
        process_id_list = process_ids.split(',')
    elif request.method == "POST":
        process_ids = request.POST.get('id', '')
        process_id_list = process_ids.split(',')
    else:
        return HttpResponse('错误请求')
    print process_ids,process_id_list
    for process_cuid in process_id_list:
        process_obj = get_object(process, cuid=process_cuid)
        process_obj.delete()
    return HttpResponse('删除成功')

@require_role()
def process_add(request):
    '''
    @应用新增
    '''
    error = ''
    msg = ''
    host_list = host.objects.all()
    if request.method == "POST":
        label_cn = request.POST.get('label_cn','')
        alias = request.POST.get('alias','')
        related_group_cuid = request.POST.get('related_group_cuid','')
        path = request.POST.get('path','')
        url_path = request.POST.get('url_path','')
        middleware_type = request.POST.get('middleware_type','')
        related_system_cn = request.POST.get('related_system_cn','')
        related_host_cuid = request.POST.get('related_host_cuid','')
        is_restart = request.POST.get('is_restart','')
        restart_command = request.POST.get('restar_common','')

        if process.objects.filter(Q(label_cn=label_cn) & Q(related_host_cuid=related_host_cuid)):
            error = u'应用已存在'
        else:
            try:
                print related_group_cuid
                process(related_system_cn = related_system_cn,
                         label_cn = label_cn,
                         alias = alias,
                         related_group_cuid = related_group_cuid,
                         path = path,
                         url_path = url_path,
                         middleware_type = middleware_type,
                         related_host_cuid = get_object(host,cuid = related_host_cuid),
                         is_restart = is_restart,
                         restart_command = restart_command,
                         cuid = get_cuid('CM_PROCESS')
                         ).save()
                msg = u'应用添加成功' 
            except Exception,e:
                error = e
            
        return render_to_response('process_add.html', locals())
    elif request.method == "GET":
        
        return render_to_response('process_add.html', locals())

@require_role()    
def process_edit(request):
    '''
    @应用编辑
    '''
    error = ''
    msg = ''
    host_list = host.objects.all()
    cuid = request.GET.get('cuid','')
    object_list = get_object(process,cuid=cuid)
    if request.method == "GET":
        
        return render_to_response('process_edit.html', locals())
    
    elif request.method == "POST":
        label_cn = request.POST.get('label_cn','')
        alias = request.POST.get('alias','')
        related_group_cuid = request.POST.get('related_group_cuid','')
        path = request.POST.get('path','')
        url_path = request.POST.get('url_path','')
        middleware_type = request.POST.get('middleware_type','')
        related_system_cn = request.POST.get('related_system_cn','')
        related_host_cuid = request.POST.get('related_host_cuid','')
        is_restart = request.POST.get('is_restart','')
        restart_command = request.POST.get('restar_common','')

        try:
            get_update_object(process,cuid=cuid).update(related_system_cn = related_system_cn,
                    label_cn = label_cn,
                    alias = alias,
                    related_group_cuid = related_group_cuid,
                    path = path,
                    url_path = url_path,
                    middleware_type = middleware_type,
                    related_host_cuid = get_object(host,cuid = related_host_cuid),
                    is_restart = is_restart,
                    restart_command = restart_command)
            msg = u'应用修改成功' 
        except Exception,e:
            error = e
        return render_to_response('process_edit.html', locals())
    
@require_role()    
def process_detail(request):
    
    cuid = request.GET.get('cuid','')
    if not cuid:
        return render_to_response('index.html')
    process_info = get_object(process,cuid=cuid)
    cur_process_info = get_any_object(current_process,related_process_cuid=cuid)[0]
    if request.method == "GET":
        
        return render_to_response('process_detail.html', locals())



@require_role()    
def monitor_list(request):
    '''
    @监控查询
    '''
    error = ''
    msg = ''
    keyword = request.GET.get('keyword', '')
    object_list = monitor.objects.all().order_by('cuid')
    if keyword:
        host_list = host.objects.filter(Q(ipaddr__icontains=keyword))
        process_list = process.objects.filter(related_host_cuid__in = host_list )
        database_list = database.objects.filter(related_host_cuid__in = host_list )
        object_list = monitor.objects.filter(Q(monitor_type__icontains=keyword)|Q(monitor_object__in=host_list)|Q(monitor_object__in=process_list)|Q(monitor_object__in=database_list))
    
    object_list, p, objects, page_range, current_page, show_first, show_end = pages(object_list, request)

    return render_to_response('monitor.html', locals())

@require_role()
def monitor_add(request):
    pass

@require_role()
def monitor_del(request):
    '''
    @应用删除
    '''
    if request.method == "GET":
        monitor_ids = request.GET.get('id', '')
        monitor_id_list = monitor_ids.split(',')
    elif request.method == "POST":
        monitor_ids = request.POST.get('id', '')
        monitor_id_list = monitor_ids.split(',')
    else:
        return HttpResponse('错误请求')
    for monitor_cuid in monitor_id_list:
        monitor_obj = get_object(monitor, cuid=monitor_cuid)
        monitor_obj.delete()
    return HttpResponse('删除成功')

@require_role()
def monitor_edit(request):
    error = ''
    msg = ''
    host_list = host.objects.all()
    cuid = request.GET.get('cuid','')
    alarm_desc = monitor_value.objects.all()
    ranges =range(1,5)
    object_list = get_object(monitor,cuid=cuid)
    
    if request.method == "GET":
        
        return render_to_response('monitor_edit.html', locals())
    
    elif request.method == "POST":
        cuid = request.POST.get('cuid','')
        monitor_level = request.POST.get('monitor_level','')
        monitor_desc = request.POST.get('monitor_desc','')
        is_send = request.POST.get('is_send','')

        get_update_object(monitor,cuid=cuid).update(monitor_level =monitor_level,
                                                    is_send = is_send,
                                                    monitor_alarm_type = monitor_desc )
      
        msg = u'修改成功' 

        return render_to_response('monitor_edit.html', locals())
    
@require_role()
def alarm_list(request):
    '''
    @告警查询
    '''
    error = ''
    msg = ''
    keyword = request.GET.get('keyword', '')
    object_list = alarm.objects.all().order_by('cuid')
    if keyword:
        object_list = alarm.objects.filter(Q(ip__icontains=keyword)|Q(alarm_title__icontains=keyword))
    
    object_list, p, objects, page_range, current_page, show_first, show_end = pages(object_list, request)

    return render_to_response('alarm.html', locals())

@require_role()
def alarm_detail(request):
    
    cuid = request.GET.get('cuid','')
    if not cuid:
        return render_to_response('index.html')
    process_info = get_object(process,cuid=cuid)
    cur_process_info = get_any_object(current_process,related_process_cuid=cuid)[0]
    if request.method == "GET":
        
        return render_to_response('process_detail.html', locals())

def page_error(request):
    return render(request, '500.html')


def page_not_found(request):
    return render(request, '404.html')