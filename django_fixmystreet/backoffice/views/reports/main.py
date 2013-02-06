import math

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.forms.models import inlineformset_factory
from django_fixmystreet.fixmystreet.models import ZipCode, dictToPoint, Report, ReportSubscription, ReportFile, OrganisationEntity, FMSUser
from django_fixmystreet.fixmystreet.forms import ProReportForm, ReportFileForm, ReportCommentForm, MarkAsDoneForm, ReportMainCategoryClass
from django_fixmystreet.backoffice.forms import  RefuseForm
from django.template import RequestContext
from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from django.utils.translation import get_language
from django_fixmystreet.fixmystreet.stats import ReportCountStatsPro, ReportCountQuery


def new(request):
    pnt = dictToPoint(request.REQUEST)
    ReportFileFormSet = inlineformset_factory(Report, ReportFile, form=ReportFileForm, extra=0)
    report = None
    if request.method == "POST":
        report_form = ProReportForm(request.POST, request.FILES, prefix='report')
        comment_form = ReportCommentForm(request.POST, request.FILES, prefix='comment')

        # this checks update is_valid too
        if report_form.is_valid() and (not request.POST["comment-text"] or comment_form.is_valid()):
            # this saves the update as part of the report.
            report = report_form.save(commit=False)

            file_formset = ReportFileFormSet(request.POST, request.FILES, instance=report, prefix='files', queryset=ReportFile.objects.none())
            if file_formset.is_valid():
                report.save()

                if request.POST["comment-text"]:
                    comment = comment_form.save(commit=False)
                    comment.report = report
                    comment.save()
                file_formset.save()

    else:
        report_form = ProReportForm(initial={
            'x': request.REQUEST.get('x'),
            'y': request.REQUEST.get('y')
        }, prefix='report')

    file_formset = ReportFileFormSet(prefix='files', queryset=ReportFile.objects.none())
    comment_form = ReportCommentForm(prefix='comment')

    connectedUser = request.fmsuser

    #if the user is an contractor then user the dependent organisation id
    if (connectedUser.contractor == True or connectedUser.applicant == True):
        #if the user is an contractor then display only report where He is responsible
        reports = Report.objects.filter(contractor__in = connectedUser.work_for.all())
    else:
        reports = Report.objects.filter(responsible_entity = connectedUser.organisation)

    #If the manager is connected then filter on manager
    if (connectedUser.manager == True):
        reports = reports.filter(responsible_manager=connectedUser);

    reports = reports.distance(pnt).filter(point__distance_lte=(pnt, 1000)).order_by('distance')
    return render_to_response("pro/reports/new.html",
            {
                "report":report,
                "all_zips":ZipCode.objects.all(),
                "category_classes":ReportMainCategoryClass.objects.prefetch_related('categories').all(),
                "report_form": report_form,
                "pnt":pnt,
                "reports":reports[0:5],
                "file_formset":file_formset,
                "comment_form":comment_form,
            },
            context_instance=RequestContext(request))


def report_prepare_pro(request, location = None, error_msg = None):
    '''Used to redirect the user to welcome without processing home view controller method. This controller method contain a few redirection logic'''
    zipcodes = ZipCode.objects.filter(hide=False).order_by('name_'+get_language())
    statsObject = ReportCountStatsPro()
    stats_result = statsObject.get_result()
    stats = statsObject.get_stats()
    popup_reports = []
    if "stat_type" in request.GET:
        start_date = stats[str(request.GET["stat_type"])]["start_date"]
        end_date = stats[str(request.GET["stat_type"])]["end_date"]
        if str(request.GET["stat_status"]) == 'unpublished':
            popup_reports = Report.objects.filter(status=Report.CREATED).filter(created__gt=str(start_date)).filter(created__lt=str(end_date))
        elif str(request.GET["stat_status"])== 'in_progress':
            popup_reports = Report.objects.filter(status__in=Report.REPORT_STATUS_IN_PROGRESS).filter(created__gt=str(start_date)).filter(created__lt=str(end_date))
        else:
            popup_reports = Report.objects.filter(status__in=Report.REPORT_STATUS_CLOSED).filter(created__gt=str(start_date)).filter(created__lt=str(end_date))

    return render_to_response("pro/home.html",
            {
                "report_counts": ReportCountQuery('1 year'),
                'search_error': error_msg,
                'zipcodes': zipcodes,
                'location':location,
                'reports':Report.objects.all(),
                'reports_created': Report.objects.filter(status=Report.CREATED).order_by('-modified')[0:5],
                'reports_in_progress': Report.objects.filter(status__in=Report.REPORT_STATUS_IN_PROGRESS).order_by('-modified')[0:5],
                'reports_closed':Report.objects.filter(status__in=Report.REPORT_STATUS_CLOSED).order_by('-modified')[0:5],
                'stats':stats_result,
                'popup_reports':popup_reports,
            },
            context_instance=RequestContext(request))

