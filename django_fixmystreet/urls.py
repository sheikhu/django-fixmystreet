from django.conf.urls.defaults import url, patterns, include
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.conf import settings

from django_fixmystreet.fixmystreet.sitemaps import ReportSitemap

admin.autodiscover()
js_info_dict = {
    'packages': ('django_fixmystreet.fixmystreet', 'django_fixmystreet.backoffice', ),
}

urlpatterns = i18n_patterns(
    '',
    url(r'^', include('django_fixmystreet.fixmystreet.urls')),
    url(r'^pro/', include('django_fixmystreet.backoffice.urls')),
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict, name='jsi18n'),
    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': {
        "reports": ReportSitemap()
    }}),
)
urlpatterns += patterns(
    '',
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', admin.site.urls),
    (r'^ckeditor/', include('ckeditor.urls')),
    (r'^monitoring/', include('django_fixmystreet.monitoring.urls')),
    (r'^status/', include('mobileserverstatus.urls')),
)
if settings.DEBUG:
    baseurlregex = r'^media/(?P<path>.*)$'
    urlpatterns += patterns(
        '', (
            baseurlregex,
            'django.views.static.serve',
            {'document_root':  settings.MEDIA_ROOT}
        ),
        (r'^debug/', include('django_fixmystreet.fixmystreet.debug.urls'))
    )

if settings.DEBUG:
    urlpatterns += patterns(
        'django_fixmystreet.fixmystreet.views.api',
        ('^urbis/(?P<path>.*)$', 'proxy'),
    )
