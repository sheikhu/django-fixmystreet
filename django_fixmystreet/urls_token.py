from django.conf.urls.defaults import url, patterns
from django.utils.translation import ugettext_lazy as _

urlpatterns = patterns(
    '',
    url(_(r'^report/(\d+)/pdf/'), 'django_fixmystreet.fixmystreet.views.reports.updates.report_pdf', {"pro_version": True}, name='report_pdf_pro_token'),
)
