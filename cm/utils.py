#!/usr/bin/env python
# encoding: utf-8

from osrm.api import get_object,set_log,get_cur_info, get_any_object
import cm_api
from cm.models import * 
from osrm.settings import *
import logging
import datetime
from xml.dom.minidom import Document
import traceback
import time



logger = logging.getLogger('django')


class  ResObj(object):
    
    def __init__(self,data):
        '''
        @资源采集对象初始化
        '''
        
        self.Process_Info = data.get('ProcessPlugin',None)
        self.Disk_Info = data.get('DiskPlugin',None)
        self.Memory_Info = data.get('MemoryPlugin',None)
        self.Cpu_Info = data.get('CpuPlugin',None)
        self.Host_info = data.get('host',None)
        self.collect_time = data.get('collect_time',None)
        self.host = get_object(host,ipaddr=self.Host_info)
        self.alarm_object = Hard_AmObj()

    def dict_format(self,model,**dict):
        '''
        @字典格式化函数 添加数据库中必要字段：
        '''        
        dict['cuid'] =get_cuid(model)
        dict['collect_time'] = self.collect_time
        dict['related_host_cuid'] =self.host
        return  dict

    def disk_parse(self,):
        '''
        @硬盘解析函数 数据样例：
        {u'E:\\': {u'device_total': u'205.1G', u'device_percent': 92.9, u'mount_point': u'E:\\', u'device_name': u'E:\\', u'device_free': u'14.5G', u'device_used': u'190.6G'}, u'D:\\': {u'device_total': u'214.8G', u'device_percent': 93.8, u'mount_point': u'D:\\', u'device_name': u'D:\\', u'device_free': u'13.4G', u'device_used': u'201.4G'}, u'C:\\': {u'device_total': u'48.8G', u'device_percent': 90.8, u'mount_point': u'C:\\', u'device_name': u'C:\\', u'device_free': u'4.5G', u'device_used': u'44.3G'}, u'F:\\': {u'device_total': u'214.9G', u'device_percent': 90.7, u'mount_point': u'F:\\', u'device_name': u'F:\\', u'device_free'[07/Dec/2016 11:34:40] "POST /reveiver/server/ HTTP/1.1" 200 2: u'20.0G', u'device_used': u'195.0G'}}
        '''
        try:
            logger.debug('开始入库硬盘采集数据')
            his_disk_data = self.host.current_disk_set.all()
            his_disk.objects.bulk_create(his_disk_data)
            his_disk_data.delete()
            for value in  self.Disk_Info.values():
                value = self.dict_format('current_disk',**value)
                current_disk(**value).save()
                logger.debug('硬盘采集数据入库成功,THE END')
                self.alarm_object.disk_am_parse(value)
        except Exception,e:
            logger.error(traceback.format_exc())
            
    
    def process_parse(self,):
        '''
        @进程解析函数 数据样例：
        {u'2596': {u'username': u'ydq-PC\\ydq', u'num_threads': 10, u'name': u'taskhost.exe', u'cpu_percent': 0.0, u'pid': 2596, u'tcp_connections_num': 0, u'mem_uss': u'3.5M', u'mem_vms': u'8.2M', u'mem_rss': u'11.8M', u'cwd': u'C:\\Windows\\system32', u'process_create_time': 1481159550.0}}
        '''
        try:
            logger.debug('开始入库进程采集数据')
            his_process_data = self.host.current_process_set.all()
            his_process.objects.bulk_create(his_process_data)
            his_process_data.delete()
            for value in  self.Process_Info.values():
                value = self.process_match(**value)
                value = self.dict_format('current_process',**value)
                value = current_process(**value).save()
            logger.debug('进程采集数据入库成功,THE END')
        except Exception,e:
            logger.error(traceback.format_exc())
            
    
    def process_match(self,**data):
        '''
        @进程匹配函数 根据采集的进程信息和监控进程表的自动对比，返回监控进程表的CUID：
        '''
        try:
            data['related_process_cuid'] = process.objects.filter(path=data['cwd'])[0].cuid
        except Exception,e:
            data['related_process_cuid'] = ''
        finally:
            return data
                
        
    
    def memory_parse(self,):
        '''
        @CPU解析函数 数据样例：
        {u'memory_used': u'5.9G', u'swap_used': u'6.2G', u'memory_free': u'2.0G', u'swap_free': u'9.6G', u'swap_total': u'15.8G', u'memory_available': u'2.0G', u'memory_total': u'7.9G', u'memory_percent': 74.8, u'swap_percent': 39.1}
        '''
        try:
            logger.debug('开始入库内存采集数据')
            his_memory_data = self.host.current_memory_set.all()
            his_memory.objects.bulk_create(his_memory_data)
            his_memory_data.delete()
            self.Memory_Info = self.dict_format('current_memory',**self.Memory_Info)
            value = current_memory(**self.Memory_Info).save()
            logger.debug('内存采集数据入库成功,THE END')
            self.alarm_object.memory_am_parse(self.Memory_Info)
        except Exception,e:
            logger.error(traceback.format_exc())
            

    
    def cpu_parse(self,):
        '''
        @CPU解析函数 数据样例：
        {u'cpu_iowait': 0, u'physics_cpu_num': 2, u'cpu_idle': 82.6, u'logical_cpu_num': 4, u'cpu_user': 3.2, u'cpu_system': 13.9}
        '''
        try:
            logger.debug('开始入库CPU采集数据')
            his_cpu_data = self.host.current_cpu_set.all()
            his_cpu.objects.bulk_create(his_cpu_data)
            his_cpu_data.delete()
            self.Cpu_Info = self.dict_format('current_cpu',**self.Cpu_Info)
            value = current_cpu(**self.Cpu_Info).save()
            logger.debug('cpu采集数据入库成功,THE END')
            self.alarm_object.cpu_am_parse(self.Cpu_Info)
        except Exception,e:
            logger.error(traceback.format_exc())
            
            
    def execute(self):
        '''
        @执行函数 执行所有解析函数
        '''

        self.disk_parse()
        self.memory_parse()
        self.cpu_parse()
        
    
