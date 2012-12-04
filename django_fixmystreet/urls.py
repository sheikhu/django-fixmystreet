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
    (r'^admin/', admin.site.urls),
)
urlpatterns += patterns('',
    (r'^i18n/', include('django.conf.urls.i18n')),
)
