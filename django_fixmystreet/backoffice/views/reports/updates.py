from datetime import datetime
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.db import transaction

from django_fixmystreet.fixmystreet.utils import render_to_pdf
from django_fixmystreet.fixmystreet.models import Report, FMSUser, OrganisationEntity, ReportComment, ReportFile
from django_fixmystreet.fixmystreet.forms import ReportCommentForm, ReportFileForm
from django_fixmystreet.backoffice.forms import RefuseForm

@transaction.commit_on_success
def accept( request, report_id ):
    report = get_object_or_404(Report, id=report_id)

    #Update the status and persist to the database
    report.status = Report.MANAGER_ASSIGNED
    report.save()
    #Redirect to the report show page
    if "pro" in request.path:
        return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
        return HttpResponseRedirect(report.get_absolute_url())

def refuse( request, report_id ):
    report = get_object_or_404(Report, id=report_id)
    #Update the status
    report.status = Report.REFUSED
    form = RefuseForm(request)
    #Save the refusal motivation in the database
    report.refusal_motivation = form.data.POST.get('refusal_motivation')
    report.save()
    #Redirect to the report show page
    if "pro" in request.path:
        return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
        return HttpResponseRedirect(report.get_absolute_url())

def fixed( request, report_id ):
    report = get_object_or_404(Report, id=report_id)
    #Update the status
    report.status = Report.SOLVED
    report.save()
    #Redirect to the report show page
    if "pro" in request.path:
        return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
        return HttpResponseRedirect(report.get_absolute_url())


def close( request, report_id ):
    report = get_object_or_404(Report, id=report_id)
    #Update the status and set the close date
    report.status = Report.PROCESSED
    report.close_date = datetime.now()
    report.save()
    #Redirect to the report show page
    if "pro" in request.path:
        return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
        return HttpResponseRedirect(report.get_absolute_url())

def new( request, report_id ):
    report = get_object_or_404(Report, id=report_id)
    if request.method == 'POST':
        if request.POST['form-type'] == u"comment-form":
            comment_form = ReportCommentForm(request.POST)
            if comment_form.is_valid():
                comment_form.save(request.user, report)

        if request.POST['form-type'] == u"file-form":
            if request.POST['title'] == "":
                request.POST['title']= request.FILES.get('file').name
            file_form = ReportFileForm(request.POST,request.FILES)
            if file_form.is_valid:
                file_form.save(request.user, report)

        if "pro" in request.path:
            return HttpResponseRedirect(report.get_absolute_url_pro())
        else:
            return HttpResponseRedirect(report.get_absolute_url())
    raise Http404()


def switchPrivacy(request,report_id):
    report = get_object_or_404(Report, id=report_id)
    privacy = request.REQUEST.get("privacy")
    report.private = ('true' == privacy)
    report.save()
    if "pro" in request.path:
            return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
            return HttpResponseRedirect(report.get_absolute_url())

def changeManager(request,report_id):
    report = Report.objects.get(pk=report_id)
    report.status = Report.MANAGER_ASSIGNED
    manId = request.REQUEST.get("manId")
    if manId.split("_")[0] == "manager":
        newRespMan = FMSUser.objects.get(pk=int(manId.split("_")[1]))
        report.responsible_manager = newRespMan
        report.save()
    if manId.split("_")[0] == "entity":
        orgId = int(manId.split("_")[1])
        report.responsible_entity = OrganisationEntity.objects.get(id=orgId)
        managers = FMSUser.objects.filter(organisation_id = orgId).filter(manager=True)
        for manager in managers:
            if manager.categories.all().filter(id = report.category.id):
                report.responsible_manager = manager
                report.save()
                break

    if "pro" in request.path:
            return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
            return HttpResponseRedirect(report.get_absolute_url())
def changeContractor(request,report_id):
    report = get_object_or_404(Report, id=report_id)
    contractorId = request.REQUEST.get("contractorId")
    if contractorId=='-1':
        report.subcontractor = None
        #Restore status to IN_PROGRESS
        report.status = Report.IN_PROGRESS
    else:
        organisation = OrganisationEntity.objects.get(pk=int(contractorId))
        report.contractor = organisation
        if organisation.subcontractor:
            report.status = Report.CONTRACTOR_ASSIGNED
        else:
            report.status = Report.APPLICANT_RESPONSIBLE

    report.save()
    if "pro" in request.path:
            return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
            return HttpResponseRedirect(report.get_absolute_url())

def reportPdf(request, report_id, pro_version):
    '''reportPdf is called from report details page to generate the pdf with report story. When pro_version == 0 then filter pdf content'''
    report = get_object_or_404(Report, id=report_id)

    #Verify if the connected user is well pro ! (Server side protection)
    # if request.user.fmsuser.is_citizen():
       # pro_Version = 0

    if request.GET.get('output', False):
        return render_to_response("pro/pdf.html", {'user' : request.user.fmsuser,'report' : report, 'file_list' : report.attachments, 'comment_list' : report.attachments, 'activity_list' : report.activities ,'pro_version': pro_version},
                context_instance=RequestContext(request))
    else:
        return render_to_pdf("pro/pdf.html", {'user' : request.user.fmsuser,'report' : report, 'file_list' : report.attachments, 'comment_list' : report.attachment, 'activity_list' : report.activities, 'pro_version' : pro_version},
                context_instance=RequestContext(request))


def acceptAndValidate(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    report.status = Report.MANAGER_ASSIGNED
    report.save()
    comments = ReportComment.objects.filter(report_id=report_id)
    for comment in comments:
        comment.is_validated= True
        comment.save()
    files = ReportFile.objects.filter(report_id=report_id)
    for f in files:
        f.is_validated = True
        f.save()
    if "pro" in request.path:
            return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
            return HttpResponseRedirect(report.get_absolute_url())

def validateAll(request,report_id):
    report = get_object_or_404(Report, id=report_id)
    comments = ReportComment.objects.filter(report_id=report_id)
    files = ReportFile.objects.filter(report_id=report_id)
    for comment in comments:
        comment.is_validated = True
        comment.is_visible = True
        comment.save()
    for f in files:
        f.is_validated = True
        f.is_visible = True
        f.save()
    if "pro" in request.path:
            return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
            return HttpResponseRedirect(report.get_absolute_url())

def updateComment(request,report_id):
    report = get_object_or_404(Report,id=report_id)
    security_level = request.REQUEST.get('updateType')
    comment = ReportComment.objects.get(pk=request.REQUEST.get('commentId'))
    comment.security_level = comment.get_security_level(int(security_level))

    comment.save()
    if "pro" in request.path:
            return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
            return HttpResponseRedirect(report.get_absolute_url())

def updateFile(request,report_id):
    report = get_object_or_404(Report,id=report_id)
    security_level = request.REQUEST.get('updateType')
    f = ReportFile.objects.get(pk=request.REQUEST.get('fileId'))
    f.security_level = f.get_security_level(int(security_level))

    f.save()
    if "pro" in request.path:
            return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
            return HttpResponseRedirect(report.get_absolute_url())
