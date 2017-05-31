from django.conf.urls import patterns, url
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse

urlpatterns = patterns(
    'apps.fixmystreet.views.main',
    url(_(r'^$'), 'home', name='home'),
    url(_(r'^robots.txt$'), lambda r: HttpResponse("User-agent: Sogou web spider\nDisallow: /", content_type="text/plain")),
    url(_(r'^about/$'), 'page', name='about'),
    url(_(r'^faq-pro/$'), 'faq_pro', name='faq_pro'),
    url(_(r'^faq/$'), 'page', name='faq'),
    url(_(r'^help/$'), 'page', name='help'),
    url(_(r'^terms-of-use/$'), 'page', name='terms_of_use'),
    url(r'^update-language/$', 'update_current_language', name="update_current_language"),
)


urlpatterns += patterns(
    'apps.backoffice.views.users',
    url(r'^login/$', 'login_view', name='login'),
)

from apps.fixmystreet.forms import FMSPasswordResetForm
urlpatterns += patterns(
    'django.contrib.auth.views',
    (r'^accounts/password/reset/$', 'password_reset', {
        'post_reset_redirect': '/accounts/password/reset/done/',
        'template_name': 'admin/registration/password_reset_form.html',
        'password_reset_form': FMSPasswordResetForm
    }),
    (r'^accounts/password/reset/done/$', 'password_reset_done', {'template_name': 'admin/registration/password_reset_done.html'}),
    url(r'^accounts/password/reset/(?P<uidb64>[0-9A-Za-z]+)/(?P<token>.+)/$', 'password_reset_confirm', {
        'post_reset_redirect': '/accounts/password/done/',
        'template_name': 'admin/registration/password_reset_confirm.html'
    }, name='password_reset_confirm'),

    (r'^accounts/password/done/$', 'password_reset_complete', {'template_name': 'admin/registration/password_reset_complete.html'}),
)

# Legacy url : old syntax with report keyword
urlpatterns += patterns(
    'apps.fixmystreet.views.reports.main',
    url(r'^report/(?P<slug>.*)/(?P<report_id>\d+)$', 'show'),
)

urlpatterns += patterns(
    'apps.fixmystreet.views.reports.main',
    url(_(r'^reports/$'), 'index', name='report_index'),
    # url(_(r'^reports/(?P<slug>.*)/$'), 'index', name='report_commune_index'),
    url(_(r'^report/(?P<slug>.*)/(?P<report_id>\d+)$'), 'show', name='report_show'),
    url(_(r'^report/(?P<slug>.*)/(?P<report_id>\d+)/document$'), 'document', name='report_document'),
    url(_(r'^report/(?P<slug>.*)/(?P<report_id>\d+)/reopen$'), 'reopen_request', name='report_reopen_request'),
    url(r'^report/search', 'search_ticket', name='search_ticket'),
    url(_(r'^report/new'), 'new', name='report_new'),
    url(_(r'^report/verify'), 'verify', name='report_verify'),
    # url(_(r'^report/prepare'), 'report_prepare', name='report_prepare'),
    url(_(r'^report/(\d+)/update/'), 'update', name='report_update')
)

urlpatterns += patterns(
    'apps.fixmystreet.views.reports.updates',
    url(_(r'^report/(\d+)/pdf/(pro)?'), 'report_pdf', name='report_pdf'),
)

urlpatterns += patterns(
    'apps.fixmystreet.views.reports.subscribers',
    url(_(r'^report/(\d+)/subscribe/'), 'create', name='subscribe'),
    url(_(r'^report/(\d+)/unsubscribe/'), 'remove', name='unsubscribe'),
)

urlpatterns += patterns(
    'apps.fixmystreet.views.ajax',
    url(r'^ajax/create-comment', 'create_comment', name='create_report_comment'),
    url(r'^ajax/create-file', 'create_file', name='create_report_file'),
    url(r'^ajax/categories/(\d+)', 'report_category_note', name='report_category_note'),
    url(r'^ajax/upload-file', 'uploadFile', name='report_upload_file'),
    url(r'^ajax/reportPopupDetails', 'get_report_popup_details', name="get_report_popup_details"),
    url(r'^ajax/map/filter/', 'filter_map', name="filter_map"),
)

urlpatterns += patterns(
    'apps.fixmystreet.views.api',
    url(r'^api/reports/$', 'reports_pro', name='api_reports'),
    url(r'^api/reports/mobile/$', 'reports_pro_mobile', name='api_reports'),
    url(r'^api/reports/map/$', 'reports_pro', name='api_reports'),
    url(r'^api/reports/citizen/nearest/$', 'near_reports_citizen', name='api_reports'),
    url(r'^api/reports/pro/nearest/$', 'near_reports_pro', name='api_reports'),
    url(r'^api/reports/citizen/$', 'reports_citizen', name='api_reports'),
    url(r'^api/reports/pro/$', 'reports_pro', name='api_reports'),

    url(r'^api/login/$', 'login_user', name='login_user'),
    url(r'^api/logout/$', 'logout_user', name='logout_user'),

    url(r'^api/load_categories/$', 'load_categories', name='load_categories'),
    url(r'^api/load_zipcodes/$', 'load_zipcodes', name='load_zipcodes'),

    url(r'^api/create-report/$', 'create_report', name="create_report_citizen"),
    url(r'^api/create_report_photo/$', 'create_report_photo', name='create_report_photo'),

    url(r'^api/commit-report/$', 'commit_report', name='commit_report'),
)
