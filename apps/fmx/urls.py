from django.conf.urls import patterns

urlpatterns = patterns('apps.fmx.views',
    (r'^ack/$', 'ack'),
    (r'^categories/$', 'categories'),

    (r'^duplicates/$', 'duplicates'),

    (r'^incidents/(?P<report_id>\d+)$', 'detail'),
    (r'^incidents/(?P<report_id>\d+)/attachments/$', 'attachments'),
    (r'^incidents/(?P<report_id>\d+)/history/$', 'history'),
    (r'^incidents/last$', 'last_reports'),
    (r'^incidents$', 'reports'),

    (r'^statistics/incidents/$', 'stats'),
)
