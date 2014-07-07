from datetime import datetime, timedelta

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
from django_fixmystreet.fixmystreet.forms import ProReportForm, ReportFileForm, ReportCommentForm, ReportMainCategoryClass
from django_fixmystreet.backoffice.forms import PriorityForm


DEFAULT_TIMEDELTA_PRO = {"days": -30}
DEFAULT_SQL_INTERVAL_PRO = "30 days"
REPORTS_MAX_RESULTS = 4


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
                user = FMSUser.objects.get(pk=request.user.id)

                fingerprint.save()

                report.save()

                if report_form.cleaned_data['subscription']:
                    report.subscribe_author()

                if request.POST["comment-text"]:
                    comment = comment_form.save(commit=False)
                    comment.report = report
                    comment.created_by = user
                    comment.save()

                files = file_formset.save()

                for report_file in files:
                    report_file.created_by = user
                    report_file.save()

                messages.add_message(request, messages.SUCCESS, _("Newly created report successfull"), extra_tags="new_report")
                return HttpResponseRedirect(report.get_absolute_url_pro())
            else:
                report = None

    else:
        report_form = ProReportForm(initial={
            'x': request.REQUEST.get('x'),
            'y': request.REQUEST.get('y')
        }, prefix='report')

    file_formset = ReportFileFormSet(prefix='files', queryset=ReportFile.objects.none())
    comment_form = ReportCommentForm(prefix='comment')

    # reports_nearby = Report.objects.all().visible().unfinished()
    # reports_nearby = reports_nearby.near(pnt, 150).related_fields()

    return render_to_response("pro/reports/new.html", {
        "report": report,
        "all_zips": ZipCode.objects.all(),
        "category_classes": ReportMainCategoryClass.objects.prefetch_related('categories').all(),
        "report_form": report_form,
        "pnt": pnt,
        # "reports": Report.objects.all().visible(),
        "file_formset": file_formset,
        "comment_form": comment_form,
        # "reports_nearby": reports_nearby
    }, context_instance=RequestContext(request))


def report_prepare_pro(request, location=None, error_msg=None):
    '''Used to redirect the user to welcome without processing home view controller method. This controller method contain a few redirection logic'''
    zipcodes = ZipCode.objects.filter(hide=False).order_by('name_' + get_language())
    statsObject = ReportCountStatsPro()
    stats_result = statsObject.get_result()
    stats = statsObject.get_stats()
    popup_reports = []

    if "stat_type" in request.GET:
        start_date = stats[str(request.GET["stat_type"])]["start_date"]
        end_date = stats[str(request.GET["stat_type"])]["end_date"]

        popup_reports = Report.objects.all().visible().related_fields().created_between(start_date, end_date)

        if str(request.GET["stat_status"]) == 'unpublished':
            popup_reports = popup_reports.created()
        elif str(request.GET["stat_status"]) == 'in_progress':
            popup_reports = popup_reports.in_progress()
        else:
            popup_reports = popup_reports.closed()

    last_30_days = datetime.today() + timedelta(**DEFAULT_TIMEDELTA_PRO)

    # Queryset common to all reports
    qs = Report.objects.all().visible() \
         .extra(select={"has_thumbnail_pro": "CASE WHEN fixmystreet_report.thumbnail_pro IS NULL OR fixmystreet_report.thumbnail_pro = '' THEN 0 ELSE 1 END"}) \
         .related_fields().order_by('-has_thumbnail_pro', '-modified')

    return render_to_response("pro/home.html", {
        "report_counts": ReportCountQuery(interval=DEFAULT_SQL_INTERVAL_PRO),
        'search_error': error_msg,
        'zipcodes': zipcodes,
        'all_zipcodes': ZipCode.objects.all(),
        'location': location,
        'reports_created': qs.filter(status=Report.CREATED, created__gte=last_30_days)[:REPORTS_MAX_RESULTS],
        'reports_in_progress': qs.filter(status__in=Report.REPORT_STATUS_IN_PROGRESS, modified__gte=last_30_days)[:REPORTS_MAX_RESULTS],
        'reports_closed': qs.filter(status=Report.PROCESSED, close_date__gte=last_30_days)[:REPORTS_MAX_RESULTS],
        'stats': stats_result,
        'popup_reports': popup_reports,
    }, context_instance=RequestContext(request))


def search_ticket_pro(request):
    report_id = request.REQUEST.get('report_id')
    try:
        report = Report.objects.get(id=report_id)
        return HttpResponseRedirect(report.get_absolute_url_pro())
    except:
        messages.add_message(request, messages.ERROR, _("No incident found with this ticket number"))
        return HttpResponseRedirect(reverse('home_pro'))


# DEPRECATED ??? is it used somwhere ??
def subscription(request):
    """
    Method used to load all my subscription reports
    """
    reports = Report.objects.filter(subscriptions__subscriber_id=request.user.id).related_fields()

    return render_to_response("pro/reports/subscriptions.html", {
        "reports": reports
    }, context_instance=RequestContext(request))


def delete(request, slug, report_id):
    report = get_object_or_404(Report, id=report_id, responsible_manager=request.fmsuser)
    report.status = Report.DELETED
    report.save()
    messages.add_message(request, messages.ERROR, _("Report successfully deleted"))
    return HttpResponseRedirect(reverse('home_pro'))


