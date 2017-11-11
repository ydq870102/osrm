from django.db import models,connection
from django.template.defaultfilters import default
from string import upper

# Create your models here.


class   host (models.Model):
    
    related_system_cn   = models.CharField(max_length=20,default='')
    label_cn            = models.CharField(max_length=100)
    alias               = models.CharField(max_length=100)
    ipaddr              = models.CharField(max_length=20)
    private_ipaddr      = models.CharField(max_length=20,default='')
    os_version          = models.CharField(max_length=20)
    vendor              = models.CharField(max_length=20)
    cuid                = models.CharField(max_length=100,primary_key=True)
    create_time         = models.DateTimeField(auto_now_add=True)
    last_modify_time    = models.DateTimeField(auto_now=True)
    

class   process(models.Model):
    
    user_name           = models.CharField(max_length=20)
    related_system_cn   = models.CharField(max_length=20)
    label_cn            = models.CharField(max_length=100)
    alias               = models.CharField(max_length=100)
    related_host_cuid   = models.ForeignKey(host)
    related_group_cuid  = models.CharField(max_length=100)
    path                = models.CharField(max_length=100)
    restart_command     = models.CharField(max_length=100)
    url_path            = models.CharField(max_length=100)
    middleware_type     = models.CharField(max_length=20)
    process_type        = models.CharField(max_length=100)
    cuid                = models.CharField(max_length=100,primary_key=True)
    create_time         = models.DateTimeField(auto_now_add=True)
    last_modify_time    = models.DateTimeField(auto_now=True)
    is_restart          = models.IntegerField(default=0)
    
class database(models.Model):
    
    label_cn            = models.CharField(max_length=88)
    ipaddr              = models.CharField(max_length=88)
    port                = models.CharField(max_length=88)
    sid                 = models.CharField(max_length=88)
    service_name        = models.CharField(max_length=88)
    user_name           = models.CharField(max_length=88)
    passwd              = models.CharField(max_length=88)
    related_host_cuid   = models.ForeignKey(host)
    cuid                = models.CharField(max_length=100,primary_key=True)
    create_time         = models.DateTimeField(auto_now_add=True)
    
    
class   current_cpu (models.Model):
    
    related_host_cuid   = models.ForeignKey(host)
    cuid                = models.CharField(max_length=100,primary_key=True)
    physics_cpu_num     = models.IntegerField()
    logical_cpu_num     = models.IntegerField()
    cpu_user            = models.CharField(max_length=20)
    cpu_system          = models.CharField(max_length=20)
    cpu_iowait          = models.CharField(max_length=20)
    cpu_idle            = models.CharField(max_length=20)
    collect_time        = models.DateTimeField()
    create_time         = models.DateTimeField(auto_now_add=True)
    
    
class   current_disk(models.Model):
    
    related_host_cuid   = models.ForeignKey(host)
    cuid                = models.CharField(max_length=100,primary_key=True)
    device_name         = models.CharField(max_length=100)
    mount_point         = models.CharField(max_length=100)
    device_total        = models.CharField(max_length=20)
    device_used         = models.CharField(max_length=20)
    device_free         = models.CharField(max_length=20)
    device_percent      = models.CharField(max_length=20)
    collect_time        = models.DateTimeField()
    create_time         = models.DateTimeField(auto_now_add=True)
    
    
class   current_memory(models.Model):
    
    related_host_cuid   = models.ForeignKey(host)
    cuid                = models.CharField(max_length=100,primary_key=True)
    memory_total        = models.CharField(max_length=20)
    memory_used         = models.CharField(max_length=20)
    memory_free         = models.CharField(max_length=20)
    memory_available    = models.CharField(max_length=20)
    memory_percent      = models.CharField(max_length=20)
    swap_total          = models.CharField(max_length=20)
    swap_used           = models.CharField(max_length=20)
    swap_free           = models.CharField(max_length=20)
    swap_percent        = models.CharField(max_length=20)
    collect_time        = models.DateTimeField()
    create_time         = models.DateTimeField(auto_now_add=True)

