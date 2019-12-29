from django.apps import AppConfig


class SysadminConfig(AppConfig):
    name = 'nuesoft-system.sysadmin'
    verbose_name = "sysadmin"

    def ready(self):
        """Override this to put in:
            Users system checks
            Users signal registration
        """
        pass
