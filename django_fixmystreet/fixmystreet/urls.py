from django.conf.urls.defaults import *
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib.auth import views as auth_views
from django.views.generic.simple import direct_to_template

from django_fixmystreet.fixmystreet.feeds import LatestReports, LatestReportsByCity, LatestReportsByWard, LatestUpdatesByReport
from django_fixmystreet.fixmystreet.models import City
from django_fixmystreet.fixmystreet.views import cities

feeds = {
    'report': LatestReports,
    'commune': LatestReportsByWard,
    'city': LatestReportsByCity,
    'report_updates': LatestUpdatesByReport,
}


urlpatterns = patterns('',
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.Feed', {'feed_dict': feeds},'feeds'),
    url(r'^', include('social_auth.urls')),
    url(r'^logout/$',
            auth_views.logout_then_login,
            {'login_url':'/'},
            name='auth_logout'
    ),
    url(r'^login-callback/$', direct_to_template, {'template': 'login-callback.html'}),
)

urlpatterns += patterns('django_fixmystreet.fixmystreet.views.main',
    url(r'^$', 'home',name='home'),
    url(r'^about/$', 'about',name='about'),
    url(r'^posters/$', 'posters',name='posters'),
    url(r'^terms_of_use/$', 'terms_of_use',name='terms_of_use'),
    url(r'^robots.txt$', 'robot'),
)

urlpatterns += patterns('django_fixmystreet.fixmystreet.views.promotion',
    (r'^promotions/(\w+)$', 'show'),
)

urlpatterns += patterns('django_fixmystreet.fixmystreet.views.wards',
    (r'^communes/$', cities.show, {"city_id":1}, 'bxl_wards'), 
    url(r'^commune/(\d+)', 'show',name='ward_show'),
)

urlpatterns += patterns('django_fixmystreet.fixmystreet.views.cities',
    url(r'^city/(\d+)', 'show',name='city_show'),
)

urlpatterns += patterns('django_fixmystreet.fixmystreet.views.reports.main',
    url(r'^report/(\d+)$', 'show',name='report_show'),       
    url(r'^report/new', 'new',name='report_new'),
)

urlpatterns += patterns( 'django_fixmystreet.fixmystreet.views.reports.updates',
    url(r'^report/(\d+)/update/', 'new', name='report_update'),
)

urlpatterns += patterns( 'django_fixmystreet.fixmystreet.views.reports.subscribers',
    url(r'^report/(\d+)/subscribe/', 'create', name='subscribe'),
    url(r'^report/(\d+)/unsubscribe/', 'unsubscribe',name='unsubscribe'),
)

urlpatterns += patterns( 'django_fixmystreet.fixmystreet.views.reports.flags',
    url(r'^report/(\d+)/flags/thanks', 'thanks',name='flag_success'),
    url(r'^report/(\d+)/flags', 'new',name='flag_report'),
)

urlpatterns += patterns('django_fixmystreet.fixmystreet.views.contact',
    (r'^contact/thanks', 'thanks'),
    (r'^contact/', 'new', {}, 'contact'),
)

urlpatterns += patterns('django_fixmystreet.fixmystreet.views.ajax',
    (r'^ajax/categories/(\d+)', 'category_desc'),
)

urlpatterns += patterns('django_fixmystreet.fixmystreet.views.api',
    url(r'^api/reports/$', 'reports',name='api_reports'),
    url(r'^api/report/new/$', 'create_report',name='api_report_new'),
)

