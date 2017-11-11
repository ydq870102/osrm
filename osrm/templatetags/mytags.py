# coding: utf-8

import re
import ast
import time

from django import template
from osrm.api import get_object
from cm.models import *
import re

register = template.Library()


@register.filter(name='get_memory_info')
def templatetags(object):
    """
    int 转换为 str
    """
    memory_info = get_object(current_memory,related_host_cuid=object)
    if memory_info:
        return object.cuid
    else:
        return object.cuid
    
@register.filter(name='convert_monitor_object')   
def convert_monitor_object(monitor_cuid):
    """
    @转换monitor对象
    """
    host_object = get_object(host,cuid=monitor_cuid)
    process_object = get_object(process,cuid=monitor_cuid)
    database_object = get_object(database,cuid=monitor_cuid)
    if host_object:
        return '主机-%s'%host_object.ipaddr.encode('utf-8')
    if process_object:
        return '应用-%s'%process_object.label_cn.encode('utf-8')
    if database_object:
        return '数据库-%s'%database_object.label_cn.encode('utf-8')

@register.filter(name='convert_enum')   
def convert_enum(num):
    """
    @转换monitor对象
    """
    if num == 0 or num is None:
        return '否'
    if num == 1:
        return '是'

@register.filter(name='interpret_ip')   
def interpret_ip(monitor_cuid):
    """
    @转换monitorIP
    """
    host_object = get_object(host,cuid=monitor_cuid)
    process_object = get_object(process,cuid=monitor_cuid)
    database_object = get_object(database,cuid=monitor_cuid)
    if host_object:
        return host_object.ipaddr
    if process_object:
        return process_object.related_host_cuid.ipaddr
    if database_object:
        return database_object.related_host_cuid.ipaddr

@register.filter(name='range')   
def range(value):
    """
    @转换monitorIP
    """
    print range(value)
    return range(value)






