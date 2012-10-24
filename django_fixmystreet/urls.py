
from django.conf.urls.defaults import patterns, include
from django.contrib import admin

from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    (r'', include('django_fixmystreet.fixmystreet.urls')),
    (r'pro/', include('django_fixmystreet.backoffice.urls')),
    (r'^admin/', admin.site.urls),
)

#The following is used to serve up local media files like images
if settings.DEBUG:
    baseurlregex = r'^static/(?P<path>.*)$'
    urlpatterns += patterns('',
        (
            baseurlregex, 
            'django.views.static.serve',
            {'document_root':  settings.STATIC_ROOT}
        ),
    )
#The following is used to serve up local media files like images
if settings.DEBUG:
    baseurlregex = r'^media/(?P<path>.*)$'
    urlpatterns += patterns('',
        (
            baseurlregex, 
            'django.views.static.serve',
            {'document_root':  settings.MEDIA_ROOT}
        ),
    )
