from django.conf.urls.defaults import patterns, url
from django.utils.translation import ugettext_lazy as _

from piston.resource import Resource

from django_fixmystreet.fixmystreet.api import ReportHandler

# from django_fixmystreet.backoffice.views.users import CreateUser


urlpatterns = patterns('django_fixmystreet.backoffice.views.main',
    url(_(r'^$'), 'home',name='home_pro'),
)

urlpatterns += patterns('django_fixmystreet.backoffice.views.reports.main',
    url(_(r'^report/(?P<slug>.*)/(?P<report_id>\d+)$'), 'show',name='report_show_pro'),
    url(_(r'^report/new$'), 'new',name='report_new_pro'),
    url(_(r'^report/subscription$'), 'subscription',name='report_subscription_pro'),
    url(_(r'^report/search$'), 'search_ticket_pro',name='search_ticket_pro'),
    url(_(r'^report/$'), 'report_prepare_pro',name='report_prepare_pro'),
    url(_(r'^report/(\d+)/delete/$'), 'delete', name='report_delete_pro'),
)

urlpatterns += patterns('django_fixmystreet.backoffice.views.reports.list',
    url(_(r'^report/list/(.+)'), 'list',name='report_list_pro'),
)

urlpatterns += patterns( 'django_fixmystreet.backoffice.views.reports.updates',
    url(_(r'^report/(\d+)/update/$'), 'new', name='report_update_pro'),
    url(_(r'^report/(\d+)/accept/$'), 'accept', name='report_accept_pro'),
    url(_(r'^report/(\d+)/refuse/$'), 'refuse', name='report_refuse_pro'),
    url(_(r'^report/(\d+)/fixed/$'), 'fixed', name='report_fix_pro'),
    url(_(r'^report/(\d+)/close/$'), 'close', name='report_close_pro'),
    url(_(r'^report/(\d+)/validateAll/$'),'validateAll',name='report_validate_all_pro'),
    url(_(r'^report/(\d+)/updateFile$'), 'updateFile', name='report_update_file'),
    url(_(r'^report/(\d+)/deleteFile$'), 'deleteFile', name='report_delete_file'),
    url(_(r'^report/(\d+)/updateComment$'), 'updateComment', name='report_update_comment'),
    url(_(r'^report/(\d+)/deleteComment$'), 'deleteComment', name='report_delete_comment'),
    url(_(r'^report/(\d+)/changeManager/'), 'changeManager', name='report_change_manager_pro'),
    url(_(r'^report/(\d+)/changeContractor/'), 'changeContractor', name='report_change_contractor_pro'),
    url(_(r'^report/(\d+)/switchPrivacy/'), 'switchPrivacy', name='report_change_switch_privacy'),
    url(_(r'^report/(\d+)/accept_and_validate/'), 'acceptAndValidate', name='report_accept_and_validate'),
)
urlpatterns += patterns( 'django_fixmystreet.fixmystreet.views.reports.updates',
    url(_(r'^report/(\d+)/pdf/'), 'report_pdf', {"pro_version": True}, name='report_pdf_pro'),
)

urlpatterns += patterns( 'django_fixmystreet.backoffice.views.reports.subscribers',
    url(_(r'^report/(\d+)/subscribe/'), 'create', name='subscribe_pro'),
    url(_(r'^report/(\d+)/unsubscribe/'), 'unsubscribe',name='unsubscribe_pro'),
)

urlpatterns += patterns( 'django_fixmystreet.backoffice.views.reports.flags',
    url(_(r'^report/(\d+)/flags/thanks'), 'thanks',name='flag_success_pro'),
    url(_(r'^report/(\d+)/flags'), 'new',name='flag_report_pro'),
)

urlpatterns += patterns('django_fixmystreet.backoffice.views.manager_category_configuration',
    url(r'^category-gestionnaire-configuration/dialog/','update',name='gestionnaire_selection_dialog'),
    url(r'^category-gestionnaire-configuration','show',name='category_gestionnaire_configuration'),

)

urlpatterns += patterns('django_fixmystreet.backoffice.views.ajax',
    url(_(r'^ajax/saveSelection'),'saveCategoryConfiguration',name='saveSelection'),
)

urlpatterns +=patterns('django_fixmystreet.backoffice.views.users',
    # (r'^accounts/', include('registration.backends.simple.urls')),
    url(_(r'^logout/$'),'logout_view', name='logout'),
    url(_(r'^change-password/$'), 'change_password', name='password_change'),
    #url(_(r'^change_password/$'), 'django.contrib.auth.views.password_change', {'template_name': 'pro/change_password.html','post_change_redirect':'/pro/'}, name='password_change'),

    url(r'^users/$',    'list_users', {'user_type': 'users'},    name='list_users'),
    url(r'^agents/$',   'list_users', {'user_type': 'agents'},   name='list_users'),
    url(r'^managers/$', 'list_users', {'user_type': 'managers'}, name='list_users'),
    url(r'^contractors/$', 'list_contractors', name='list_contractors'),

    url(r'^users/(?P<user_id>\d+)/$',    'list_users', {'user_type': 'users'},    name='edit_user'),
    url(r'^agents/(?P<user_id>\d+)/$',   'list_users', {'user_type': 'agents'},   name='edit_user'),
    url(r'^managers/(?P<user_id>\d+)/$', 'list_users', {'user_type': 'managers'}, name='edit_user'),
    url(r'^contractors/(?P<contractor_id>\d+)/$', 'list_contractors', name='edit_contractor'),

    url(r'^users/create$',   'create_user', {'user_type': 'users'},     name='create_user'),
    url(r'^agents/create$',  'create_user', {'user_type': 'agents'},    name='create_user'),
    url(r'^managers/create$','create_user', {'user_type': 'managers'},  name='create_user'),
    url(r'^contractors/create$', 'create_contractor', name='create_contractor'),

    url(r'^users/(?P<user_id>\d+)/delete$',    'delete_user', {'user_type': 'users'},    name="delete_user"),
    url(r'^agents/(?P<user_id>\d+)/delete$',   'delete_user', {'user_type': 'agents'},   name="delete_user"),
    url(r'^managers/(?P<user_id>\d+)/delete$', 'delete_user', {'user_type': 'managers'}, name="delete_user"),
    url(r'^contractors/(?P<contractor_id>\d+)/delete$', 'delete_contractor', name='delete_contractor'),
)

urlpatterns += patterns('',
    url(_(r'^export_file/reports/(?P<emitter_format>.+)/(?P<id>\d+)'), Resource(ReportHandler), name="export_report"),
    url(_(r'^export_file/reports/(?P<emitter_format>.+)'), Resource(ReportHandler), name="export_report"),
)