class MonitorObj(object):
    
    def __init__(self):
        '''
        @监控对象初始化
        '''
        self.ping_list = get_any_object(monitor,monitor_type='PING')
        self.proccesses = get_any_object(monitor,monitor_type='PROCESS')
        self.mview_list = get_any_object(monitor,monitor_type='MVIEW')
        self.job_list = get_any_object(monitor,monitor_type='JOB')
        self.alarm_object = Soft_AmObj()
        
        
    def ping_parse(self):
        '''
        @PING测主机监控方法
        '''
        try:
            logger.debug('开始PING测所有主机列表')
            for host_list in self.ping_list:
                value ={}
                hostobj = get_object(host,cuid=host_list.monitor_object)
                result = cm_api.check_host(hostobj.ipaddr)
                value['related_host_cuid'] = hostobj
                value['result'] = result
                value['collect_time'] =time.strftime(ISOTIMEFORMAT, time.localtime(time.time()))
                self.alarm_object.ping_am_parse(value)
            logger.debug('主机PING测结束,THE END!')    
        except Exception,e:
            logger.error(traceback.format_exc())    
    
    def process_parse(self):
        '''
        @进程URL和PID监控方法
        '''
        try:
            logger.debug('开始检测进程PID和URL')
            for process_list in self.proccesses:
                processobj = get_object(process,cuid=process_list.monitor_object)
                value = {}
                if processobj.url_path:
                    url_result = cm_api.check_url(processobj.url_path)
                else:
                    url_result = 0
                pid = get_any_object(current_process,related_process_cuid=process_list.monitor_object)
                if  pid :
                    pid_result = 0
                else :
                    pid_result = 1
                value['related_host_cuid'] = processobj.related_host_cuid
                value['pid_result'] = pid_result
                value['url_result'] = url_result
                value['collect_time'] =time.strftime(ISOTIMEFORMAT, time.localtime(time.time()))
                value['process'] = processobj
                self.alarm_object.process_am_parse(value)
            logger.debug('进程PID和URL检测结束,THE END!')    
        except Exception,e:
            logger.error(traceback.format_exc())     

            
    
    def oracle_jobs_parse(self):
        '''
        @数据库JOB监控方法
        '''
        pass
    
    def oracle_mviews_parse(self):
        '''
        @数据库物化视图刷新监控方法
        '''
        logger.debug('开始物化视图刷新状态监测')
        for mview in self.mview_list:
            value = {}
            database_info = get_object(database,cuid=mview.monitor_object)
            value['related_host_cuid'] = database_info.related_host_cuid
            value['database'] = database_info
            value['monitor_object'] = mview
            value['collect_time'] =time.strftime(ISOTIMEFORMAT, time.localtime(time.time()))
            sql = "select mview_name,last_refresh,last_sync_exception from meta_mview where isactive='Y'"
            result_list = cm_api.exec_sql(database_info.user_name,database_info.passwd,database_info.ipaddr,database_info.port,database_info.sid,sql)
            for result in result_list:
                value['mview_name'] = result[0]
                value['last_refresh_time'] = result[1]
                value['last_sync_exception'] = result[2]
                self.alarm_object.mview_am_parse(value)
                
        
    def execute(self):
        '''
        @执行函数 执行所有解析函数
        '''

        self.ping_parse()
        self.process_parse()
        self.oracle_mviews_parse()

        
        
        
        
