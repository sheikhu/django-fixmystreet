from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.template import Context, RequestContext
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.db import transaction
from django_fixmystreet.fixmystreet.utils import FixStdImageField, HtmlTemplateMail, render_to_pdf
from django.contrib.auth.models import User
from django_fixmystreet.fixmystreet.models import Report, ReportSubscription, ReportCategory, FMSUser, OrganisationEntity, ReportComment, ReportFile
from django_fixmystreet.fixmystreet.forms import ReportForm, ReportCommentForm, ReportFileForm

@transaction.commit_on_success
def accept( request, report_id ):
	report = get_object_or_404(Report, id=report_id)
        report.status = Report.MANAGER_ASSIGNED
	report.save()    
	
    	if "pro" in request.path:
        	return HttpResponseRedirect(report.get_absolute_url_pro())
        else:
        	return HttpResponseRedirect(report.get_absolute_url())

def refuse( request, report_id ):
    report = get_object_or_404(Report, id=report_id)
    report.status = Report.REFUSED
    report.save()
    creator = None
    if report.created_by:
        creator = report.created_by
    else:
        creator = report.citizen
    if "pro" in request.path:
        return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
        return HttpResponseRedirect(report.get_absolute_url())

def fixed( request, report_id ):
	report = get_object_or_404(Report, id=report_id)
        report.status = Report.SOLVED
	report.save()    	

	if "pro" in request.path:
       		return HttpResponseRedirect(report.get_absolute_url_pro())
       	else:
       		return HttpResponseRedirect(report.get_absolute_url())

def close( request, report_id ):
    report = get_object_or_404(Report, id=report_id)
    report.status = Report.PROCESSED
    report.save()
    subscriptions = ReportSubscription.objects.filter(report_id=report_id)
    mailto = ['']*len(subscriptions)
    i =0
    for reportsubscription in subscriptions:
        mailto[i] = User.objects.get(pk=reportsubscription.subscriber_id).email
        i = i+1
    comments = ReportComment.objects.filter(report_id=report_id)
    files = ReportFile.objects.filter(report_id=report_id)
    mail = HtmlTemplateMail(template_dir='send_report_closed_to_subscribers', data={'report': report,'comments':comments,'files':files}, recipients=tuple(mailto))
    mail.send()
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
        if organisation.is_subcontractor() == True:
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
    if request.user.fmsuser.is_citizen():
       pro_Version = 0
    
    if request.GET.get('output', False):
        return render_to_response("pro/pdf.html", {'report' : report, 'file_list' : report.get_files(), 'comment_list' : report.get_comments(), 'pro_version': pro_version},
                context_instance=RequestContext(request))
    else:
        return render_to_pdf("pro/pdf.html", {'report' : report, 'file_list' : report.get_files(), 'comment_list' : report.get_comments(), 'pro_version' : pro_version},
                context_instance=RequestContext(request))

def acceptAndValidate(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    report.status = Report.MANAGER_ASSIGNED
    report.save()
    comments = ReportComment.objects.filter(report_id=report_id)
    for comment in comments:
        comment.validated= True
        comment.save()
    files = ReportFile.objects.filter(report_id=report_id)
    for f in files:
        f.validated = True
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
        comment.validated = True
        comment.save()
    for f in files:
        f.validated = True
        f.save()
    if "pro" in request.path:
            return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
            return HttpResponseRedirect(report.get_absolute_url())

def updateComment(request,report_id):
    report = get_object_or_404(Report,id=report_id)
    updateType = request.REQUEST.get('updateType')
    comment = ReportComment.objects.get(pk=request.REQUEST.get('commentId'))
    if updateType == "valid":
        comment.validated= (request.REQUEST.get('updateValue')=='checked')
        if comment.validated:
            comment.isVisible= True
    if updateType == 'confidential':
        comment.isVisible = not (request.REQUEST.get('updateValue')=='checked')
        if (comment.isVisible == False):
            comment.validated = False #When setting element to confidential then it becomes unvalidated automatically
    
    comment.save()
    if "pro" in request.path:
            return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
            return HttpResponseRedirect(report.get_absolute_url())

def updateFile(request,report_id):
    report = get_object_or_404(Report,id=report_id)
    updateType = request.REQUEST.get('updateType')
    f = ReportFile.objects.get(pk=request.REQUEST.get('fileId'))
    if updateType == "valid":
        f.validated= (request.REQUEST.get('updateValue')=='checked')
        if f.validated:
            f.isVisible= True
    if updateType == 'confidential':
        f.isVisible = not (request.REQUEST.get('updateValue')=='checked')
        if (f.isVisible == False):
            f.validated = False #When setting element to confidential then it becomes unvalidated automatically
    f.save()
    if "pro" in request.path:
            return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
            return HttpResponseRedirect(report.get_absolute_url())
