from django.conf.urls.defaults import *
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic.simple import direct_to_template

from fixmystreet.feeds import LatestReports, LatestReportsByCity, LatestReportsByWard, LatestUpdatesByReport
from fixmystreet.models import City
from fixmystreet.views import cities

feeds = {
    'reports': LatestReports,
    'communes': LatestReportsByWard,
    'cities': LatestReportsByCity,
    'report_updates': LatestUpdatesByReport,
}

if settings.DEBUG:
    SSL_ON = False
else:
    SSL_ON = True
    
admin.autodiscover()
urlpatterns = patterns('',
    (r'^admin/', admin.site.urls,{'SSL':SSL_ON}),
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds},'feeds'),
    url(r'^', include('social_auth.urls')),
    url(r'^logout/$',
            auth_views.logout_then_login,
            {'login_url':'/'},
            name='auth_logout'
    ),
    url(r'^login-callback/$', direct_to_template, {'template': 'login-callback.html'}),
)

urlpatterns += patterns('fixmystreet.views.main',
    url(r'^$', 'home',name='home'),
    url(r'^about/$', 'about',name='about'),
    url(r'^posters/$', 'posters',name='posters'),
    url(r'^terms_of_use/$', 'terms_of_use',name='terms_of_use'),
    url(r'^robots.txt$', 'robot'),
)

urlpatterns += patterns('fixmystreet.views.faq',
    (r'^about/(\S+)$', 'show'),
)


urlpatterns += patterns('fixmystreet.views.promotion',
    (r'^promotions/(\w+)$', 'show'),
)

urlpatterns += patterns('fixmystreet.views.wards',
    (r'^communes/$', cities.show, {"city_id":1}, 'bxl_wards'), 
    url(r'^commune/(\d+)', 'show',name='ward_show'),
)

urlpatterns += patterns('fixmystreet.views.reports.main',
    url(r'^report/(\d+)$', 'show',name='report_show'),       
    url(r'^report/new', 'new',name='report_new'),
)

urlpatterns += patterns( 'fixmystreet.views.reports.updates',
    url(r'^report/(\d+)/update/', 'new', name='report_update'),
)

urlpatterns += patterns( 'fixmystreet.views.reports.subscribers',
    url(r'^report/(\d+)/subscribe/', 'create', name='subscribe'),
    url(r'^report/(\d+)/unsubscribe/', 'unsubscribe',name='unsubscribe'),
)

urlpatterns += patterns( 'fixmystreet.views.reports.flags',
    url(r'^report/(\d+)/flags/thanks', 'thanks',name='flag_success'),
    url(r'^report/(\d+)/flags', 'new',name='flag_report'),
)

urlpatterns += patterns('fixmystreet.views.reports.mobile',
    url(r'^mobile/report/(\d+)$', 'show',name='mobile_report_show'),       
    url(r'^mobile/report/new', 'new',name='mobile_report_new'),
)

urlpatterns += patterns('fixmystreet.views.contact',
    (r'^contact/thanks', 'thanks'),
    (r'^contact/', 'new', {}, 'contact'),
)

urlpatterns += patterns('fixmystreet.views.ajax',
    (r'^ajax/categories/(\d+)', 'category_desc'),
)

urlpatterns += patterns('fixmystreet.views.api',
    url(r'^api/search/$', 'search',name='api_search'),
    url(r'^api/locate/$', 'locate',name='api_locate'),
    #url(r'^api/wards/$', 'wards',name='api_wards'),
    url(r'^api/reports/$', 'reports',name='api_reports'),
    url(r'^api/report/new/$', 'create_report',name='api_report_new'),
)