class AmObj(object):
    
    def __init__(self):
        '''
        @获取告警监控阈值
        '''
        
        self.memory_monitor_opt = get_object(monitor_opt,monitor_type = 'MEMORY')
        self.disk_monitor_opt = get_object(monitor_opt,monitor_type = 'DISK')
        self.cpu_monitor_opt = get_object(monitor_opt,monitor_type = 'CPU')
        self.ping_monitor_opt = get_object(monitor_opt,monitor_type = 'PING')
        self.process_monitor_opt = get_object(monitor_opt,monitor_type = 'PROCESS')
        self.heart_monitor_opt = get_object(monitor_opt,monitor_type = 'HEART')
        
        
    def alarm_insert(self,value):
        '''
        @新增告警方法
        '''
        try:
            send_xml = self.create_alarm_xml(value,'new')
            alarm(       
                         related_system_cn = value['related_host_cuid'].related_system_cn,
                         ip = value['related_host_cuid'].ipaddr,
                         related_object_cuid = value['monitor_object'].monitor_object,
                         related_monitor_cuid = value['monitor_object'].cuid,
                         alarm_tag = value['tag'],
                         alarm_title = value['title'],
                         cuid = value['cuid'],
                         alarm_content = value['content'],
                         alarm_level = value['monitor_object'].monitor_level,
                         eventid = value['monitor_object'].monitor_alarm_type,
                         alarm_time = value['collect_time'],
                         send_detail = send_xml.decode('GB18030')
                 ).save()
            logger.debug('开始发送MQ,发送XML为：%s'%send_xml)
            logger.debug(cm_api.send_mq(send_xml))
            models.alarm.objects.filter(cuid=value['cuid']).update(is_send=1)
        except Exception:
            logger.error(traceback.format_exc())           
    
    def alarm_update(self,value):
        '''
        @更新告警方法
        '''
        try:
            send_xml = self.create_alarm_xml(value,'update')
            value['alarm_object'].update(last_modify_time=value['collect_time'],alarm_num = value['alarm_object'][0].alarm_num + 1,send_detail = send_xml.decode('GB18030'))
            logger.debug('开始发送MQ,发送XML为：%s'%send_xml)
            logger.debug(cm_api.send_mq(send_xml))
            models.alarm.objects.filter(cuid=value['cuid']).update(is_send=1)
        except Exception:
            logger.error(traceback.format_exc())   
    
    def alarm_delete(self,value):
        '''
        @删除告警方法
        '''
        try:
            send_xml = self.create_alarm_xml(value,'delete')
            his_alarm.objects.bulk_create(value['alarm_object'])
            value['alarm_object'].delete()
            logger.debug('开始发送MQ,发送XML为：%s'%send_xml)
            logger.debug(cm_api.send_mq(send_xml))
        except Exception:
            logger.error(traceback.format_exc()) 
            
    def create_alarm_xml(self,value,type):
        '''
        @生成告警XML
        '''
        try:
            value['alarm_action'] = type
            value['eventid'] = value['monitor_object'].monitor_alarm_type.monitor_type
            if type == 'new':
                value['cuid'] = get_cuid('CM_ALARM')
            else :
                value['cuid'] = value['alarm_object'][0].cuid
            send_xml = cm_api.create_Xml(value,)
            return send_xml
        except Exception:
            logger.error(traceback.format_exc()) 
    
