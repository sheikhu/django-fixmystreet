
from django.conf.urls.defaults import *

from django_fixmystreet import settings

urlpatterns = patterns('',
    (r'', include('django_fixmystreet.fixmystreet.urls'))
)

#The following is used to serve up local media files like images
if settings.LOCAL_DEV:
    baseurlregex = r'^media/(?P<path>.*)$'
    urlpatterns += patterns('',
        (
            baseurlregex, 
            'django.views.static.serve',
            {'document_root':  settings.MEDIA_ROOT}
        ),
    )
