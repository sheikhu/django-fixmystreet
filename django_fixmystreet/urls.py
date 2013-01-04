from django.conf.urls.defaults import url, patterns, include
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.conf import settings

from django_fixmystreet.fixmystreet.sitemaps import ReportSitemap

admin.autodiscover()

urlpatterns = i18n_patterns('',
    url(r'^', include('django_fixmystreet.fixmystreet.urls')),
    url(r'^pro/', include('django_fixmystreet.backoffice.urls')),
    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': {
        "reports": ReportSitemap()
    }}),
)
urlpatterns += patterns('',
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', admin.site.urls),
)
if settings.DEBUG:
    baseurlregex = r'^media/(?P<path>.*)$'
    urlpatterns += patterns('',
        (
            baseurlregex,
            'django.views.static.serve',
            {'document_root':  settings.MEDIA_ROOT}
        ),
    )