class Hard_AmObj(AmObj):
    
    def __init__(self):
        '''
        @获取告警监控阈值
        '''
        AmObj.__init__(self)
        
    def disk_am_parse(self,value):
        '''
        @硬盘告警解析
        
        '''
        try:
            logger.debug('开始硬盘告警解析')
            value['monitor_object'] = get_object(monitor,monitor_object=value['related_host_cuid'].cuid,monitor_type='DISK')
            value['tag'] = value['device_name']
            value['title'] = '硬盘阈值告警'
            if  value['monitor_object'] and self.disk_monitor_opt:
                value['alarm_object'] = alarm.objects.filter(related_monitor_cuid=value['monitor_object'].cuid, alarm_tag=value['tag'])
                if float(value['device_percent']) > float(self.disk_monitor_opt.monitor_alarm_value):
                    value['content'] = '当前磁盘：%s 磁盘利用率:%s%%,产生告警，原因：磁盘利用率大于%s%%' %(value['device_name'].encode('utf-8'),float(value['device_percent']),float(self.cpu_monitor_opt.monitor_alarm_value))
                    if value['alarm_object']:
                        logger.debug('告警已存在，更新告警时间、告警次数')
                        self.alarm_update(value)
                    else:
                        logger.debug('开始新增告警')
                        self.alarm_insert(value)
                else :
                    if value['alarm_object']:
                        logger.debug('告警已消除，删除活动告警')
                        self.alarm_delete(value)
            else :
                logger.debug('主机%s不再管理范围,不进行告警解析'%((value['related_host_cuid'].cuid).encode('utf-8')))
        except Exception,e:
            logger.error(traceback.format_exc())
                            
    def cpu_am_parse(self,value):
        '''
        @CPU告警解析
        
        '''
        try:
            logger.debug('开始CPU告警解析')
            value['monitor_object'] = get_object(monitor,monitor_object=value['related_host_cuid'].cuid,monitor_type='CPU')
            value['tag'] = 'cpu'
            value['title'] = 'CPU阈值告警'
            if  value['monitor_object'] and self.cpu_monitor_opt:
                value['alarm_object'] = alarm.objects.filter(related_monitor_cuid=value['monitor_object'].cuid, alarm_tag=value['tag'])
                if 100-float(value['cpu_idle']) > float(self.cpu_monitor_opt.monitor_alarm_value):
                    value['content'] = '当前CPU利用率:%s%%,产生告警，原因：CPU利用率大于%s%%' %(100-float(value['cpu_idle']),float(self.cpu_monitor_opt.monitor_alarm_value))
                    if value['alarm_object']:
                        logger.error('告警已存在，更新告警时间')
                        self.alarm_update(value)
                    else:
                        logger.error('开始新增告警')
                        self.alarm_insert(value)
                else :
                    if value['alarm_object']:
                        logger.error('告警已消除，删除活动告警')
                        self.alarm_delete(value)
            else :
                logger.debug('主机%s不再管理范围,不进行告警解析'%((value['related_host_cuid'].cuid).encode('utf-8')))
        except Exception,e:
            logger.error(traceback.format_exc())
            
    def memory_am_parse(self,value):
        '''
        @内存告警解析
        
        '''
        try:
            logger.debug('开始内存告警解析')
            value['monitor_object'] = get_object(monitor,monitor_object=value['related_host_cuid'].cuid,monitor_type='MEMORY')
            value['tag'] = 'memory'
            value['title'] = 'MEMORY阈值告警'
            if  value['monitor_object'] and self.memory_monitor_opt:
                value['alarm_object'] = alarm.objects.filter(related_monitor_cuid=value['monitor_object'].cuid, alarm_tag=value['tag'])
                if float(value['memory_percent']) > float(self.cpu_monitor_opt.monitor_alarm_value):
                    value['content'] = '内存利用率:%s%%,产生告警，原因：内存利用率大于%s%%' %(float(value['memory_percent']),float(self.memory_monitor_opt.monitor_alarm_value))
                    if value['alarm_object']:
                        logger.error('告警已存在，更新告警时间')
                        self.alarm_update(value)
                    else:
                        logger.error('开始新增告警')
                        self.alarm_insert(value)
                else :
                    if value['alarm_object']:
                        logger.error('告警已消除，删除活动告警')
                        self.alarm_delete(value)
            else :
                logger.debug('主机%s不再管理范围,不进行告警解析'%((value['related_host_cuid'].cuid).encode('utf-8')))
        except Exception,e:
            logger.error(traceback.format_exc())
        
        
