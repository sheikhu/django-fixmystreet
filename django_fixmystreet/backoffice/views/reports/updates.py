from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.template import Context, RequestContext
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.db import transaction

from django_fixmystreet.fixmystreet.models import Report, Status, ReportCategory, FMSUser, OrganisationEntity, ReportComment, ReportFile
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

	if "pro" in request.path:
       		return HttpResponseRedirect(report.get_absolute_url_pro())
       	else:
       		return HttpResponseRedirect(report.get_absolute_url())

def fixed( request, report_id ):
	report = get_object_or_404(Report, id=report_id)
        report.status = Status.objects.get(pk='7') #Refused
	report.save()    	

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
    contractorId = contractorId.split("_")[1]
    if contractorId=='':
        report.subcontractor = None
    else:
        organisation = OrganisationEntity.objects.get(pk=int(contractorId))
        report.subcontractor = organisation
    report.save()
    if "pro" in request.path:
            return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
            return HttpResponseRedirect(report.get_absolute_url())
def acceptAndValidate(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    report.status = Status.objects.get(pk='4') #Gestionnaire is assigned
    report.save()
    comments = Comment.objects.filter(report_id=report_id)
    for comment in comments:
        comment.validated= True
        comment.save()
    files = File.objects.filter(report_id=report_id)
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
    comment = Comment.objects.get(pk=request.REQUEST.get('commentId'))
    print request.REQUEST
    if updateType == "valid":
        comment.validated= (request.REQUEST.get('updateValue')=='checked')
        if comment.validated:
            comment.isVisible= True
    if updateType == 'confidential':
        comment.isVisible = not (request.REQUEST.get('updateValue')=='checked')
    comment.save()
    if "pro" in request.path:
            return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
            return HttpResponseRedirect(report.get_absolute_url())

def updateFile(request,report_id):
    report = get_object_or_404(Report,id=report_id)
    updateType = request.REQUEST.get('updateType')
    f = File.objects.get(pk=request.REQUEST.get('fileId'))
    if updateType == "valid":
        f.validated= (request.REQUEST.get('updateValue')=='checked')
        if f.validated:
            f.isVisible= True
    if updateType == 'confidential':
        f.isVisible = not (request.REQUEST.get('updateValue')=='checked')
    f.save()
    if "pro" in request.path:
            return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
            return HttpResponseRedirect(report.get_absolute_url())
