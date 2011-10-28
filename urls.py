from django.conf.urls.defaults import *
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib import admin
from mainapp.feeds import LatestReports, LatestReportsByCity, LatestReportsByWard, LatestUpdatesByReport
from mainapp.models import City
import mainapp.views.cities as cities

feeds = {
    'reports': LatestReports,
    'wards': LatestReportsByWard,
    'cities': LatestReportsByCity,
    'report_updates': LatestUpdatesByReport,
}

if settings.DEBUG:
    SSL_ON = False
else:
    SSL_ON = True
    
admin.autodiscover()
urlpatterns = patterns('',
    (r'^admin/password_reset/$', 'django.contrib.auth.views.password_reset',{'SSL':SSL_ON}),
    (r'^password_reset/done/$', 'django.contrib.auth.views.password_reset_done'),
    (r'^reset/(?P<uidb36>[-\w]+)/(?P<token>[-\w]+)/$', 'django.contrib.auth.views.password_reset_confirm'),
    (r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete'),
    (r'^admin/', admin.site.urls,{'SSL':SSL_ON}),
    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds},'feeds'),
    (r'^i18n/', include('django.conf.urls.i18n')),
)



urlpatterns += patterns('mainapp.views.main',
    url(r'^$', 'home',name='home'),
    url(r'about/$', 'about',name='about'),
    url(r'posters/$', 'posters',name='posters'),
)

urlpatterns += patterns('mainapp.views.faq',
    (r'^about/(\S+)$', 'show'),
)


urlpatterns += patterns('mainapp.views.promotion',
    (r'^promotions/(\w+)$', 'show'),
)

urlpatterns += patterns('mainapp.views.wards',
    (r'^wards/$', cities.show, {"city_id":1}, 'bxl_wards'), 
    url(r'^wards/(\d+)', 'show',name='ward'),       
    #(r'^cities/(\d+)/wards/(\d+)', 'show_by_number'),
)

#urlpatterns += patterns('',
    #(r'^cities/(\d+)$', cities.show ),
    #(r'^cities', cities.index, {}, 'cities_url_name'),
#)

urlpatterns += patterns( 'mainapp.views.reports.updates',
    url(r'^reports/updates/confirm/(\S+)', 'confirm', name='confirm'), 
    url(r'^reports/updates/create/', 'create', name='update_created'), 
    url(r'^reports/(\d+)/updates/', 'new', name='update_new'),
)


urlpatterns += patterns( 'mainapp.views.reports.subscribers',
    url(r'^reports/subscribers/confirm/(\S+)', 'confirm',name='subscribe_confirm'), 
    url(r'^reports/subscribers/unsubscribe/(\S+)', 'unsubscribe',name='unsubscribe'),
    url(r'^reports/subscribers/create/', 'create', name='subscribe_create'),
    url(r'^reports/(\d+)/subscribers', 'new', name='subscribe'),
)

urlpatterns += patterns( 'mainapp.views.reports.flags',
    url(r'^reports/(\d+)/flags/thanks', 'thanks',name='flag_success'),
    url(r'^reports/(\d+)/flags', 'new',name='flag'),
)

urlpatterns += patterns('mainapp.views.reports.main',
    url(r'^reports/(\d+)$', 'show',name='report_show'),       
    url(r'^reports/new', 'new',name='report_new'),
)

urlpatterns += patterns('mainapp.views.reports.mobile',
    url(r'^mobile/reports/(\d+)$', 'show',name='mobile_report_show'),       
    url(r'^mobile/reports/new', 'new',name='mobile_report_new'),
)

urlpatterns += patterns('mainapp.views.contact',
    (r'^contact/thanks', 'thanks'),
    (r'^contact/', 'new', {}, 'contact'),
)

urlpatterns += patterns('mainapp.views.ajax',
    (r'^ajax/categories/(\d+)', 'category_desc'),
)

urlpatterns += patterns('mainapp.views.api',
    url(r'^api/search/$', 'search',name='api_search'),
    url(r'^api/locate/$', 'locate',name='api_locate'),
    url(r'^api/wards/$', 'wards',name='api_wards'),
    url(r'^api/reports/$', 'reports',name='api_reports'),
)

if settings.DEBUG and 'TESTVIEW' in settings.__dir__():
    urlpatterns += patterns ('',
    (r'^testview',include('django_testview.urls')))


#The following is used to serve up local media files like images
if settings.LOCAL_DEV:
    baseurlregex = r'^media/(?P<path>.*)$'
    urlpatterns += patterns('',
        (
            baseurlregex, 
            'django.views.static.serve',
            {'document_root':  settings.MEDIA_ROOT}
        ),
    )
