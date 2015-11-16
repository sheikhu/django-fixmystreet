from django.conf.urls import patterns, url
from django.utils.translation import ugettext_lazy as _


urlpatterns = patterns(
    'apps.backoffice.views.main',
    url(_(r'^$'), 'home', name='home_pro'),
)

# Legacy url : old syntax with report keyword
urlpatterns += patterns(
    'apps.backoffice.views.reports.main',
    url(r'^report/(?P<slug>.*)/(?P<report_id>\d+)$', 'show'),
)

urlpatterns += patterns(
    'apps.backoffice.views.reports.main',
    url(_(r'^report/(?P<slug>.*)/(?P<report_id>\d+)$'), 'show', name='report_show_pro'),
    url(_(r'^report/(?P<slug>.*)/(?P<report_id>\d+)/document$'), 'document', name='report_document_pro'),
    url(_(r'^report/(?P<slug>.*)/(?P<report_id>\d+)/reopen$'), 'reopen_request', name='report_reopen_request_pro'),
    url(_(r'^report/(?P<slug>.*)/(?P<report_id>\d+)/merge$'), 'merge', name='report_merge_pro'),
    url(_(r'^report/new'), 'new', name='report_new_pro'),
    url(_(r'^report/verify'), 'verify', name='report_verify_pro'),
    url(r'^report/search$', 'search_ticket_pro', name='search_ticket_pro'),
    url(_(r'^report/$'), 'report_prepare_pro', name='report_prepare_pro'),
    url(_(r'^report/(\d+)/delete/$'), 'delete', name='report_delete_pro'),
)

urlpatterns += patterns(
    'apps.backoffice.views.reports.list',
    url(_(r'^report/table/$'), 'table', name='report_table_pro'),
    url(_(r'^report/table-content/(?P<selection>\w+)?$'), 'table_content', name='report_table_content_pro'),
)

urlpatterns += patterns(
    'apps.backoffice.views.reports.updates',
    url(_(r'^report/(\d+)/accept/$'), 'accept', name='report_accept_pro'),
    url(_(r'^report/(\d+)/refuse/$'), 'refuse', name='report_refuse_pro'),
    url(_(r'^report/(\d+)/fixed/$'), 'fixed', name='report_fix_pro'),
    url(_(r'^report/(\d+)/close/$'), 'close', name='report_close_pro'),
    url(_(r'^report/(\d+)/reopen/$'), 'reopen', name='report_reopen_pro'),
    url(_(r'^report/(\d+)/merge/$'), 'do_merge', name='report_do_merge_pro'),
    url(_(r'^report/(\d+)/planned/$'), 'planned', name='report_planned_pro'),
    url(_(r'^report/(\d+)/pending/$'), 'pending', name='report_pending_pro'),
    url(_(r'^report/(\d+)/not-pending/$'), 'notpending', name='report_notpending_pro'),
    url(_(r'^report/(\d+)/validate-all/$'), 'validateAll', name='report_validate_all_pro'),
    url(_(r'^report/(\d+)/update-attachment$'), 'updateAttachment', name='report_update_attachment'),
    url(_(r'^report/(\d+)/delete-file$'), 'deleteAttachment', name='report_delete_attachment'),
    url(_(r'^report/(\d+)/change-responsible/'), 'changeManager', name='report_change_manager_pro'),
    url(_(r'^report/(\d+)/change-contractor/'), 'changeContractor', name='report_change_contractor_pro'),
    url(_(r'^report/(\d+)/switch-visibility/'), 'switchVisibility', name='report_change_switch_visibility'),
    url(_(r'^report/(\d+)/switch-third-party-responsibility/'), 'switchThirdPartyResponsibility', name='report_change_switch_third_party_responsibility'),
    url(_(r'^report/(\d+)/switch-private-property/'), 'switchPrivateProperty', name='report_change_switch_private_property'),
    url(_(r'^report/(\d+)/update-priority/'), 'updatePriority', name="report_update_priority"),
    url(_(r'^report/(\d+)/false-address/'), 'report_false_address', name="report_false_address"),
    url(_(r'^report/(\d+)/change-flag-and-add-comment/'), 'change_flag_and_add_comment', name="report_change_flag_and_add_comment"),
)

urlpatterns += patterns(
    'apps.fixmystreet.views.reports.updates',
    url(_(r'^report/(\d+)/pdf/'), 'report_pdf', {"pro_version": True}, name='report_pdf_pro'),
)

urlpatterns += patterns(
    'apps.backoffice.views.reports.subscribers',
    url(_(r'^report/(\d+)/subscribe/'), 'create', name='subscribe_pro'),
    url(_(r'^report/(\d+)/unsubscribe/'), 'unsubscribe', name='unsubscribe_pro'),
)

urlpatterns += patterns(
    'apps.backoffice.views.manager_category_configuration',
    url(r'^category-gestionnaire-configuration/dialog/', 'update', name='gestionnaire_selection_dialog'),
    url(r'^category-gestionnaire-configuration', 'show', name='category_gestionnaire_configuration'),

)

urlpatterns += patterns(
    'apps.backoffice.views.ajax',
    url(r'^ajax/saveSelection', 'saveCategoryConfiguration', name='saveSelection'),
    url(r'^ajax/reportPopupDetails', 'get_report_popup_details', name="get_report_popup_details_pro"),
    # url(r'^ajax/map/filter/', 'filter_map', name="filter_map"),
    url(r'^ajax/secondary_category_for_main_category', 'secondary_category_for_main_category', name="secondary_category_for_main_category"),
    url(r'^ajax/update_category_for_report/(\d+)', 'update_category_for_report', name="update_category_for_report"),
    url(r'^ajax/send_pdf/(\d+)', 'send_pdf', name="send_pdf"),
)

urlpatterns += patterns(
    'apps.backoffice.views.users',
    # (r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^logout/$', 'logout_view', name='logout'),
    url(r'^change-password/$', 'change_password', name='password_change'),
    #url(_(r'^change_password/$'), 'django.contrib.auth.views.password_change', {'template_name': 'pro/change_password.html','post_change_redirect':'/pro/'}, name='password_change'),

    url(r'^users/$', 'list_users', name='list_users'),
    url(r'^users/(?P<user_id>\d+)/$', 'edit_user', name='edit_user'),
    url(r'^users/create$', 'create_user', name='create_user'),
    url(r'^users/(?P<user_id>\d+)/delete$', 'delete_user', name="delete_user"),
)

urlpatterns += patterns(
    'apps.backoffice.views.groups',
    url(r'^groups/$', 'list_groups', name='list_groups'),
    url(r'^groups/create/$', 'create_group', name='create_group'),

    url(r'^groups/(?P<group_id>\d+)/$', 'edit_group', name='edit_group'),
    url(r'^groups/(?P<group_id>\d+)/delete/$', 'delete_group', name='delete_group'),

    url(r'^groups/membership/add/(?P<group_id>\d+)/(?P<user_id>\d+)/$', 'add_membership', name='add_membership'),
    url(r'^groups/membership/remove/(?P<membership_id>\d+)/$', 'remove_membership', name='remove_membership'),
    url(r'^groups/membership/contact/(?P<membership_id>\d+)/$', 'contact_membership', name='contact_membership'),
)

urlpatterns += patterns(
    'apps.backoffice.views.reporting',
    url(r'^reporting/$', 'reporting_list', name='reporting_list'),
    url(r'^reporting/(?P<path>.+)$', 'reporting_download', name='reporting_download'),
)