class   current_process(models.Model):
    
    related_host_cuid   = models.ForeignKey(host)
    related_process_cuid= models.CharField(max_length=50)
    cuid                = models.CharField(max_length=100,primary_key=True)
    username            = models.CharField(max_length=50)
    num_threads         = models.IntegerField()
    name                = models.CharField(max_length=50)
    cpu_percent         = models.CharField(max_length=20)
    pid                 = models.IntegerField()
    tcp_connections_num = models.IntegerField()
    process_create_time = models.DateTimeField()
    cwd                 = models.CharField(max_length=255)
    mem_rss             = models.CharField(max_length=50)
    mem_vms             = models.CharField(max_length=50)             
    mem_uss             = models.CharField(max_length=50)
    mem_pss             = models.CharField(max_length=50)
    mem_swap            = models.CharField(max_length=50)
    collect_time        = models.DateTimeField()
    create_time         = models.DateTimeField(auto_now_add=True)
    

class   his_cpu (models.Model):
    
    related_host_cuid   = models.ForeignKey(host)
    cuid                = models.CharField(max_length=100,primary_key=True)
    physics_cpu_num     = models.IntegerField()
    logical_cpu_num     = models.IntegerField()
    cpu_user            = models.CharField(max_length=20)
    cpu_system          = models.CharField(max_length=20)
    cpu_iowait          = models.CharField(max_length=20)
    cpu_idle            = models.CharField(max_length=20)
    collect_time        = models.DateTimeField()
    create_time         = models.DateTimeField(auto_now_add=True)
    
    
class   his_disk(models.Model):
    
    related_host_cuid   = models.ForeignKey(host)
    cuid                = models.CharField(max_length=100,primary_key=True)
    device_name         = models.CharField(max_length=100)
    mount_point         = models.CharField(max_length=100)
    device_total        = models.CharField(max_length=20)
    device_used         = models.CharField(max_length=20)
    device_free         = models.CharField(max_length=20)
    device_percent      = models.CharField(max_length=20)
    collect_time        = models.DateTimeField()
    create_time         = models.DateTimeField(auto_now_add=True)
    
    
class   his_memory(models.Model):
    
    related_host_cuid   = models.ForeignKey(host)
    cuid                = models.CharField(max_length=100,primary_key=True)
    memory_total        = models.CharField(max_length=20)
    memory_used         = models.CharField(max_length=20)
    memory_free         = models.CharField(max_length=20)
    memory_available    = models.CharField(max_length=20)
    memory_percent      = models.CharField(max_length=20)
    swap_total          = models.CharField(max_length=20)
    swap_used           = models.CharField(max_length=20)
    swap_free           = models.CharField(max_length=20)
    swap_percent        = models.CharField(max_length=20)
    collect_time        = models.DateTimeField()
    create_time         = models.DateTimeField(auto_now_add=True)

class   his_process(models.Model):
    
    related_host_cuid   = models.ForeignKey(host)
    related_process_cuid= models.CharField(max_length=50)
    cuid                = models.CharField(max_length=100,primary_key=True)
    username            = models.CharField(max_length=50)
    num_threads         = models.IntegerField()
    name                = models.CharField(max_length=50)
    cpu_percent         = models.CharField(max_length=20)
    pid                 = models.IntegerField()
    tcp_connections_num = models.IntegerField()
    process_create_time = models.DateTimeField()
    cwd                 = models.CharField(max_length=255)
    mem_rss             = models.CharField(max_length=50)
    mem_vms             = models.CharField(max_length=50)             
    mem_uss             = models.CharField(max_length=50)
    mem_pss             = models.CharField(max_length=50)
    mem_swap            = models.CharField(max_length=50)
    collect_time        = models.DateTimeField()
    create_time         = models.DateTimeField(auto_now_add=True)
    
    
