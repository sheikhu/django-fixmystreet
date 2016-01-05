from django.conf.urls import patterns, url

urlpatterns = patterns(
    'apps.fixmystreet.debug.views',
    url(r'^rank/$', 'rank'),
)
