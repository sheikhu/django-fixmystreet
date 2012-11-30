from django.conf.urls.defaults import *
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib.auth import views as auth_views
from django.views.generic.simple import direct_to_template
from django.utils.translation import ugettext_lazy as _

# from django_fixmystreet.backoffice.views.users import CreateUser

urlpatterns = patterns('django_fixmystreet.backoffice.views.main',
    url(_(r'^$'), 'home',name='home_pro'),
)

urlpatterns += patterns('',
	url(_(r'^accounts/login/$'), 'django.contrib.auth.views.login', {'template_name': 'pro/login.html'},name='login'),
	url(_(r'^logout/$'),
            auth_views.logout_then_login,
            {'login_url':'/pro/accounts/login/?next=/pro/'},
            name='auth_logout'
    ),
)


urlpatterns += patterns('django_fixmystreet.backoffice.views.reports.main',
    url(_(r'^report/(?P<slug>[\w-]+)(?P<report_id>\d+)$'), 'show',name='report_show_pro'),
    url(_(r'^report/new'), 'new',name='report_new_pro'),
    url(_(r'^report/subscription'), 'subscription',name='report_subscription_pro'),
)

urlpatterns += patterns('django_fixmystreet.backoffice.views.reports.list',
    url(_(r'^report/list/(.+)'), 'list',name='report_list_pro'),
)

urlpatterns += patterns( 'django_fixmystreet.backoffice.views.reports.updates',
    url(_(r'^report/(\d+)/update/'), 'new', name='report_update_pro'),
    url(_(r'^report/(\d+)/accept/'), 'accept', name='report_accept_pro'),
    url(_(r'^report/(\d+)/refuse/'), 'refuse', name='report_refuse_pro'),
    url(_(r'^report/(\d+)/fixed/'), 'fixed', name='report_fix_pro'),
    url(_(r'^report/(\d+)/close/'), 'close', name='report_close_pro'),
    url(_(r'^report/(\d+)/updateFile'), 'updateFile', name='report_update_file'),
    url(_(r'^report/(\d+)/updateComment'), 'updateComment', name='report_update_comment'),
    url(_(r'^report/(\d+)/fixed/'), 'fixed', name='report_fix_pro'),
    url(_(r'^report/(\d+)/changeManager/'), 'changeManager', name='report_change_manager_pro'),
    url(_(r'^report/(\d+)/changeContractor/'), 'changeContractor', name='report_change_contractor_pro'),
    url(_(r'^report/(\d+)/accept_and_validate/'), 'acceptAndValidate', name='report_accept_and_validate'),
    url(_(r'^report/(\d+)-(\d+)/pdf/'), 'reportPdf', name='report_pdf_pro'),
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
    url(_(r'^categoryGestionnaireConfiguration/dialog/'),'update',name='gestionnaire_selection_dialog'),
    url(_(r'^categoryGestionnaireConfiguration'),'show',name='category_gestionnaire_configuration'),

)

urlpatterns += patterns('django_fixmystreet.backoffice.views.ajax',
    url(_(r'^ajax/saveSelection'),'saveCategoryConfiguration',name='saveSelection'),
)

urlpatterns +=patterns('django_fixmystreet.backoffice.views.users',
    url(_(r'users/overview/delete'),'deleteUser',name="userDelete"),
    url(_(r'users/overview/edit'),'edit',name='usersEdit'),
    url(_(r'users/overview/save'),'saveChanges',name="userSave"),
    url(_(r'users/overview'),'show',name='usersOverview'),
	url(_(r'^createuser'),'createUser',name='create_user_pro'),
)
