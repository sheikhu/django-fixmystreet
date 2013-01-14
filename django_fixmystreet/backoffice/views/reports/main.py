from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django_fixmystreet.fixmystreet.models import ZipCode, dictToPoint, Report, ReportSubscription, ReportFile, ReportComment, OrganisationEntity, FMSUser
from django_fixmystreet.fixmystreet.forms import ProReportForm, ReportFileForm, ReportCommentForm, FileUploadForm, MarkAsDoneForm
from django_fixmystreet.backoffice.forms import  RefuseForm
from django.template import RequestContext
from django_fixmystreet.fixmystreet.session_manager import SessionManager
from django.conf import settings


def new(request):
    pnt = dictToPoint(request.REQUEST)
    if request.method == "POST":
        report_form = ProReportForm(request.POST, request.FILES)
        # this checks update is_valid too
        if report_form.is_valid():
            # this saves the update as part of the report.
            report = report_form.save(request.user)
            SessionManager.saveComments(request.session, report)
            SessionManager.saveFiles(request.session, report)
            if report:
                if request.backoffice:
                    return HttpResponseRedirect(report.get_absolute_url_pro())
                else:
                    return HttpResponseRedirect(report.get_absolute_url())
    else:
        SessionManager.clearSession(request.session)
        report_form = ProReportForm(initial={
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

    return render_to_response("pro/reports/new.html",
            {
                "available_zips":ZipCode.objects.all(),
                "report_form": report_form,
                "pnt":pnt,
                "reports":reports,
                "file_upload_Form":FileUploadForm()
            },
            context_instance=RequestContext(request))


def search_ticket(request):
    report_id = request.REQUEST.get('report_id')
    report = Report.objects.get(id=report_id)

    return HttpResponseRedirect(report.get_absolute_url_pro())

def subscription(request):
    """
    Method used to load all my subscription reports
    """
    subscriptions = ReportSubscription.objects.filter(subscriber_id = request.user.id)
    reports = [None]*len(subscriptions)
    i = 0
    for subscription in subscriptions:
        reports[i] = Report.objects.get(pk=subscription.report_id)
        i= i+1
    return render_to_response("pro/reports/subscriptions.html",
            {
              "reports":reports
            },
            context_instance=RequestContext(request))

def show(request,slug, report_id):
    if request.GET.get("page"):
        page_number= int(request.GET.get("page"))
    else :
        page_number=1
    report = get_object_or_404(Report, id=report_id)
    files = ReportFile.objects.filter(report_id=report_id)
    comments = ReportComment.objects.filter(report_id=report_id)
    organisationId = FMSUser.objects.get(pk=request.user.id).organisation_id
    managers = FMSUser.objects.filter(organisation_id = organisationId).filter(manager=True)

    entitiesHavingAManager = FMSUser.objects.filter(manager=True);
    entities = OrganisationEntity.objects.exclude(pk=organisationId).filter(commune=True).filter(id__in=entitiesHavingAManager)
    contractors = OrganisationEntity.objects.filter(dependency_id=organisationId).filter(subcontractor=True)
    applicants = OrganisationEntity.objects.filter(applicant=True)
    reports = Report.objects.all()
    pages_list = range(1,int((len(reports)/settings.MAX_ITEMS_PAGE)+2))
    fms_user = FMSUser.objects.get(pk=request.user.id)
    return render_to_response("pro/reports/show.html",
            {
                "reports":reports[int((page_number-1)*settings.MAX_ITEMS_PAGE):int(page_number*settings.MAX_ITEMS_PAGE)],
                "fms_user": fms_user,
                "report": report,
                "subscribed": request.user.is_authenticated() and ReportSubscription.objects.filter(report=report, subscriber=request.user).exists(),
                "comment_form": ReportCommentForm(),
                "file_form":ReportFileForm(),
                "files":files,
                "comments":comments,
                "managers":managers,
                "contractors":contractors,
                "applicants":applicants,
                "entities":entities,
                "refuse_form": RefuseForm(instance=report),
                "pages_list":pages_list,
                "mark_as_done_form":MarkAsDoneForm(),
            },
            context_instance=RequestContext(request))
