from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.template import Context, RequestContext
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.db import transaction


from django_fixmystreet.fixmystreet.models import Report, Status, ReportUpdate, ReportCategory
from django_fixmystreet.fixmystreet.forms import ReportForm, ReportUpdateForm, ReportCommentForm, ReportFileForm

@transaction.commit_on_success
def accept( request, report_id ):
	report = get_object_or_404(Report, id=report_id)
        report.status = Status.objects.get(pk='4') #Gestionnaire is assigned
	report.save()    
	
    	if "pro" in request.path:
        	return HttpResponseRedirect(report.get_absolute_url_pro())
        else:
        	return HttpResponseRedirect(report.get_absolute_url())

def refuse( request, report_id ):
	report = get_object_or_404(Report, id=report_id)
        report.status = Status.objects.get(pk='4') #Refused
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
