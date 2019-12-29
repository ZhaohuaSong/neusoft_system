#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls import url

from views import HostList, ApplicationJson, ItemsList, ItemsJson, ChartShow
from views_analysis import AnalysisList, AnalysisJson, TrafficDataList, TrafficDataJson, TabPageDataJson
from views_clientgroup_port import ClientGroupPortList, ClientGroupPortJson, CreateClientGroupPort, EditClientGroupPort, delete_clientgroup_port
from views_clientinterfacemgr import ClientInterfaceMgrList, ClientInterfaceMgrJson, CreateClientInterfaceMgr
from views_cpu_chartshow import CpuChartshowList, CpuList, CpuJson
from views_interface_charshow import InterfacechartshowList
from views_network_cost import NetworkCostList, NetworkCostJson
from views_network_interface import NetworkInterfaceList, NetworkInterfaceJson,CreateNetworkInterface, set_allnetworkinterface_db, delete_networkinterface
from views_network_interface_group import NetworkInterfaceGroupList, NetworkInterfaceGroupJson, \
    CreateNetworkInterfaceGroup, EditNetworkInterfaceGroup, delete_networkinterfacegroup
from views_sheets_actual import SheetsActualList, SheetsActualJson
from views_sheets_manager import SheetsManagerList, SheetsManagerJason
from views_traffic_analysis import TrafficAnalysisList, TrafficAnalysisJson, traffic_analysis_treeview
from views_today_analysis import NowdayAnalysisList, NowdayAnalysisJson, NowdayTabPageDataJson, NowdayTrafficDataList, NowdayTrafficDataJson
from views_autoping import AutoPing
from views_diamgr import DeviceDialingList, DeviceDialingJson, CreateDeviceDialing, EditDeviceDialing, delete_devicedialing, DialingTest
from home_page.views_traffic_chartshow import OutTrafficChartshow

