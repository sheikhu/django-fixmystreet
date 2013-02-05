from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('django_fixmystreet.monitoring.views',
    url(r'^happy/$', 'happy_page', name="happy_page"),
    url(r'^cpu/$', 'cpu', name="monitoring_cpu"),
)
