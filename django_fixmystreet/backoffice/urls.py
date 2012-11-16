from django.conf.urls.defaults import *
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib.auth import views as auth_views
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('django_fixmystreet.backoffice.views.main',
    url(r'^$', 'home',name='home_pro'),
)

urlpatterns += patterns('',
	url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'connection.html'},name='login'),
	url(r'^logout/$',
            auth_views.logout_then_login,
            {'login_url':'/pro/accounts/login/'},
            name='auth_logout'
    ),
)


urlpatterns += patterns('django_fixmystreet.backoffice.views.reports.main',
    url(r'^report/(\d+)$', 'show',name='report_show_pro'),       
    url(r'^report/new', 'new',name='report_new_pro'),
    url(r'^report/subscription', 'subscription',name='report_subscription_pro'),
)

urlpatterns += patterns( 'django_fixmystreet.backoffice.views.reports.updates',
    url(r'^report/(\d+)/update/', 'new', name='report_update_pro'),
    url(r'^report/(\d+)/accept/', 'accept', name='report_accept_pro'),
    url(r'^report/(\d+)/refuse/', 'refuse', name='report_refuse_pro'),
)

urlpatterns += patterns( 'django_fixmystreet.backoffice.views.reports.subscribers',
    url(r'^report/(\d+)/subscribe/', 'create', name='subscribe_pro'),
    url(r'^report/(\d+)/unsubscribe/', 'unsubscribe',name='unsubscribe_pro'),
)

urlpatterns += patterns( 'django_fixmystreet.backoffice.views.reports.flags',
    url(r'^report/(\d+)/flags/thanks', 'thanks',name='flag_success_pro'),
    url(r'^report/(\d+)/flags', 'new',name='flag_report_pro'),
)

urlpatterns +=patterns('django_fixmystreet.backoffice.views.createuser',
	url(r'^createuser','createUser',name='create_user_pro'),
)
urlpatterns += patterns('django_fixmystreet.backoffice.views.categoryGestionnaireConfiguration',
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
)
