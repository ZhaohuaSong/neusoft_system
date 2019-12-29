from django.apps import AppConfig


class VanillaConfig(AppConfig):
    name = 'nuesoft-system.vanilla'
    verbose_name = "vanilla"

    def ready(self):
        """Override this to put in:
            Users system checks
            Users signal registration
        """
        pass
