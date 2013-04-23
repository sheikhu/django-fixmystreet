from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django_fixmystreet.fixmystreet.utils import render_to_pdf
from django_fixmystreet.fixmystreet.models import Report




#DEPRECATED ??? USE TH EONE IN BACKOFFICE???
def reportPdf(request, report_id, pro_version):
    '''reportPdf is called from report details page to generate the pdf with report story. When pro_version == 0 then filter pdf content'''
    report = get_object_or_404(Report, id=report_id)


    #Set pro version to 0 per default as this view method should always be called by the citizen version of the webapp
    # pro_Version = 0
    if request.GET.get('output', False):
        return render_to_response("pro/pdf.html", {
            'report' : report,
            'file_list' : report.files(),
            'comment_list' : report.comments(),
            'activity_list' : report.activities.all(),
            'pro_version' : pro_version
        }, context_instance=RequestContext(request))
    else:
        return render_to_pdf("pro/pdf.html", {'report' : report,  'file_list' : report.files(), 'comment_list' : report.comments(), 'activity_list' : report.activities.all(), 'pro_version' : pro_version},
                context_instance=RequestContext(request))
