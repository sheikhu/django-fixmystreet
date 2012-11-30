from django.conf.urls.defaults import *
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib.auth import views as auth_views
from django.views.generic.simple import direct_to_template
from django_fixmystreet.fixmystreet.feeds import LatestReports, LatestReportsByCity, LatestUpdatesByReport
from django.utils.translation import ugettext_lazy as _

feeds = {
    'report': LatestReports,
    # 'commune': LatestReportsByWard,
    #'city': LatestReportsByCity,
    'report_updates': LatestUpdatesByReport,
}


urlpatterns = patterns('',
    (_(r'^i18n/'), include('django.conf.urls.i18n')),
    (_(r'^feeds/(?P<url>.*)/$'), 'django.contrib.syndication.views.Feed', {'feed_dict': feeds},'feeds'),
)

urlpatterns += patterns('django_fixmystreet.fixmystreet.views.main',
    url(_(r'^$'), 'home',name='home'),
    url(_(r'^about/$'), 'about',name='about'),
    url(_(r'^posters/$'), 'posters',name='posters'),
    url(_(r'^terms_of_use/$'), 'terms_of_use',name='terms_of_use'),
    url(_(r'^robots.txt$'), 'robot'),
)

urlpatterns += patterns('django_fixmystreet.fixmystreet.views.promotion',
    (_(r'^promotions/(\w+)$'), 'show'),
)

# urlpatterns += patterns('django_fixmystreet.fixmystreet.views.wards',
    # (r'^communes/$', cities.show, {"city_id":1}, 'bxl_wards'), 
    # url(r'^commune/(\d+)', 'show',name='ward_show'),
# )

#urlpatterns += patterns('django_fixmystreet.fixmystreet.views.cities',
#    url(r'^city/(\d+)', 'show',name='city_show'),
#)

urlpatterns += patterns('django_fixmystreet.fixmystreet.views.reports.main',
    url(_(r'^reports/$'), 'index',name='report_index'),
    url(_(r'^reports/(?P<slug>.*)/(?P<commune_id>\d+)$'), 'index',name='report_commune_index'),       
    url(_(r'^report/(?P<slug>.*)/(?P<report_id>\d+)$'), 'show',name='report_show'),     
    url(_(r'^report/new'), 'new',name='report_new'),
)

urlpatterns += patterns( 'django_fixmystreet.fixmystreet.views.reports.updates',
    url(_(r'^report/(\d+)/update/'), 'new', name='report_update'),
    url(_(r'^report/(\d+)-(\d+)/pdf/'), 'reportPdf', name='report_pdf'),
)

urlpatterns += patterns( 'django_fixmystreet.fixmystreet.views.reports.subscribers',
    url(_(r'^report/(\d+)/subscribe/'), 'create', name='subscribe'),
)

urlpatterns += patterns( 'django_fixmystreet.fixmystreet.views.reports.flags',
    url(_(r'^report/(\d+)/flags/thanks'), 'thanks',name='flag_success'),
    url(_(r'^report/(\d+)/flags'), 'new',name='flag_report'),
)

urlpatterns += patterns('django_fixmystreet.fixmystreet.views.contact',
    (_(r'^contact/thanks'), 'thanks'),
    (_(r'^contact/'), 'new', {}, 'contact'),
)

urlpatterns += patterns('django_fixmystreet.fixmystreet.views.ajax',

    url(_(r'^ajax/createComment'),'create_comment',name='create_report_comment'),
    url(_(r'^ajax/createFile'),'create_file',name='create_report_file'),
    url(_(r'^ajax/categories/(\d+)'), 'report_category_note',name='report_category_note'),
    url(_(r'^ajax/uploadFile'),'uploadFile',name='report_upload_file'),
    url(_(r'^ajax/update_language/'),'update_last_used_language',name="update_last_used_language"),
)

urlpatterns += patterns('django_fixmystreet.fixmystreet.views.api',
    #next line to be deprecated...
    url(_(r'^api/reports/$'), 'reports_pro',name='api_reports'),
    url(_(r'^api/reports/map/$'), 'reports_pro',name='api_reports'),
    url(_(r'^api/reports/citizen/nearest/$'), 'near_reports_citizen',name='api_reports'),
    url(_(r'^api/reports/pro/nearest/$'), 'near_reports_pro',name='api_reports'),
    url(_(r'^api/reports/citizen/$'), 'reports_citizen',name='api_reports'),
    url(_(r'^api/reports/pro/$'), 'reports_pro',name='api_reports'),
    url(_(r'^api/report/new/$'), 'create_report',name='api_report_new'),
    url(_(r'^api/login/$'),'login_user',name='login_user'),
)

