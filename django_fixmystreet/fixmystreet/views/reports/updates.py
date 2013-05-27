from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django_fixmystreet.fixmystreet.utils import render_to_pdf
from django_fixmystreet.fixmystreet.models import Report
from django.core.exceptions import PermissionDenied


def report_pdf(request, report_id, pro_version=False):
    '''reportPdf is called from report details page to generate the pdf with report story. When pro_version == 0 then filter pdf content'''
    report = get_object_or_404(Report, id=report_id)

    if pro_version and not (request.user.is_authenticated() and request.fmsuser.is_pro()):
        raise PermissionDenied

    #Set pro version to 0 per default as this view method should always be called by the citizen version of the webapp
    # pro_Version = 0

    return render_to_pdf("reports/pdf.html", {
        'report' : report,
        'files': report.files() if pro_version else report.active_files(),
        'comments': report.comments() if pro_version else report.active_comments(),
        'activity_list' : report.activities.all(),
        'privacy' : 'private'  if pro_version else 'public'
    }, context_instance=RequestContext(request))
