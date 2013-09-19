
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.forms.models import inlineformset_factory
from django.template import RequestContext
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.utils.translation import get_language

from django_fixmystreet.fixmystreet.stats import ReportCountStatsPro, ReportCountQuery
from django_fixmystreet.fixmystreet.models import ZipCode, Report, ReportSubscription, ReportFile, OrganisationEntity, FMSUser
from django_fixmystreet.fixmystreet.utils import dict_to_point, RequestFingerprint
from django_fixmystreet.fixmystreet.forms import ProReportForm, ReportFileForm, ReportCommentForm, MarkAsDoneForm, ReportMainCategoryClass
from django_fixmystreet.backoffice.forms import  RefuseForm

def new(request):
    pnt = dict_to_point(request.REQUEST)
    ReportFileFormSet = inlineformset_factory(Report, ReportFile, form=ReportFileForm, extra=0)
    report = None
    if request.method == "POST":
        report_form = ProReportForm(request.POST, request.FILES, prefix='report')
        comment_form = ReportCommentForm(request.POST, request.FILES, prefix='comment')

        fingerprint = RequestFingerprint(request)

        # this checks update is_valid too
        if report_form.is_valid() and (not request.POST["comment-text"] or comment_form.is_valid()) and not fingerprint.is_duplicate():
            # this saves the update as part of the report.
            report = report_form.save(commit=False)

            file_formset = ReportFileFormSet(request.POST, request.FILES, instance=report, prefix='files', queryset=ReportFile.objects.none())
            if file_formset.is_valid():
                fingerprint.save()

                report.save()

                if request.POST["comment-text"]:
                    comment = comment_form.save(commit=False)
                    comment.report = report
                    comment.save()
                file_formset.save()
                # messages.add_message(request, messages.SUCCESS, _("Newly created report successfull"))
                # return HttpResponseRedirect(report.get_absolute_url_pro())
            else:
                report = None

    else:
        report_form = ProReportForm(initial={
            'x': request.REQUEST.get('x'),
            'y': request.REQUEST.get('y')
        }, prefix='report')

    file_formset = ReportFileFormSet(prefix='files', queryset=ReportFile.objects.none())
    comment_form = ReportCommentForm(prefix='comment')

    reports = Report.objects.all().distance(pnt).filter(point__distance_lte=(pnt, 150)).pending().order_by('distance')
    return render_to_response("pro/reports/new.html",
            {
                "report":report,
                "all_zips":ZipCode.objects.all(),
                "category_classes":ReportMainCategoryClass.objects.prefetch_related('categories').all(),
                "report_form": report_form,
                "pnt":pnt,
                "reports":reports,
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

        popup_reports = Report.objects.created_between(start_date, end_date)

        if str(request.GET["stat_status"]) == 'unpublished':
            popup_reports = popup_reports.created()
        elif str(request.GET["stat_status"])== 'in_progress':
            popup_reports = popup_reports.in_progress()
        else:
            popup_reports = popup_reports.closed()

    return render_to_response("pro/home.html",
            {
                "report_counts": ReportCountQuery('1 year'),
                'search_error': error_msg,
                'zipcodes': zipcodes,
                'location':location,
                'reports_created': Report.objects.all().created().order_by('-modified')[0:5],
                'reports_in_progress': Report.objects.all().in_progress().order_by('-modified')[0:5],
                'reports_closed':Report.objects.all().closed().order_by('-modified')[0:5],
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

def delete(request,slug, report_id):
    report = get_object_or_404(Report, id=report_id, responsible_manager=request.fmsuser)
    report.status = Report.DELETED
    report.save()
    messages.add_message(request, messages.ERROR, _("Report successfully deleted"))
    return HttpResponseRedirect(reverse('home_pro'))



def show(request,slug, report_id):
    ReportFileFormSet = inlineformset_factory(Report, ReportFile, form=ReportFileForm, extra=0)

    report = get_object_or_404(Report, id=report_id)

    if request.method == "POST":
        file_formset = ReportFileFormSet(request.POST, request.FILES, instance=report, prefix='files', queryset=ReportFile.objects.none())
        comment_form = ReportCommentForm(request.POST, request.FILES, prefix='comment')
        comment = None
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

            files = file_formset.save()

            report.trigger_updates_added(request.fmsuser, files=files, comment=comment)

            messages.add_message(request, messages.SUCCESS, _("You attachments has been sent"))
            return HttpResponseRedirect(report.get_absolute_url_pro())

    else:
        file_formset = ReportFileFormSet(prefix='files', queryset=ReportFile.objects.none())
        comment_form = ReportCommentForm(prefix='comment')

    organisation = request.fmsuser.organisation

    managers = FMSUser.objects.filter(organisation = organisation).filter(manager=True)

    region_institution = OrganisationEntity.objects.filter(region=True).filter(active=True)
    entities = OrganisationEntity.objects.filter(commune=True).filter(active=True)
    if organisation:
        entities.exclude(pk=organisation.id)
        contractors = organisation.associates.filter(subcontractor=True)
    else:
        contractors = OrganisationEntity.objects.filter(subcontractor=True)

    applicants = OrganisationEntity.objects.filter(applicant=True)
    pnt = report.point
    nearby_reports = Report.objects.all().distance(pnt).filter(point__distance_lte=(pnt, 250)).order_by('distance').exclude(id=report.id)
    return render_to_response("pro/reports/show.html",
            {
                "fms_user": request.fmsuser,
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
                "mark_as_done_form":MarkAsDoneForm(),
                'activity_list' : report.activities.all(),
                'attachment_edit': request.fmsuser == report.responsible_manager and (report.is_created() or report.is_in_progress()),
                "nearby_reports":nearby_reports
            },
            context_instance=RequestContext(request))
