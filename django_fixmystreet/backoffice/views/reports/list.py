from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django_fixmystreet.fixmystreet.models import dictToPoint, Report, ReportSubscription, ReportFile, ReportComment, OrganisationEntity, FMSUser
from django_fixmystreet.fixmystreet.forms import ReportForm, ReportFileForm,ReportCommentForm
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

@login_required(login_url='/pro/accounts/login/')
def list(request):
    pnt = dictToPoint(request.REQUEST)
    if request.method == "POST":
        report_form = ReportForm(request.POST, request.FILES)
        # this checks update is_valid too
        if report_form.is_valid():
            # this saves the update as part of the report.
            report = report_form.save(request.user)
            if report:
            	if "pro" in request.path:
                	return HttpResponseRedirect(report.get_absolute_url_pro())
                else:
                	return HttpResponseRedirect(report.get_absolute_url())
    else:
        report_form = ReportForm(initial={
            'x': request.REQUEST.get('x'),
            'y': request.REQUEST.get('y')
        })
   
    user_organisation = FMSUser.objects.get(pk=request.user.id).organisation
    #reports = Report.objects.distance(pnt).order_by('distance')[0:10]
    statusQ = request.REQUEST.get('status', 'all')
    if statusQ == 'created':
    	reports = Report.objects.filter(responsible_entity=user_organisation).filter(status=Report.CREATED)
    elif statusQ == 'in_progress':
    	reports = Report.objects.filter(responsible_entity=user_organisation).filter(status__in=Report.REPORT_STATUS_IN_PROGRESS)
    elif statusQ == 'closed':
    	reports = Report.objects.filter(responsible_entity=user_organisation).filter(status__in=Report.REPORT_STATUS_CLOSED)
    else:
        reports = Report.objects.filter(responsible_entity=user_organisation).all()
    #import pdb
    #pdb.set_trace()
    reports = reports.distance(pnt).order_by('distance')
    return render_to_response("pro/reports/list.html",
            {
                "report_form": report_form,
                "pnt":pnt,
                "reports":reports
            },
            context_instance=RequestContext(request))
