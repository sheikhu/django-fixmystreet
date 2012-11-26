from django.conf.urls.defaults import *
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib.auth import views as auth_views
from django.views.generic.simple import direct_to_template

# from django_fixmystreet.backoffice.views.users import CreateUser

urlpatterns = patterns('django_fixmystreet.backoffice.views.main',
    url(r'^$', 'home',name='home_pro'),
)

urlpatterns += patterns('',
	url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'pro/login.html'},name='login'),
	url(r'^logout/$',
            auth_views.logout_then_login,
            {'login_url':'/pro/accounts/login/?next=/pro/'},
            name='auth_logout'
    ),
)


urlpatterns += patterns('django_fixmystreet.backoffice.views.reports.main',
    url(r'^report/(\d+)$', 'show',name='report_show_pro'),
    url(r'^report/new', 'new',name='report_new_pro'),
    url(r'^report/subscription', 'subscription',name='report_subscription_pro'),
)

urlpatterns += patterns('django_fixmystreet.backoffice.views.reports.list',
    url(r'^report/list/(.+)', 'list',name='report_list_pro'),
)

urlpatterns += patterns( 'django_fixmystreet.backoffice.views.reports.updates',
    url(r'^report/(\d+)/update/', 'new', name='report_update_pro'),
    url(r'^report/(\d+)/accept/', 'accept', name='report_accept_pro'),
    url(r'^report/(\d+)/refuse/', 'refuse', name='report_refuse_pro'),
    url(r'^report/(\d+)/fixed/', 'fixed', name='report_fix_pro'),
    url(r'^report/(\d+)/close/', 'close', name='report_close_pro'),
    url(r'^report/(\d+)/updateFile', 'updateFile', name='report_update_file'),
    url(r'^report/(\d+)/updateComment', 'updateComment', name='report_update_comment'),
    url(r'^report/(\d+)/fixed/', 'fixed', name='report_fix_pro'),
    url(r'^report/(\d+)/changeManager/', 'changeManager', name='report_change_manager_pro'),
    url(r'^report/(\d+)/changeContractor/', 'changeContractor', name='report_change_contractor_pro'),
    url(r'^report/(\d+)/accept_and_validate/', 'acceptAndValidate', name='report_accept_and_validate'),
)

urlpatterns += patterns( 'django_fixmystreet.backoffice.views.reports.subscribers',
    url(r'^report/(\d+)/subscribe/', 'create', name='subscribe_pro'),
    url(r'^report/(\d+)/unsubscribe/', 'unsubscribe',name='unsubscribe_pro'),
)

urlpatterns += patterns( 'django_fixmystreet.backoffice.views.reports.flags',
    url(r'^report/(\d+)/flags/thanks', 'thanks',name='flag_success_pro'),
    url(r'^report/(\d+)/flags', 'new',name='flag_report_pro'),
)

urlpatterns += patterns('django_fixmystreet.backoffice.views.manager_category_configuration',
    url(r'^categoryGestionnaireConfiguration/dialog/','update',name='gestionnaire_selection_dialog'),
    url(r'^categoryGestionnaireConfiguration','show',name='category_gestionnaire_configuration'),

)

urlpatterns += patterns('django_fixmystreet.backoffice.views.ajax',
    url(r'^ajax/saveSelection','saveCategoryConfiguration',name='saveSelection'),
)

urlpatterns +=patterns('django_fixmystreet.backoffice.views.users',
    url(r'users/overview/delete','deleteUser',name="userDelete"),
    url(r'users/overview/edit','edit',name='usersEdit'),
    url(r'users/overview/save','saveChanges',name="userSave"),
    url(r'users/overview','show',name='usersOverview'),
	url(r'^createuser','createUser',name='create_user_pro'),
)
