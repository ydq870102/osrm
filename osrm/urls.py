"""osrm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import url,include
from django.contrib import admin
from osrm import settings
from django.conf.urls.static import static
import views

urlpatterns = [
    url(r'^admin/', admin.site.urls,name='admin'),
    url(r'^reveiver/', include('cm.urls')),
    url(r'^osrm/login/$', views.Login,name='login'),
    url(r'^osrm/logout/$', views.Logout,name='logout'),
    url(r'^osrm/index/$', views.index,name ='index'),
    url(r'^osrm/process/$', views.process_list,name ='process_list'),
    url(r'^osrm/process/process_del/$', views.process_del,name='process_del'),
    url(r'^osrm/process/process_add/$', views.process_add,name='process_add'),
    url(r'^osrm/process/process_edit/$', views.process_edit,name='process_edit'),
    url(r'^osrm/process/process_detail/$', views.process_detail,name='process_detail'),
    url(r'^osrm/host/$', views.asset,name='asset'),
    url(r'^osrm/host/host_del/$', views.asset_del,name='asset_del'),
    url(r'^osrm/host/host_add/$', views.asset_add,name='asset_add'),
    url(r'^osrm/host/host_edit/$', views.asset_edit,name='asset_edit'),
    url(r'^osrm/host/host_detail/$', views.asset_detail,name='asset_detail'),
    url(r'^osrm/host/host_perfor/$', views.asset_perfor,name='asset_perfor'),
    url(r'^osrm/database/$', views.database_list),
    url(r'^osrm/database/database_del/$', views.database_del,name='database_del'),
    url(r'^osrm/database/database_add/$', views.database_add,name='database_add'),
    url(r'^osrm/database/database_edit/$', views.database_edit,name='database_edit'),
    url(r'^osrm/database/database_detail/$', views.asset_detail,name='database_detail'),
    url(r'^osrm/monitor/$', views.monitor_list),
    url(r'^osrm/monitor/monitor_del/$', views.monitor_del,name='monitor_del'),
    url(r'^osrm/monitor/monitor_add/$', views.monitor_add,name='monitor_add'),
    url(r'^osrm/monitor/monitor_edit/$', views.monitor_edit,name='monitor_edit'),
    url(r'^osrm/alarm/$', views.alarm_list),
    url(r'^osrm/alarm/alarm_detail/$', views.alarm_detail,name='alarm_detail'),
]


handler404 = views.page_not_found
handler500 = views.page_error