urlpatterns = [
    #主页
    url(r'^zabbixmgr/outtrafficchartshow$', OutTrafficChartshow.as_view(), name='outtrafficchartshow.list'),  # 主页图表

    #zabbix监控
    url(r'^zabbixmgr/host/list/\d+$', HostList.as_view(), name='host.list'),  # 设备显示列表
    url(r'^zabbixmgr/application/data/$', ApplicationJson.as_view(), name='application.data'),  # 获取数据
    url(r'^zabbixmgr/items/list/(?P<pk>\d+)/$', ItemsList.as_view(), name='items.list'), #应用显示列表
    url(r'^zabbixmgr/items/data/$', ItemsJson.as_view(), name='items.data'),  # 获取数据

    #zabbix图表
    url(r'^zabbixmgr/chart/show/(?P<pk>\d+)\/\d+/$', ChartShow.as_view(), name='chart.show'),  # 图表展示

    #分组管理
    url(r'^zabbixmgr/networkinterfacegroup/list/\d+$', NetworkInterfaceGroupList.as_view(), name='networkinterfacegroup.list'),  # 设备显示列表
    url(r'^zabbixmgr/networkinterfacegroup/data/$', NetworkInterfaceGroupJson.as_view(), name='networkinterfacegroup.data'),  # 获取数据
    url(r'^zabbixmgr/networkinterfacegroup/add/$', CreateNetworkInterfaceGroup.as_view(), name='networkinterfacegroup.add'),  # 添加数据
    url(r'^zabbixmgr/networkinterfacegroup/edit/(?P<pk>\d+)/$', EditNetworkInterfaceGroup.as_view(), name='networkinterfacegroup.edit'), #编辑
    url(r'^zabbixmgr/networkinterfacegroup/delete/$', delete_networkinterfacegroup, name='networkinterfacegroup.delete'),  # 删除

    #网络接口管理
    url(r'^zabbixmgr/networkinterface/list/\d+$', NetworkInterfaceList.as_view(), name='networkinterface.list'),  # 设备显示列表
    url(r'^zabbixmgr/networkinterface/data/$', NetworkInterfaceJson.as_view(), name='networkinterface.data'),  # 获取数据
    url(r'^zabbixmgr/networkinterface/add/$', CreateNetworkInterface.as_view(), name='networkinterface.add'),  # 添加数据
    url(r'^zabbixmgr/allnetworkinterface/set/$', set_allnetworkinterface_db, name='allnetworkinterface.set'), #重置端口表单
    url(r'^zabbixmgr/networkinterface/delete/$', delete_networkinterface, name='networkinterface.delete'),  # 删除

    #流量组图表
    url(r'^zabbixmgr/interfacechartshow/list\/\d+\/\d+/\d+$', InterfacechartshowList.as_view(), name='interfacechartshow.list'),  # 设备显示列表

    #cpu负载图表
    url(r'^zabbixmgr/cpuchartshow/list/\d+$', CpuChartshowList.as_view(), name='cpuchartshow.list'),  # cpu负载显图表
    url(r'^zabbixmgr/cpuchartshow/list/(?P<pk>\d+)/$', CpuList.as_view(), name='cpu.list'), #cpu负载列表
    url(r'^zabbixmgr/cpu/data/$', CpuJson.as_view(), name='cpu.data'),  # 获取数据

    #客户管理
    url(r'^zabbixmgr/clientinterfacemgr/list$', ClientInterfaceMgrList.as_view(), name='clientinterfacemgr.list'),  # 客户列表
    url(r'^zabbixmgr/clientinterfacemgr/data/$', ClientInterfaceMgrJson.as_view(), name='clientinterfacemgr.data'),  # 获取数据
    url(r'^zabbixmgr/clientinterfacemgr/add/$', CreateClientInterfaceMgr.as_view(), name='clientinterfacemgr.add'),  # 获取数据

    #客户端口管理
    url(r'^zabbixmgr/clientgroupport/list$', ClientGroupPortList.as_view(), name='clientgroupport.list'),  # 客户端口列表
    url(r'^zabbixmgr/clientgroupport/data/$', ClientGroupPortJson.as_view(), name='clientgroupport.data'),  # 获取数据
    url(r'^zabbixmgr/clientgroupport/add/$', CreateClientGroupPort.as_view(), name='clientgroupport.add'),  # 获取数据
    url(r'^zabbixmgr/clientgroupport/edit/(?P<pk>\d+)/$', EditClientGroupPort.as_view(), name='clientgroupport.edit'), #编辑
    url(r'^zabbixmgr/clientgroupport/delete/$', delete_clientgroup_port, name='clientgroupport.delete'),  # 删除

    #报表管理
    url(r'^zabbixmgr/sheetsmanager/list$', SheetsManagerList.as_view(), name='sheetsmanager.list'),  # 流量日报列表
    url(r'^zabbixmgr/sheetsmanager/data/$', SheetsManagerJason.as_view(), name='sheetsmanager.data'),  # 获取数据

    #实时数据表
    url(r'^zabbixmgr/sheetsactual/list$', SheetsActualList.as_view(), name='sheetsactual.list'),  # 实时数据列表
    url(r'^zabbixmgr/sheetsactual/data/$', SheetsActualJson.as_view(), name='sheetsactual.data'),  # 获取数据

    #基础流量分析
    url(r'^zabbixmgr/trafficanalysis/list/$', TrafficAnalysisList.as_view(), name='trafficanalysis.list'),  # 流量分析（闲置）
    url(r'^zabbixmgr/trafficanalysis/data/$', TrafficAnalysisJson.as_view(), name='trafficanalysis.data'),  # 获取数据(默认或自定义查询共有方法)
    url(r'^zabbixmgr/trafficanalysis/treeview', traffic_analysis_treeview, name='trafficanalysis.treeview'),  # 树状列表（闲置)

    #基础流量分析二
    url(r'^zabbixmgr/analysis/list/\d+$', AnalysisList.as_view(), name='analysis.list'),  # 流量分析(默认某客户)
    url(r'^zabbixmgr/analysis/data/(?P<industry_id>\d+)$', AnalysisJson.as_view(), name='analysis.data'),  # 获取数据(默认某客户)
    url(r'^zabbixmgr/trafficdata/list/\d+\/\w+\/\d+\/\d+\/\d+/\d+$', TrafficDataList.as_view(), name='trafficdata.list'),  # 流量分析(自定义查询）
    url(r'^zabbixmgr/trafficdata/data/(?P<industry_id>\d+)$', TrafficDataJson.as_view(), name='trafficdata.data'),  # 获取数据（自定义查询）

    #tab页
    url(r'^zabbixmgr/tabpagedata/data/$', TabPageDataJson.as_view(), name='tabpagedata.data'),  # 获取tab页数据

    #95流量计费
    url(r'^zabbixmgr/networkcost/list/\d+$', NetworkCostList.as_view(), name='networkcost.list'),  # 客户端口列表
    url(r'^zabbixmgr/networkcost/data/(?P<industry_id>\d+)$', NetworkCostJson.as_view(), name='networkcost.data'),  # 获取数据

    #当天流量分析
    url(r'^zabbixmgr/nowdayanalysis/list/\d+$', NowdayAnalysisList.as_view(), name='nowdayanalysis.list'),  # 当天流量分析(默认某客户)
    url(r'^zabbixmgr/nowdayanalysis/data/(?P<industry_id>\d+)$', NowdayAnalysisJson.as_view(), name='nowdayanalysis.data'),  # 获取当天数据(默认某客户)
    url(r'^zabbixmgr/nowdaytrafficdata/list/\d+\/\w+\/\d+\/\d+\/\d+/\d+$', NowdayTrafficDataList.as_view(), name='nowdaytrafficdata.list'),  # 流量分析(自定义查询）
    url(r'^zabbixmgr/nowdaytrafficdata/data/(?P<industry_id>\d+)$', NowdayTrafficDataJson.as_view(), name='nowdaytrafficdata.data'),  # 获取数据（自定义查询）

    #当天tab页
    url(r'^zabbixmgr/nowdaytabpagedata/data/$', NowdayTabPageDataJson.as_view(), name='nowdaytabpagedata.data'),  # 获取tab页数据

    #拨测

    url(r'^dialing/autoping/list/\d+$', AutoPing.as_view(), name='autoping.list'),  # 自动拨测

    url(r'^zabbixmgr/devicedialing/list/\d+$', DeviceDialingList.as_view(), name='devicedialing.list'),  # 显示列表
    url(r'^zabbixmgr/devicedialing/data/$', DeviceDialingJson.as_view(), name='devicedialing.data'),  # 获取数据
    url(r'^zabbixmgr/devicedialing/add/$', CreateDeviceDialing.as_view(), name='devicedialing.add'),  # 添加
    url(r'^zabbixmgr/devicedialing/edit/(?P<pk>\d+)/$', EditDeviceDialing.as_view(), name='devicedialing.edit'),  # 编辑
    url(r'^zabbixmgr/devicedialing/delete/$', delete_devicedialing, name='devicedialing.delete'),  # 删除

    url(r'^zabbixmgr/devicedialing/list/dialingtest/(?P<pk>\d+)$', DialingTest.as_view(), name='devicedialing.test'),  # 编辑
]
