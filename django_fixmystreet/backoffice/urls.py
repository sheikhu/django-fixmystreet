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
    url(_(r'^report/list'), 'list', name='report_list_pro'),
    url(_(r'^report/table'), 'table', name='report_table_pro'),
)

urlpatterns += patterns( 'django_fixmystreet.backoffice.views.reports.updates',
    url(_(r'^report/(\d+)/accept/$'), 'accept', name='report_accept_pro'),
    url(_(r'^report/(\d+)/refuse/$'), 'refuse', name='report_refuse_pro'),
    url(_(r'^report/(\d+)/fixed/$'), 'fixed', name='report_fix_pro'),
    url(_(r'^report/(\d+)/close/$'), 'close', name='report_close_pro'),
    url(_(r'^report/(\d+)/merge/$'),'merge',name='report_merge_pro'),
    url(_(r'^report/(\d+)/planned/$'), 'planned', name='report_planned_pro'),
    url(_(r'^report/(\d+)/validateAll/$'),'validateAll',name='report_validate_all_pro'),
    url(_(r'^report/(\d+)/updateAttachment$'), 'updateAttachment', name='report_update_attachment'),
    url(_(r'^report/(\d+)/deleteFile$'), 'deleteAttachment', name='report_delete_attachment'),
    url(_(r'^report/(\d+)/changeManager/'), 'changeManager', name='report_change_manager_pro'),
    url(_(r'^report/(\d+)/changeContractor/'), 'changeContractor', name='report_change_contractor_pro'),
    url(_(r'^report/(\d+)/switchPrivacy/'), 'switchPrivacy', name='report_change_switch_privacy'),
    url(_(r'^report/(\d+)/publish/'), 'publish', name='report_publish_pro'),
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
    url(_(r'^ajax/reportPopupDetails'),'get_report_popup_details',name="get_report_popup_details_pro"),
    url(_(r'^ajax/report/(\d+)/updatePriority/'),'updatePriority',name="report_update_priority"),
)

urlpatterns +=patterns('django_fixmystreet.backoffice.views.users',
    # (r'^accounts/', include('registration.backends.simple.urls')),
    url(_(r'^logout/$'),'logout_view', name='logout'),
    url(_(r'^change-password/$'), 'change_password', name='password_change'),
    #url(_(r'^change_password/$'), 'django.contrib.auth.views.password_change', {'template_name': 'pro/change_password.html','post_change_redirect':'/pro/'}, name='password_change'),

    url(r'^users/$', 'list_users', name='list_users'),
    url(r'^users/(?P<user_id>\d+)/$', 'edit_user', name='edit_user'),
    url(r'^users/create$',   'create_user', name='create_user'),
    url(r'^users/(?P<user_id>\d+)/delete$', 'delete_user', name="delete_user"),

    # url(r'^contractors/$', 'list_contractors', name='list_contractors'),
    # url(r'^contractors/create$', 'create_contractor', name='create_contractor'),
    # url(r'^contractors/(?P<contractor_id>\d+)/delete$', 'delete_contractor', name='delete_contractor'),
)

urlpatterns +=patterns('django_fixmystreet.backoffice.views.groups',
    url(r'^groups/$',                   'list_groups',  name='list_groups'),
    url(r'^groups/create/$',            'create_group', name='create_group'),

    url(r'^groups/(?P<group_id>\d+)/$', 'edit_group',   name='edit_group'),
    url(r'^groups/(?P<group_id>\d+)/delete/$', 'delete_group',   name='delete_group'),

    url(r'^groups/membership/add/(?P<group_id>\d+)/(?P<user_id>\d+)/$', 'add_membership',   name='add_membership'),
    url(r'^groups/membership/remove/(?P<membership_id>\d+)/$', 'remove_membership',   name='remove_membership'),
)

urlpatterns += patterns('',
    url(_(r'^export_file/reports/(?P<emitter_format>.+)/(?P<id>\d+)'), Resource(ReportHandler), name="export_report"),
    url(_(r'^export_file/reports/(?P<emitter_format>.+)/fromtime/(?P<time_ago>.+)'), Resource(ReportHandler), name="export_report"),
    url(_(r'^export_file/reports/(?P<emitter_format>.+)'), Resource(ReportHandler), name="export_report"),
)
