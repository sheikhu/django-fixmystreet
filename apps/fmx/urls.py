from django.conf.urls import patterns

urlpatterns = patterns('apps.fmx.views',

    (r'^is_pro/$', 'is_pro'),
    (r'^ack/$', 'ack'),

    (r'^categories/$', 'categories'),
    (r'^categories_status/$', 'categories_status'),

    (r'^duplicates/$', 'duplicates'),

    (r'^password/reset$', 'userResetPassword'),
    (r'^password/reset/(?P<uidb64>[0-9A-Za-z]+)/(?P<token>.+)/$', 'validatePasswordReset'),
    (r'^password/change/(?P<uidb64>[0-9A-Za-z]+)/(?P<token>.+)/$', 'changePassword'),

    (r'^incidents/(?P<report_id>\d+)$', 'detail'),
    (r'^incidents/(?P<report_id>\d+)/attachments/$', 'attachments'),
    (r'^incidents/(?P<report_id>\d+)/history/$', 'history'),
    (r'^incidents/last$', 'last_reports'),
    (r'^incidents/map$', 'map_reports'),
    (r'^incidents$', 'reports'),
    (r'^incidents/create-report/$', 'create_incident'),

    (r'^statistics/incidents/$', 'stats'),

    (r'^incidents/(?P<report_id>\d+)/subscription-count/$', 'subscription_count'),
    (r'^incidents/(?P<report_id>\d+)/subscribe/$', 'subscribe'),
    (r'^incidents/(?P<report_id>\d+)/unsubscribe/$', 'unsubscribe'),
    (r'^incidents/(?P<report_id>\d+)/is-fixed/$', 'isFixed'),
    (r'^incidents/(?P<report_id>\d+)/inc-duplicate-counter/$', 'incDuplicateCounter'),
    (r'^incidents/(?P<report_id>\d+)/reopen/$', 'reopen'),
)
