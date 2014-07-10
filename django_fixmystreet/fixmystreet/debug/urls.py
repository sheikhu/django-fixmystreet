from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'django_fixmystreet.fixmystreet.debug.views',
    url(r'^rank/$', 'rank'),
)
