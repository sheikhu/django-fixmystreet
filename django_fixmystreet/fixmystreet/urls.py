from django.conf.urls.defaults import patterns, url
from django.utils.translation import ugettext_lazy as _

from piston.resource import Resource

from django_fixmystreet.fixmystreet.api import ReportHandler
#from django_fixmystreet.fixmystreet.views.api import CitizenReportHandler, ProReportHandler

urlpatterns = patterns(
    'django_fixmystreet.fixmystreet.views.main',
    url(_(r'^$'), 'home', name='home'),
    url(_(r'^about/$'), 'about', name='about'),
    url(_(r'^faq/$'), 'faq', name='faq'),
    url(_(r'^help/$'), 'help', name='help'),
    url(_(r'^terms-of-use/$'), 'terms_of_use', name='terms_of_use'),
    url(r'^update-language/', 'update_current_language', name="update_current_language"),
)


urlpatterns += patterns(
    'django_fixmystreet.backoffice.views.users',
    url(r'^login/$', 'login_view', name='login'),
)

urlpatterns += patterns(
    'django.contrib.auth.views',
    (r'^accounts/password/reset/$', 'password_reset', {
        'post_reset_redirect': '/accounts/password/reset/done/',
        'template_name': 'admin/registration/password_reset_form.html'
    }),
    (r'^accounts/password/reset/done/$', 'password_reset_done', {'template_name': 'admin/registration/password_reset_done.html'}),
    (r'^accounts/password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'password_reset_confirm', {
        'post_reset_redirect': '/accounts/password/done/',
        'template_name': 'admin/registration/password_reset_confirm.html'
    }),
    (r'^accounts/password/done/$', 'password_reset_complete', {'template_name': 'admin/registration/password_reset_complete.html'}),
)

urlpatterns += patterns(
    'django_fixmystreet.fixmystreet.views.reports.main',
    url(_(r'^reports/$'), 'index', name='report_index'),
    # url(_(r'^reports/(?P<slug>.*)/$'), 'index', name='report_commune_index'),
    url(_(r'^report/(?P<slug>.*)/(?P<report_id>\d+)$'), 'show', name='report_show'),
    url(_(r'^report/(?P<slug>.*)/(?P<report_id>\d+)/document$'), 'document', name='report_document'),
    url(r'^report/search', 'search_ticket', name='search_ticket'),
    url(_(r'^report/new'), 'new', name='report_new'),
    url(_(r'^report/verify'), 'verify', name='report_verify'),
    # url(_(r'^report/prepare'), 'report_prepare', name='report_prepare'),
    url(_(r'^report/(\d+)/update/'), 'update', name='report_update')
)

urlpatterns += patterns(
    'django_fixmystreet.fixmystreet.views.reports.updates',
    url(_(r'^report/(\d+)/pdf/(pro)?'), 'report_pdf', name='report_pdf'),
)

urlpatterns += patterns(
    'django_fixmystreet.fixmystreet.views.reports.subscribers',
    url(_(r'^report/(\d+)/subscribe/'), 'create', name='subscribe'),
    url(_(r'^report/(\d+)/unsubscribe/'), 'remove', name='unsubscribe'),
)

urlpatterns += patterns(
    'django_fixmystreet.fixmystreet.views.ajax',
    url(r'^ajax/create-comment', 'create_comment', name='create_report_comment'),
    url(r'^ajax/create-file', 'create_file', name='create_report_file'),
    url(r'^ajax/categories/(\d+)', 'report_category_note', name='report_category_note'),
    url(r'^ajax/upload-file', 'uploadFile', name='report_upload_file'),
    url(r'^ajax/reportPopupDetails', 'get_report_popup_details', name="get_report_popup_details"),
    url(r'^ajax/map/filter/', 'filter_map', name="filter_map"),
)


urlpatterns += patterns(
    'django_fixmystreet.fixmystreet.views.api',
    url(r'^api/reports/$', 'reports_pro', name='api_reports'),
    url(r'^api/reports/mobile/$', 'reports_pro_mobile', name='api_reports'),
    url(r'^api/reports/map/$', 'reports_pro', name='api_reports'),
    url(r'^api/reports/citizen/nearest/$', 'near_reports_citizen', name='api_reports'),
    url(r'^api/reports/pro/nearest/$', 'near_reports_pro', name='api_reports'),
    url(r'^api/reports/citizen/$', 'reports_citizen', name='api_reports'),
    url(r'^api/reports/pro/$', 'reports_pro', name='api_reports'),
    #url(_(r'^api/report/new/$'), 'create_report',name='api_report_new'),
    url(r'^api/login/$', 'login_user', name='login_user'),
    url(r'^api/logout/$', 'logout_user', name='logout_user'),
    url(r'^api/load_categories/$', 'load_categories', name='load_categories'),
    url(r'^api/load_zipcodes/$', 'load_zipcodes', name='load_zipcodes'),
    url(r'^api/create-report/$', Resource(ReportHandler), name="create_report_citizen"),
    url(r'^api/create_report_photo/$', 'create_report_photo', name='create_report_photo'),
    url(r'^api/commit-report/$', 'commit_report', name='commit_report'),
)
