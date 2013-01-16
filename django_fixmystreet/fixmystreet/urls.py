from django.conf.urls.defaults import patterns, url
from django_fixmystreet.fixmystreet.feeds import LatestReports, LatestUpdatesByReport
from django.utils.translation import ugettext_lazy as _
from piston.resource import Resource

from django_fixmystreet.fixmystreet.export_piston import ReportHandler
from django_fixmystreet.fixmystreet.views.api import CitizenReportHandler

feeds = {
    'report': LatestReports,
    # 'commune': LatestReportsByWard,
    #'city': LatestReportsByCity,
    'report_updates': LatestUpdatesByReport,
}


urlpatterns = patterns('',
    (_(r'^feeds/(?P<url>.*)/$'), 'django.contrib.syndication.views.Feed', {'feed_dict': feeds},'feeds'),
)

urlpatterns += patterns('django_fixmystreet.fixmystreet.views.main',
    url(_(r'^$'), 'home',name='home'),
    url(_(r'^about/$'), 'about',name='about'),
    url(_(r'^posters/$'), 'posters',name='posters'),
    url(_(r'^terms-of-use/$'), 'terms_of_use',name='terms_of_use'),
    url(_(r'^update-language/'),'update_current_language',name="update_current_language"),

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
    url(_(r'^report/search_ticket'), 'search_ticket',name='search_ticket'),
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

    url(_(r'^ajax/create-comment'),'create_comment',name='create_report_comment'),
    url(_(r'^ajax/create-file'),'create_file',name='create_report_file'),
    url(_(r'^ajax/categories/(\d+)'), 'report_category_note',name='report_category_note'),
    url(_(r'^ajax/upload-file'),'uploadFile',name='report_upload_file'),
)

citizen_report_handler = Resource(CitizenReportHandler)

urlpatterns += patterns('django_fixmystreet.fixmystreet.views.api',
    #next line to be deprecated...
    url(_(r'^api/reports/$'), 'reports_pro',name='api_reports'),
    url(_(r'^api/reports/mobile/$'), 'reports_pro_mobile',name='api_reports'),
    url(_(r'^api/reports/map/$'), 'reports_pro',name='api_reports'),
    url(_(r'^api/reports/citizen/nearest/$'), 'near_reports_citizen',name='api_reports'),
    url(_(r'^api/reports/pro/nearest/$'), 'near_reports_pro',name='api_reports'),
    url(_(r'^api/reports/citizen/$'), 'reports_citizen',name='api_reports'),
    url(_(r'^api/reports/pro/$'), 'reports_pro',name='api_reports'),	
    #url(_(r'^api/report/new/$'), 'create_report',name='api_report_new'),
    url(_(r'^api/login/$'),'login_user',name='login_user'),
    url(_(r'^api/load_categories/$'),'load_categories',name='load_categories'),
    url(_(r'^api/load_zipcodes/$'),'load_zipcodes',name='load_zipcodes'),
    url(_(r'^api/create_report_citizen/$'),citizen_report_handler,name='create_report_citizen'),
    url(_(r'^api/create_report_pro/$'),'create_report_pro',name='create_report_pro'),
    url(_(r'^api/create_report_photo/$'),'create_report_photo',name='create_report_photo'),
)

urlpatterns += patterns('django_fixmystreet.fixmystreet.views.import',
    url(_(r'^import/report/close/$'), 'close_report',name='close_report'),
    url(_(r'^import/report/change_manager/$'), 'change_manager_report',name='change_manager_report'),
)

urlpatterns += patterns('django_fixmystreet.fixmystreet.views.export',
    url(_(r'^export/reports/entity/$'), 'entity_reports',name='entity_reports'),
    url(_(r'^export/reports/contractor/$'), 'contractor_reports',name='contractor_reports'),
    url(_(r'^export/reports/manager/$'), 'manager_reports',name='manager_reports'),
)

urlpatterns += patterns('django_fixmystreet.fixmystreet.export_piston',
    url(_(r'^export_file/reports/((?P<emitter_format>.+))/'), Resource(ReportHandler)),
)