def search_ticket_pro(request):
    report_id = request.REQUEST.get('report_id')
    try:
        report = Report.objects.get(id=report_id)
        return HttpResponseRedirect(report.get_absolute_url_pro()+"?page=1")
    except:
        messages.add_message(request, messages.ERROR, _("No incident found with this ticket number"))
        return HttpResponseRedirect(reverse('home_pro'))

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
    ReportFileFormSet = inlineformset_factory(Report, ReportFile, form=ReportFileForm, extra=0)

    page_number = int(request.GET.get("page", 1))
    report = get_object_or_404(Report, id=report_id)

    if request.method == "POST":
        file_formset = ReportFileFormSet(request.POST, request.FILES, instance=report, prefix='files', queryset=ReportFile.objects.none())
        comment_form = ReportCommentForm(request.POST, request.FILES, prefix='comment')
        # citizen_form = CitizenForm(request.POST, request.FILES, prefix='citizen')
        # this checks update is_valid too
        if file_formset.is_valid() and (not request.POST["comment-text"] or comment_form.is_valid()): # and citizen_form.is_valid():
            # this saves the update as part of the report.
            # citizen = citizen_form.save()
            if request.POST["comment-text"] and len(request.POST["comment-text"]) > 0:
                    comment = comment_form.save(commit=False)
                    comment.created_by = FMSUser.objects.get(pk=request.user.id)
                    comment.report = report
                    comment.save()

            file_formset.save()

    else:
        file_formset = ReportFileFormSet(prefix='files', queryset=ReportFile.objects.none())
        comment_form = ReportCommentForm(prefix='comment')

    organisationId = FMSUser.objects.get(pk=request.user.id).organisation_id

    managers = FMSUser.objects.filter(organisation_id = organisationId).filter(manager=True)
    fms_managers = FMSUser.objects.filter(manager=True).values_list('organisation', flat=True);
    entitiesHavingManager = OrganisationEntity.objects.filter(id__in=fms_managers).values_list('pk', flat=True)

    region_institution = OrganisationEntity.objects.filter(region=True).filter(id__in=entitiesHavingManager)
    entities = OrganisationEntity.objects.exclude(pk=organisationId).filter(commune=True).filter(id__in=entitiesHavingManager)

    contractors = OrganisationEntity.objects.filter(dependency_id=organisationId).filter(subcontractor=True)
    applicants = OrganisationEntity.objects.filter(applicant=True)

    connectedUser = request.fmsuser

    #if the user is an contractor then user the dependent organisation id
    if (connectedUser.contractor == True or connectedUser.applicant == True):
        #if the user is an contractor then display only report where He is responsible
        reports = Report.objects.filter(contractor__in = connectedUser.work_for.all())
    else:
        reports = Report.objects.filter(responsible_entity = connectedUser.organisation)

    #If the manager is connected then filter on manager
    if (connectedUser.manager == True):
        reports = reports.filter(responsible_manager=connectedUser);

    reports = reports.order_by('-created')

    pages_list = range(1,int(math.ceil(len(reports)/settings.MAX_ITEMS_PAGE))+1+int(len(reports)%settings.MAX_ITEMS_PAGE != 0))
    fms_user = FMSUser.objects.get(pk=request.user.id)
    return render_to_response("pro/reports/show.html",
            {
                "reports":reports[int((page_number-1)*settings.MAX_ITEMS_PAGE):int(page_number*settings.MAX_ITEMS_PAGE)],
                "fms_user": fms_user,
                "report": report,
                "subscribed": request.user.is_authenticated() and ReportSubscription.objects.filter(report=report, subscriber=request.user).exists(),
                "comment_form": comment_form,
                "file_formset":file_formset,
                "region_institution":region_institution,
                "managers":managers,
                "contractors":contractors,
                "applicants":applicants,
                "entities":entities,
                "refuse_form": RefuseForm(instance=report),
                "pages_list":pages_list,
                "mark_as_done_form":MarkAsDoneForm(),
                "page_number": page_number,
                'activity_list' : report.activities.all(),
            },
            context_instance=RequestContext(request))
