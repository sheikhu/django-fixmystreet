from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.template import Context, RequestContext
from django.contrib import messages
from django.utils.translation import ugettext as _
from django_fixmystreet.fixmystreet.utils import FixStdImageField, HtmlTemplateMail, render_to_pdf
from django_fixmystreet.fixmystreet.models import Report, ReportCategory, ReportComment, ReportFile
from django_fixmystreet.fixmystreet.forms import ReportForm, ReportCommentForm

def new( request, report_id ):
    report = get_object_or_404(Report, id=report_id)

    if request.method == 'POST':
        update_form = ReportCommentForm(request.POST)
        if update_form.is_valid():
            update = update_form.save(request.user,report,commit=False)
            update.is_fixed = request.POST.has_key('is_fixed')
            update.save()
            messages.add_message(request, messages.SUCCESS, _('The report has been sucessfully updated.'))
        if request.POST.has_key('is_fixed'):
                alreadySolved = (report.status == Report.SOLVED)
                if not alreadySolved:
                    report.status = Report.SOLVED
                    report.save()
                    comments = ReportComment.objects.filter(report_id=report_id)
                    files = ReportFile.objects.filter(report_id=report_id)
                    mail = HtmlTemplateMail(template_dir='send_report_fixed_to_gest_resp', data={'report': report,'comments':comments,'files':files}, recipients=(report.responsible_manager.email,))
                    mail.send()
        return HttpResponseRedirect(report.get_absolute_url())
    raise Http404()


def reportPdf(request, report_id, pro_version):
    '''reportPdf is called from report details page to generate the pdf with report story. When pro_version == 0 then filter pdf content'''
    report = get_object_or_404(Report, id=report_id)

    #Set pro version to 0 per default as this view method should always be called by the citizen version of the webapp
    pro_Version = 0

    if request.GET.get('output', False):
        return render_to_response("pro/pdf.html", {'report' : report, 'file_list' : report.get_files(), 'comment_list' : report.get_comments(), 'pro_version': pro_version},
                context_instance=RequestContext(request))
    else:
        return render_to_pdf("pro/pdf.html", {'report' : report, 'file_list' : report.get_files(), 'comment_list' : report.get_comments(), 'pro_version' : pro_version},
                context_instance=RequestContext(request))

