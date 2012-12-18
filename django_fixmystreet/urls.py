from django.conf.urls.defaults import *
from django.conf.urls.defaults import patterns, include
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

admin.autodiscover()

urlpatterns = i18n_patterns('',
    url(r'^', include('django_fixmystreet.fixmystreet.urls')),
    url(r'^pro/', include('django_fixmystreet.backoffice.urls')),
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