class monitor_opt(models.Model):
    
    cuid                = models.CharField(max_length=100,primary_key=True)
    monitor_type        = models.CharField(max_length=50) 
    monitor_alarm_value = models.CharField(max_length=50)  
    comment             = models.CharField(max_length=512)
    create_time         = models.DateTimeField(auto_now_add=True)
    last_modify_time    = models.DateTimeField(auto_now=True)
    
    
class   alarm(models.Model):
    
    related_system_cn   = models.CharField(max_length=20,default='')
    ip                  = models.CharField(max_length=20)
    related_object_cuid = models.CharField(max_length=50)
    related_monitor_cuid= models.CharField(max_length=50)
    alarm_tag           = models.CharField(max_length=100)
    alarm_title         = models.CharField(max_length=50)
    eventid             = models.CharField(max_length=50)
    alarm_level         = models.IntegerField()
    cuid                = models.CharField(max_length=100,primary_key=True)
    alarm_time          = models.DateTimeField()
    alarm_content       = models.CharField(max_length=1000)
    send_detail         = models.CharField(max_length=2000,default='')
    alarm_num           = models.IntegerField(default=1)
    is_send             = models.IntegerField(default=0)
    create_time         = models.DateTimeField(auto_now_add=True)
    last_modify_time    = models.DateTimeField(auto_now=True)
    is_auto_restart     = models.IntegerField(default=0)
    

    
class   his_alarm(models.Model):
    
    related_system_cn   = models.CharField(max_length=80,default='')
    ip                  = models.CharField(max_length=20)
    related_object_cuid = models.CharField(max_length=50)
    related_monitor_cuid= models.CharField(max_length=50)
    alarm_tag           = models.CharField(max_length=20)
    alarm_title         = models.CharField(max_length=50)
    eventid             = models.CharField(max_length=50)
    alarm_level         = models.IntegerField()
    cuid                = models.CharField(max_length=100,primary_key=True)
    alarm_time          = models.DateTimeField()
    alarm_content       = models.CharField(max_length=1000)
    send_detail         = models.CharField(max_length=2000,default='')
    alarm_num           = models.IntegerField(default=1)
    is_send             = models.IntegerField(default=0)
    create_time         = models.DateTimeField(auto_now_add=True)
    last_modify_time    = models.DateTimeField(auto_now=True)
    is_auto_restart     = models.IntegerField(default=0)
    
    
class   sys_jobs(models.Model):
    
    cuid                = models.CharField(max_length=100,primary_key=True)
    label_cn            = models.CharField(max_length=1000)
    cron                = models.CharField(max_length=100)
    remark              = models.CharField(max_length=100)
    active              = models.CharField(max_length=100)
    create_time         = models.DateTimeField(auto_now_add=True)
    last_modify_time    = models.DateTimeField(auto_now=True)
    
class   monitor_value(models.Model):
    
    monitor_type        = models.CharField(max_length=100)
    monitor_value       = models.CharField(max_length=100)
    cuid                = models.CharField(primary_key=True,max_length=100)
    create_time         = models.DateTimeField(auto_now_add=True)
    last_modify_time    = models.DateTimeField(auto_now=True)
    
    
class monitor(models.Model):
    
    cuid                = models.CharField(max_length=100,primary_key=True)
    monitor_object      = models.CharField(max_length=50)
    monitor_type        = models.CharField(max_length=50)
    monitor_level       = models.IntegerField(default=4)
    is_send             = models.IntegerField(default=0)
    monitor_alarm_type  = models.ForeignKey(monitor_value,default='')
    create_time         = models.DateTimeField(auto_now_add=True)
    last_modify_time    = models.DateTimeField(auto_now=True)
    
    
def get_cuid (table_name):
    cursor = connection.cursor()
    sql="SELECT '%s-'||sys_guid() FROM DUAL"%(upper(table_name))
    cursor.execute(sql)
    return   cursor.fetchone()[0]
    
