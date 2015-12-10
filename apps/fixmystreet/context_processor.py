
from django.contrib.sites.models import Site
from django.conf import settings


def domain(request):
    site = Site.objects.get_current()
    return {
        'SITE_URL': 'http://{0}'.format(site.domain),
        'URBIS_URL': settings.URBIS_URL,
        'WMS_SERVICE_URL': '{0}geoserver/gwc/service/wms'.format(settings.URBIS_URL),
    }


def environment(request):
    return {
        'APP_VERSION':  settings.VERSION,
        'DEBUG':        settings.DEBUG,
        'ENVIRONMENT':  settings.ENVIRONMENT,
        'BACKOFFICE':   request.backoffice
    }



