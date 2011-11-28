
from django.contrib.sites.models import Site


def domain_context_processor(request):
    site = Site.objects.get_current()
    return {'SITE_URL': 'http://{}'.format(site.domain)}
