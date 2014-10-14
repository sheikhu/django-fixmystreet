from django.conf.urls.defaults import url, patterns, include

urlpatterns = patterns('django_fixmystreet.fmsproxy.views',
    (r'^accept/(?P<report_id>\d+)/$', 'accept'),
    (r'^reject/(?P<report_id>\d+)/$', 'reject'),
    (r'^close/(?P<report_id>\d+)/$', 'close'),

    # It's an example of view decoding json data in fmsproxy. It's not used by FMS.
    (r'^test_assign/$', 'test_assign'),
)
