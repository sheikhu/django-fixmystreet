
from django.contrib.sites.models import Site
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
import pkg_resources


def domain(request):
    site = Site.objects.get_current()
    return {
        'SITE_URL': 'http://{0}'.format(site.domain),
        'URBIS_URL': settings.URBIS_URL,
    }

def environment(request):
    return {
        'APP_VERSION': pkg_resources.require("django-fixmystreet")[0].version,
        'ENVIRONMENT': getattr(settings, 'ENVIRONMENT'),
        'BACKOFFICE': request.backoffice
    }


def login_form(request):
    return {
        'login_form': AuthenticationForm()
    }


