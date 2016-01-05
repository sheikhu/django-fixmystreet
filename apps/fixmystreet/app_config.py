from django.apps import AppConfig

class FixmystreetConfig(AppConfig):
    name = 'apps.fixmystreet'
    verbose_name = u'Fixmystreet'

    def ready(self):
        import signals