class Soft_AmObj(AmObj):
    
    def __init__(self):
        '''
        @获取告警监控阈值
        '''
        AmObj.__init__(self)
        
    def ping_am_parse(self,value):
        '''
        @主机PING测告警解析
        '''
        
        try:
            logger.debug('开始主机PING测告警解析')
            value['monitor_object'] = get_object(monitor,monitor_object=value['related_host_cuid'].cuid,monitor_type='PING')
            value['tag'] = 'PING'
            value['title'] = 'PING测阈值告警'
            if  value['monitor_object'] and self.ping_monitor_opt:
                value['alarm_object'] = alarm.objects.filter(related_monitor_cuid=value['monitor_object'].cuid, alarm_tag=value['tag'])
                if float(value['result']) > float(self.ping_monitor_opt.monitor_alarm_value):
                    value['content'] = 'PING测主机：%s ,当前丢包率:%s%%,产生告警，原因：ping测丢包率大于%s%%' %(value['related_host_cuid'].ipaddr.encode('utf-8'),float(value['result']),self.ping_monitor_opt.monitor_alarm_value)
                    if value['alarm_object']:
                        logger.debug('告警已存在，更新告警时间')
                        self.alarm_update(value)
                    else:
                        logger.debug('开始新增告警')
                        self.alarm_insert(value)
                else :
                    if value['alarm_object']:
                        logger.debug('告警已消除，删除活动告警')
                        self.alarm_delete(value)
            else :
                logger.debug('主机%s不再管理范围,不进行告警解析'%((value['related_host_cuid'].cuid).encode('utf-8')))
        except Exception,e:
            logger.error(traceback.format_exc())
        
    
    def process_am_parse(self,value):
        '''
        @进程URL和PID告警解析
        '''
        try:
            logger.debug('开始进程告警解析')
            value['monitor_object'] = get_object(monitor,monitor_object=value['process'].cuid,monitor_type='PROCESS')
            value['tag'] = 'PROCESS'
            value['title'] = '进程阈值告警'
            if  value['monitor_object'] and self.process_monitor_opt:
                value['alarm_object'] = alarm.objects.filter(related_monitor_cuid=value['monitor_object'].cuid, alarm_tag=value['tag'])
                if value['url_result'] == 1:
                    value['content'] = '进程：%s 产生告警，原因：进程URL：%s拨测失败' %(value['process'].label_cn.encode('utf-8'),value['process'].url_path.encode('utf-8'))
                    if value['alarm_object']:
                        logger.debug('告警已存在，更新告警时间')
                        self.alarm_update(value)
                    else:
                        logger.debug('开始新增告警')
                        self.alarm_insert(value)
                elif value['pid_result'] == 1:
                    value['content'] = '进程：%s 产生告警，原因：进程PID不存在' %((value['process'].label_cn.encode('utf-8')))
                    if value['alarm_object']:
                        logger.debug('告警已存在，更新告警时间')
                        self.alarm_update(value)
                    else:
                        logger.debug('开始新增告警')
                        self.alarm_insert(value)
                else :
                    if value['alarm_object']:
                        logger.debug('告警已消除，删除活动告警')
                        self.alarm_delete(value)
            else :
                logger.debug('主机%s不再管理范围,不进行告警解析'%((value['related_host_cuid'].cuid).encode('utf-8')))
        except Exception,e:
            logger.error(traceback.format_exc())
    
    
    def mview_am_parse(self,value):
        '''
        @物化视图刷新告警解析
        '''
        try:
            logger.debug('开始物化视图告警解析')
            value['tag'] = value['mview_name']
            value['title'] = '物化视图刷新告警'
            if  value['monitor_object']:
                value['alarm_object'] = alarm.objects.filter(related_monitor_cuid=value['monitor_object'].cuid, alarm_tag=value['tag'])
                if value['last_sync_exception'] != 'N/A':
                    value['content'] = '数据库：%s 用户：%s 物化视图： %s 刷新异常，异常原因：%s,最后一次刷新时间：%s' %(value['database'].label_cn.encode('utf-8'),value['database'].user_name.encode('utf-8'),value['mview_name'],value['last_sync_exception'],value['last_refresh_time'])
                    if value['alarm_object']:
                        logger.debug('告警已存在，更新告警时间')
                        self.alarm_update(value)
                    else:
                        logger.debug('开始新增告警')
                        self.alarm_insert(value)
                else :
                    if value['alarm_object']:
                        logger.debug('告警已消除，删除活动告警')
                        self.alarm_delete(value)
            else :
                logger.debug('主机%s不再管理范围,不进行告警解析'%((value['related_host_cuid'].cuid).encode('utf-8')))
        except Exception,e:
            logger.error(traceback.format_exc())
    
    def client_heart(self):
        
        pass
        
        
        
        
        
        
        
        
        