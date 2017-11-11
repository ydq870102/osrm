#!/usr/bin/env python
# encoding: utf-8

import logging
import logging.handlers
from osrm.settings import *
import redis
import sys
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.http import HttpResponse, Http404,HttpResponseRedirect
from django.core.urlresolvers import reverse


logger = logging.getLogger('server')

def set_log(level, filename='server.log'):
    """
    @日志函数 根据提示设置log打印，返回日志对象
    """
    log_file = os.path.join(LOG_DIR, filename)
    if not os.path.exists(LOG_DIR):
        os.mkdir(LOG_DIR)
    log_level_total = {'debug': logging.DEBUG, 'info': logging.INFO, 'warning': logging.WARN, 'error': logging.ERROR,
                       'critical': logging.CRITICAL}
    logger_f = logging.getLogger('server')
    logger_f.setLevel(logging.DEBUG)
    fh = logging.handlers.RotatingFileHandler(log_file, maxBytes = 1024*1024*100, backupCount = 5)
    fh.setLevel(log_level_total.get(level, logging.DEBUG))
    formatter = logging.Formatter('%(asctime)s - %(threadName)s- %(filename)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger_f.addHandler(fh)
    return logger_f


class RedisHelper(object):
    
    def __init__(self):
        self.__conn = redis.Redis(host=REDIS_HOST,port=int(REDIS_PORT),password=REDIS_PASSWD,socket_timeout=3)
        self.chan_sub = 'fm104.5'
        self.chan_pub = 'fm87.7'
    def get(self,key):
        return self.__conn.get(key)
    
    def set(self,key,value):
        self.__conn.set(key, value)
    
    def Keydel(self,key):
        a=self.__conn.delete(key)
        return a
    
    def exists(self,key):
        a=self.__conn.exists(key)
        return a
        
    def public(self,msg):
        self.__conn.publish(self.chan_pub, msg) 
        return True 
    def subscribe(self):
        pub = self.__conn.pubsub()
        pub.subscribe(self.chan_pub)
        pub.parse_response()
        return pub
    def flush_all(self):
        self.__conn.flushdb()
        
        
        
def get_object(model, **kwargs):
    """
    
    @数据库查询封装函数    返回查询结果对象
    """
    for value in kwargs.values():
        if not value:
            return None

    the_object = model.objects.filter(**kwargs)
    if len(the_object) == 1:
        the_object = the_object[0]
    else:
        the_object = None
    return the_object


def get_update_object(model, **kwargs):
    """
    
    @数据库查询封装函数    返回查询结果对象
    """
    for value in kwargs.values():
        if not value:
            return None

    the_object = model.objects.filter(**kwargs)
    if len(the_object) == 1:
        the_object = the_object
    else:
        the_object = None
    return the_object

def get_any_object(model, **kwargs):
    """
    
    @数据库查询封装函数    返回查询结果对象
    """
    for value in kwargs.values():
        if not value:
            return None

    the_object = model.objects.filter(**kwargs)
    if len(the_object) >= 1:
        the_object = the_object
    else:
        the_object = None
    return the_object

def get_cur_info():
    '''
    @调试函数  返回当前函数所在文件名，函数行及行号
    '''
    try:
        raise Exception
    except:
        f = sys.exc_info()[2].tb_frame.f_back
    return (f.f_code.co_filename,f.f_code.co_name, f.f_lineno)

def page_list_return(total, current=1):
    """
    page
    分页，返回本次分页的最小页数到最大页数列表
    """
    min_page = current - 2 if current - 4 > 0 else 1
    max_page = min_page + 4 if min_page + 4 < total else total

    return range(min_page, max_page + 1)


def pages(post_objects, request):
    """
    page public function , return page's object tuple
    分页公用函数，返回分页的对象元组
    """
    paginator = Paginator(post_objects, 10)
    try:
        current_page = int(request.GET.get('page', '1'))
    except ValueError:
        current_page = 1

    page_range = page_list_return(len(paginator.page_range), current_page)

    try:
        page_objects = paginator.page(current_page)
    except (EmptyPage, InvalidPage):
        page_objects = paginator.page(paginator.num_pages)

    if current_page >= 5:
        show_first = 1
    else:
        show_first = 0

    if current_page <= (len(paginator.page_range) - 3):
        show_end = 1
    else:
        show_end = 0

    # 所有对象， 分页器， 本页对象， 所有页码， 本页页码，是否显示第一页，是否显示最后一页
    return post_objects, paginator, page_objects, page_range, current_page, show_first, show_end


def convert_bytes(n):
    """
    @byte智能转换  返回转换后的单位
    """
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n

def convert_to_byte(n):
    """
    @单位智能转换  返回转换后的byte
    """
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if s == n[-1]:
            value = float(n[:-1])*prefix[s]
            return value
    
def defend_attack(func):
    def _deco(request, *args, **kwargs):
        if int(request.session.get('visit', 1)) > 10:
            logger.debug('请求次数: %s' % request.session.get('visit', 1))
            return HttpResponse('Forbidden', status=403)
        request.session['visit'] = request.session.get('visit', 1) + 1
        request.session.set_expiry(300)
        return func(request, *args, **kwargs)
    return _deco
    
    
def require_role(role='user'):
    """
    decorator for require user role in ["super", "admin", "user"]
    要求用户是某种角色 ["super", "admin", "user"]的装饰器
    """

    def _deco(func):
        def __deco(request, *args, **kwargs):
            request.session['pre_url'] = request.path
            if not request.user.is_authenticated():
                return HttpResponseRedirect(reverse('login'))
            return func(request, *args, **kwargs)
        return __deco

    return _deco