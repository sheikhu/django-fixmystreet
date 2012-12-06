
from django.contrib.sites.models import Site
from django.conf import settings


def domain(request):
    site = Site.objects.get_current()
    return {
        'SITE_URL': 'http://{0}'.format(site.domain),
        'GEOSERVER': settings.GEOSERVER,
        'SERVICE_GIS': settings.SERVICE_GIS,
    }

def environment(request):
    return {
        'ENVIRONMENT': getattr(settings, 'ENVIRONMENT'),
        'BACKOFFICE': request.backoffice
    }


