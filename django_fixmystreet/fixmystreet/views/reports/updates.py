from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django_fixmystreet.fixmystreet.utils import render_to_pdf
from django_fixmystreet.fixmystreet.models import Report
from django_fixmystreet.fixmystreet.forms import ReportCommentForm, ReportFileForm

def new( request, report_id ):
    report = get_object_or_404(Report, id=report_id)
    if request.REQUEST.has_key('is_fixed'):
        report.status = Report.SOLVED
        report.save()
        if "pro" in request.path:
            return HttpResponseRedirect(report.get_absolute_url_pro())
        else:
            return HttpResponseRedirect(report.get_absolute_url())
    if request.method == 'POST':
        if request.POST['form-type'] == u"comment-form":
            comment_form = ReportCommentForm(request.POST)
            if comment_form.is_valid():
                comment_form.save(request.user, report)
        
        if request.POST['form-type'] == u"file-form":
            #set default title if not given
            fileTitle = request.POST.get("title")
            if (fileTitle == ""):
                  request.POST.__setitem__("title",request.FILES.get('file').name)
            file_form = ReportFileForm(request.POST,request.FILES)
            if file_form.is_valid:
                file_form.save(request.user, report)
        
        if "pro" in request.path:
            return HttpResponseRedirect(report.get_absolute_url_pro())
        else:
            return HttpResponseRedirect(report.get_absolute_url())
    raise Http404()


def reportPdf(request, report_id, pro_version):
    '''reportPdf is called from report details page to generate the pdf with report story. When pro_version == 0 then filter pdf content'''
    report = get_object_or_404(Report, id=report_id)

    #Set pro version to 0 per default as this view method should always be called by the citizen version of the webapp
    # pro_Version = 0

    if request.GET.get('output', False):
        return render_to_response("pro/pdf.html", {
            'report' : report
        }, context_instance=RequestContext(request))
    else:
        return render_to_pdf("pro/pdf.html", {'report' : report, 'pro_version' : pro_version},
                context_instance=RequestContext(request))

