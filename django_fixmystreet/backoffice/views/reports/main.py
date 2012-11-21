from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django_fixmystreet.fixmystreet.models import dictToPoint, Report, ReportSubscription, ReportFile, ReportComment, ReportAttachment, OrganisationEntity, FMSUser
from django_fixmystreet.fixmystreet.forms import ReportForm, ReportFileForm,ReportCommentForm
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

@login_required(login_url='/pro/accounts/login/')
def new(request):
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
    
    #reports = Report.objects.distance(pnt).order_by('distance')[0:10]
    statusQ = request.REQUEST.get('status')
    if statusQ == 'created':
    	reports = Report.objects.filter(status=Report.CREATED)
    elif statusQ == 'in_progress':
    	reports = Report.objects.filter(status__in=Report.REPORT_STATUS_IN_PROGRESS)
    elif statusQ == 'off':
    	reports = Report.objects.filter(status__in=Report.REPORT_STATUS_OFF)
    else:
        reports = Report.objects.all()

    reports = reports.distance(pnt).order_by('distance')

    return render_to_response("reports/new_pro.html",
            {
                "report_form": report_form,
                "pnt":pnt,
                "reports":reports
            },
            context_instance=RequestContext(request))

#Method used to load all my subscription reports
@login_required(login_url='/pro/accounts/login/')
def subscription(request):
    subscriptions = ReportSubscription.objects.filter(subscriber_id = request.user.id)
    reports = [None]*len(subscriptions)
    i = 0
    for subscription in subscriptions:
        reports[i] = Report.objects.get(pk=subscription.report_id)
        i= i+1
    return render_to_response("reports/subscriptions.html",
            {
              "reports":reports  
            },
            context_instance=RequestContext(request))



@login_required(login_url='/pro/accounts/login/')
def show(request, report_id):
    report = get_object_or_404(Report, id=report_id)


@login_required(login_url='/pro/accounts/login/')
def show(request, report_id):
    report = get_object_or_404(Report, id=report_id)



@login_required(login_url='/pro/accounts/login/')
def show(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    files= File.objects.filter(report_id=report_id)
    comments = Comment.objects.filter(report_id=report_id)
    organisationId = FMSUser.objects.get(pk=request.user.id).organisation_id
    managers = FMSUser.objects.filter(organisation_id = organisationId).filter(manager=True)
    entities = OrganisationEntity.objects.exclude(pk=organisationId).filter(commune=True)
    contractors = OrganisationEntity.objects.filter(subcontractor=True)
    contractors = list(contractors) + list(OrganisationEntity.objects.filter(applicant=True))
    return render_to_response("reports/show_pro.html",
            {
                "report": report,
                "subscribed": request.user.is_authenticated() and ReportSubscription.objects.filter(report=report, subscriber=request.user).exists(),
                # "update_form": ReportUpdateForm(),
                "comment_form": ReportCommentForm(),
                "file_form":ReportFileForm(),
                "files":files,
                "comments":comments,
                "managers":managers,
                "contractors":contractors,
                "entities":entities
            },
            context_instance=RequestContext(request))
