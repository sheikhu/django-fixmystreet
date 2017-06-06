from django.conf.urls import url, patterns, include
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.conf import settings

from apps.fixmystreet.sitemaps import ReportSitemap

admin.autodiscover()
js_info_dict = {
    'packages': ('apps.fixmystreet', 'apps.backoffice', ),
}

urlpatterns = i18n_patterns(
    '',
    url(r'^', include('apps.fixmystreet.urls')),
    url(r'^pro/', include('apps.backoffice.urls')),
    url(r'^token/', include('fixmystreet_project.urls_token')),
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
    (r'^monitoring/', include('monitoring.urls')),
    (r'^status/', include('mobileserverstatus.urls')),
    url(r'^fms-proxy/', include('apps.fmsproxy.urls')),
)
urlpatterns += patterns(
    '',
    url(r'^api/v1/', include('apps.api.urls', namespace='api'))
)
urlpatterns += patterns(
    '',
    url(r'^fmx/api/', include('apps.fmx.urls', namespace='fmx'))
)
if settings.DEBUG:
    baseurlregex = r'^media/(?P<path>.*)$'
    urlpatterns += patterns(
        '', (
            baseurlregex,
            'django.views.static.serve',
            {'document_root':  settings.MEDIA_ROOT}
        ),
        (r'^debug/', include('apps.fixmystreet.debug.urls'))
    )

if settings.DEBUG:
    urlpatterns += patterns(
        'apps.fixmystreet.views.api',
        ('^urbis/(?P<path>.*)$', 'proxy'),
    )
