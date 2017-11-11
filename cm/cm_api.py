# coding: utf-8

import os
import logging
import logging.handlers
from osrm.settings import *
import redis
import time
from xml.dom.minidom import Document
from cm import models
import cm.utils
import subprocess
import cmd
import re
import urllib2
import cx_Oracle
import traceback
try:
    import pymqi
except ImportError:
    pass
    
class RedisHelper:
    '''
    @redis方法
    '''
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


def create_Xml(value,charset='GB18030'):
    '''
    @生成XML方法
    '''
    doc = Document()
    message = doc.createElement('message')
    
    #head 
    head = doc.createElement("head")
    version = doc.createElement("version")
    version.appendChild(doc.createTextNode('1.0'))
    vendor = doc.createElement("vendor")
    vendor.appendChild(doc.createTextNode(value['related_host_cuid'].related_system_cn))
    address = doc.createElement("address")
    address.appendChild(doc.createTextNode(value['related_host_cuid'].ipaddr))
    type = doc.createElement("type")
    type.appendChild(doc.createTextNode('alarm'))
    head.appendChild(version)
    head.appendChild(vendor)
    head.appendChild(address)
    head.appendChild(type)
    message.appendChild(head)
    #alarm 
    alarm = doc.createElement("alarm")
    id = doc.createElement("id")
    id.appendChild(doc.createTextNode(value['cuid']))
    operator = doc.createElement("operator")
    operator.appendChild(doc.createTextNode(value['alarm_action']))
    eventid = doc.createElement("eventid")
    eventid.appendChild(doc.createTextNode(value['eventid']))
    title = doc.createElement("title")
    title.appendChild(doc.createTextNode(value['title'].decode('utf-8')))
    level = doc.createElement("level")
    level.appendChild(doc.createTextNode(str(value['monitor_object'].monitor_level)))
    detail = doc.createElement("detail")
    detail.appendChild(doc.createTextNode(value['content'].decode('utf-8')))
    time = doc.createElement("time")
    time.appendChild(doc.createTextNode(str(value['collect_time'])))
    type = doc.createElement("type")
    type.appendChild(doc.createTextNode('performance'))
    alarm.appendChild(id)
    alarm.appendChild(operator)
    alarm.appendChild(eventid)
    alarm.appendChild(title)
    alarm.appendChild(level)
    alarm.appendChild(detail)
    alarm.appendChild(time)
    alarm.appendChild(type)
    message.appendChild(alarm)
    doc.appendChild(message)

    f = doc.toprettyxml(indent = "", newl = "", encoding = charset)
    return f


def cm_parse(data):
    
    data_obj = cm.utils.ResObj(data)
    data_obj.execute()
    
    monitor_obj = cm.utils.MonitorObj()
    monitor_obj.execute()
    
def check_host(ip,count=4,timeout=3):
    '''
    @PING测主机方法
    '''
    try:
        cmd = 'ping -n %s -w %s %s'%(count,timeout,ip)
        p=subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)
        regex = re.compile(r'\d+%')
        result = regex.findall(p.stdout.read())[0].replace('%','')
        return result
    except Exception:
        return 0

def check_url(url):
    '''
    @检查URL是否能打开方法
    '''
    header={'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language':'zh-CN,zh;q=0.8',
                'User-Agent':'Mozilla/5.0 (Windows NT 5.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.124 Safari/537.36' }
    req = urllib2.Request(url,headers=header) 
    try: 
        urllib2.urlopen(req,data=None, timeout=30)
        result = 0
    except: 
        result = 1
    return  result


def exec_sql(user_name,passwd,ip,port,sid,sql):
    '''
    @连接数据库以及执行SQL方法
    '''
    try:
        tns=cx_Oracle.makedsn(ip,port,sid)
        db=cx_Oracle.connect(user_name,passwd,tns)
        cr=db.cursor()
        cr.execute(sql)
        rs=cr.fetchall() 
        cr.close()
        return  rs
    except Exception:
        return '失败原因：%s'%traceback.format_exc()

def send_mq (xml):
    '''
    @发送MQ方法
    '''
    try:
        #conf = config_all()
        qmgr = pymqi.connect(MQ_MANAGER,MQ_CHANNEL,MQ_IP(MQ_PORT))
        putq = pymqi.Queue(qmgr, MQ_LABEL)
        putq.put(xml)
        return 'MQ发送成功！'
    except Exception:
        return 'MQ发送失败，失败原因：%s'%traceback.format_exc()
    
    
