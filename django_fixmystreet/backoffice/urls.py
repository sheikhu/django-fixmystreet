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
)

urlpatterns += patterns( 'django_fixmystreet.backoffice.views.reports.updates',
    url(r'^report/(\d+)/update/', 'new', name='report_update_pro'),
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
	url(r'^createuser/agent','createAgent',name='create_agent_user_pro'),
	url(r'^createuser/entity','createEntity',name='create_entity_user_pro'),
	url(r'^createuser/gestionnaire','createGestionnaire',name='create_gestionnaire_user_pro'),
	url(r'^createuser/executeur','createExecuteur',name='create_executeur_user_pro'),
	url(r'^createuser/impetrant','createImpetrant',name='create_impetrant_user_pro'),
)