from __future__ import unicode_literals

from django.apps import AppConfig


class FilemanageConfig(AppConfig):
    name = 'nuesoft-system.filemanage'
    verbose_name = 'filemanage'

    def ready(self):
        """Override this to put in:
            Users system checks
            Users signal registration
        """
        pass
