from django.conf.urls import patterns

urlpatterns = patterns('apps.fmx.views',
    (r'^ack/$', 'ack'),
    (r'^categories/$', 'categories'),
    (r'^stats/$', 'stats'),
    (r'^duplicates/$', 'duplicates'),

    (r'^(?P<report_id>\d+)$', 'detail'),
    (r'^(?P<report_id>\d+)/attachments/$', 'attachments'),
    (r'^(?P<report_id>\d+)/history/$', 'history'),
)
