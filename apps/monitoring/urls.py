from django.conf.urls import patterns, url

urlpatterns = patterns('apps.monitoring.views',
    url(r'^happy/$', 'happy_page', name="happy_page"),
    url(r'^cpu/$', 'cpu', name="monitoring_cpu"),
)