def show(request, slug, report_id):
    ReportFileFormSet = inlineformset_factory(Report, ReportFile, form=ReportFileForm, extra=0)

    report = get_object_or_404(Report, id=report_id)
    if request.method == "POST":
        file_formset = ReportFileFormSet(request.POST, request.FILES, instance=report, prefix='files', queryset=ReportFile.objects.none())
        comment_form = ReportCommentForm(request.POST, request.FILES, prefix='comment')
        comment = None

        # this checks update is_valid too
        if file_formset.is_valid() and (not request.POST["comment-text"] or comment_form.is_valid()):
            # this saves the update as part of the report.

            user = FMSUser.objects.get(pk=request.user.id)
            if request.POST["comment-text"] and len(request.POST["comment-text"]) > 0:
                comment = comment_form.save(commit=False)
                comment.created_by = user
                comment.report = report
                comment.save()

            files = file_formset.save()

            for report_file in files:
                report_file.created_by = user
                report_file.save()

            report.trigger_updates_added(files=files, comment=comment, user=request.fmsuser)

            messages.add_message(request, messages.SUCCESS, _("You attachments has been sent"))
            return HttpResponseRedirect(report.get_absolute_url_pro())

    else:
        file_formset = ReportFileFormSet(prefix='files', queryset=ReportFile.objects.none())
        comment_form = ReportCommentForm(prefix='comment')

    organisation = request.fmsuser.organisation
    managers = FMSUser.objects.filter(organisation=organisation).filter(manager=True).order_by('name_' + get_language())
    region_institution = OrganisationEntity.objects.filter(type=OrganisationEntity.REGION).filter(active=True).order_by('name_' + get_language())
    entities = OrganisationEntity.objects.filter(type=OrganisationEntity.COMMUNE).filter(active=True).order_by('name_' + get_language())
    departments = []
    contractors = []

    if organisation:
        entities.exclude(pk=organisation.id)
        departments = organisation.associates.all().filter(type=OrganisationEntity.DEPARTMENT).order_by('name_' + get_language())
        contractors = organisation.associates.filter(type=OrganisationEntity.SUBCONTRACTOR).order_by('name_' + get_language())
    else:
        contractors = OrganisationEntity.objects.filter(type=OrganisationEntity.SUBCONTRACTOR).order_by('name_' + get_language())

    applicants = OrganisationEntity.objects.filter(type=OrganisationEntity.APPLICANT).order_by('name_' + get_language())

    can_edit_attachment = (
        report.is_in_progress and
        request.fmsuser.memberships.filter(organisation=report.responsible_department).exists() and
        (report.is_created() or report.is_in_progress()))

    return render_to_response("pro/reports/show.html", {
        "fms_user": request.fmsuser,
        "report": report,
        "subscribed": request.user.is_authenticated() and ReportSubscription.objects.filter(report=report, subscriber=request.user).exists(),
        "comment_form": comment_form,
        "file_formset": file_formset,
        "region_institution": region_institution,
        "managers": managers,
        "departments": departments,
        "contractors": contractors,
        "applicants": applicants,
        "entities": entities,
        "refuse_form": ReportCommentForm(),
        "mark_as_done_form": ReportCommentForm(),
        "priority_form": PriorityForm(instance=report),
        'activity_list': report.activities.all(),
        'attachment_edit': can_edit_attachment,
        "category_list": ReportMainCategoryClass.objects.all().order_by('name_' + get_language()),
    }, context_instance=RequestContext(request))


def verify(request):
    pnt = dict_to_point(request.REQUEST)
    reports_nearby = Report.objects.all().visible().related_fields()
    reports_nearby = reports_nearby.near(pnt, 20)[0:6]

    if reports_nearby:
        return render_to_response("reports/verify.html", {
            "reports_nearby": reports_nearby
        }, context_instance=RequestContext(request))

    return new(request)


def document(request, slug, report_id):
    ReportFileFormSet = inlineformset_factory(Report, ReportFile, form=ReportFileForm, extra=0)
    report = get_object_or_404(Report, id=report_id)

    if request.method == "POST":
        comment = None
        comment_form = ReportCommentForm(request.POST, request.FILES, prefix='comment')
        file_formset = ReportFileFormSet(request.POST, request.FILES, instance=report, prefix='files', queryset=ReportFile.objects.none())

        # this checks update is_valid too
        if file_formset.is_valid() and (not request.POST["comment-text"] or comment_form.is_valid()):
            # this saves the update as part of the report.

            user = FMSUser.objects.get(pk=request.user.id)

            if request.POST["comment-text"] and len(request.POST["comment-text"]) > 0:
                comment = comment_form.save(commit=False)
                comment.report = report
                comment.created_by = user
                comment.save()

            files = file_formset.save()

            for report_file in files:
                report_file.created_by = user
                report_file.save()

            report.trigger_updates_added(files=files, comment=comment, user=request.fmsuser)

            messages.add_message(request, messages.SUCCESS, _("You attachments has been sent"))
            return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
        file_formset = ReportFileFormSet(prefix='files', queryset=ReportFile.objects.none())
        comment_form = ReportCommentForm(prefix='comment')

    return render_to_response("reports/document.html", {
        "report": report,
        "subscribed": request.user.is_authenticated() and ReportSubscription.objects.filter(report=report, subscriber=request.user).exists(),
        "file_formset": file_formset,
        "comment_form": comment_form,
    }, context_instance=RequestContext(request))


def merge(request, slug, report_id):
    report = get_object_or_404(Report, id=report_id)
    pnt = report.point

    reports_nearby = Report.objects.all().visible().related_fields().near(pnt, 250).exclude(id=report.id)
    if report.is_created():
        reports_nearby = reports_nearby.exclude(status=Report.CREATED)
    elif report.is_closed():
        reports_nearby = reports_nearby.exclude(status__in=Report.REPORT_STATUS_CLOSED)

    return render_to_response("pro/reports/merge.html", {
        "fms_user": request.fmsuser,
        "report": report,
        "reports_nearby": reports_nearby,
    }, context_instance=RequestContext(request))
