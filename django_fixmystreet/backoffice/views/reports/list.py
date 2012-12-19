from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django_fixmystreet.fixmystreet.models import dictToPoint, Report, FMSUser
from django_fixmystreet.fixmystreet.forms import ReportForm
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

@login_required(login_url='/pro/accounts/login/')
def list(request, status):
    default_position = {
        'x': '148954.431',
        'y': '170458.371'
    }

    if 'x' in request.REQUEST and 'y' in request.REQUEST:
        pnt = dictToPoint(request.REQUEST)
    else:
        pnt = dictToPoint(default_position)

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
            'x': request.REQUEST.get('x', default_position['x']),
            'y': request.REQUEST.get('y', default_position['y'])
        })
   
    connectedUser = FMSUser.objects.get(pk=request.user.id)
    user_organisation = connectedUser.organisation
    
    #if the user is an executeur de travaux then user the dependent organisation id
    if (connectedUser.contractor == True):
        user_organisation = user_organisation.dependency

    #reports = Report.objects.distance(pnt).order_by('distance')[0:10]

    if status == 'created':
    	reports = Report.objects.filter(responsible_entity=user_organisation).filter(status=Report.CREATED)
    elif status == 'in_progress':
    	reports = Report.objects.filter(responsible_entity=user_organisation).filter(status__in=Report.REPORT_STATUS_IN_PROGRESS)
    elif status == 'closed':
    	reports = Report.objects.filter(responsible_entity=user_organisation).filter(status__in=Report.REPORT_STATUS_CLOSED)
    else: # all
        reports = Report.objects.filter(responsible_entity=user_organisation).all()
  
    #if the user is an executeur de travaux then display only report where He is responsible
    if (connectedUser.contractor == True):
        reports = reports.filter(contractor = connectedUser.organisation)

    #reports = reports.distance(pnt).order_by('distance')
    reports = reports.distance(pnt).order_by('address', 'address_number')
    return render_to_response("pro/reports/list.html",
            {
                "report_form": report_form,
                "pnt":pnt,
                "reports":reports,
                "status":status,
            },
            context_instance=RequestContext(request))
