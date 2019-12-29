# from __future__ import unicode_literals

from django.apps import AppConfig


class ZabbixmgrConfig(AppConfig):
    name = 'nuesoft-system.zabbixmgr'
    verbose_name = 'zabbixmgr'

    def ready(self):
        """Override this to put in:
            Users system checks
            Users signal registration
        """
        pass
