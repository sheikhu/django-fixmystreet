import datetime

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.forms.models import inlineformset_factory
from django.template import RequestContext
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.utils.translation import get_language

from django_fixmystreet.fixmystreet.models import (
    Report, ReportFile, ReportSubscription,
    ZipCode, ReportMainCategoryClass)
from django_fixmystreet.fixmystreet.forms import (
    CitizenReportForm, CitizenForm,
    ReportCommentForm, ReportFileForm)
from django_fixmystreet.fixmystreet.utils import dict_to_point, RequestFingerprint

import logging
logger = logging.getLogger(__name__)


def new(request):
    ReportFileFormSet = inlineformset_factory(Report, ReportFile, form=ReportFileForm, extra=0)

    pnt = dict_to_point(request.REQUEST)
    report = None
    file_formset = ReportFileFormSet(prefix='files', queryset=ReportFile.objects.none())

    if request.method == "POST":
        report_form = CitizenReportForm(request.POST, request.FILES, prefix='report')
        comment_form = ReportCommentForm(request.POST, request.FILES, prefix='comment')
        citizen_form = CitizenForm(request.POST, request.FILES, prefix='citizen')

        fingerprint = RequestFingerprint(request)

        # this checks update is_valid too
        if report_form.is_valid() and (not request.POST["comment-text"] or comment_form.is_valid()) and citizen_form.is_valid() and not fingerprint.is_duplicate():
            # this saves the update as part of the report.
            report = report_form.save(commit=False)

            file_formset = ReportFileFormSet(request.POST, request.FILES, instance=report, prefix='files', queryset=ReportFile.objects.none())

            if file_formset.is_valid():
                fingerprint.save()

                citizen = citizen_form.save()

                report.citizen = citizen
                report.quality = citizen_form.cleaned_data["quality"]
                report.save()

                if report_form.cleaned_data['subscription']:
                    report.subscribe_author()

                if request.POST["comment-text"]:
                    comment = comment_form.save(commit=False)
                    comment.created_by = citizen
                    comment.report = report
                    comment.save()

                files = file_formset.save(commit=False)
                for report_file in files:
                    report_file.created_by = citizen
                    #report_file.report = report
                    report_file.save()
                messages.add_message(request, messages.SUCCESS, _("Newly created report successfull"))
                return HttpResponseRedirect(report.get_absolute_url())

            else:
                report = None

    else:
        report_form = CitizenReportForm(initial={
            'x': request.REQUEST.get('x'),
            'y': request.REQUEST.get('y')
        }, prefix='report')
        file_formset = ReportFileFormSet(prefix='files', queryset=ReportFile.objects.none())
        comment_form = ReportCommentForm(prefix='comment')
        citizen_form = CitizenForm(prefix='citizen')

    return render_to_response("reports/new.html", {
        "report": report,
        "available_zips": ZipCode.objects,
        "all_zips": ZipCode.objects.all(),
        "category_classes": ReportMainCategoryClass.objects.prefetch_related('categories').all().order_by('name_' + get_language()),
        "comment_form": comment_form,
        "file_formset": file_formset,
        "report_form": report_form,
        "citizen_form": citizen_form,
        "pnt": pnt
    }, context_instance=RequestContext(request))


def verify(request):
    pnt = dict_to_point(request.REQUEST)
    reports_nearby = Report.objects.all().visible().public().near(pnt, 20).related_fields()[0:6]

    if reports_nearby:
        return render_to_response("reports/verify.html", {
            "reports_nearby": reports_nearby
        }, context_instance=RequestContext(request))

    return new(request)


def show(request, slug, report_id):
    report = get_object_or_404(Report, id=report_id, private=False)

    if report.citizen:
        user_to_show = report.citizen
    else:
        user_to_show = report.created_by

    return render_to_response("reports/show.html", {
        "report": report,
        "subscribed": request.user.is_authenticated() and ReportSubscription.objects.filter(report=report, subscriber=request.user).exists(),
        "author": user_to_show,
        'activity_list': report.activities.all(),
    }, context_instance=RequestContext(request))


def document(request, slug, report_id):
    ReportFileFormSet = inlineformset_factory(Report, ReportFile, form=ReportFileForm, extra=0)
    report = get_object_or_404(Report, id=report_id)

    if request.method == "POST":
        comment = None
        comment_form = ReportCommentForm(request.POST, request.FILES, prefix='comment')
        file_formset = ReportFileFormSet(request.POST, request.FILES, instance=report, prefix='files', queryset=ReportFile.objects.none())
        citizen_form = CitizenForm(request.POST, request.FILES, prefix='citizen')

        # this checks update is_valid too
        if file_formset.is_valid() and (not request.POST["comment-text"] or comment_form.is_valid()) and citizen_form.is_valid():
            # this saves the update as part of the report.
            citizen = citizen_form.save()

            if request.POST["comment-text"] and len(request.POST["comment-text"]) > 0:
                comment = comment_form.save(commit=False)
                comment.report = report
                comment.created_by = citizen
                comment.save()

            files = file_formset.save()

            for report_file in files:
                report_file.created_by = citizen
                report_file.save()

            # if request.POST.get("citizen_subscription", False):
            #     ReportSubscription(report=report, subscriber=report.created_by).save()

            report.trigger_updates_added(files=files, comment=comment, user=citizen)

            messages.add_message(request, messages.SUCCESS, _("You attachments has been sent"))
            return HttpResponseRedirect(report.get_absolute_url())
    else:
        file_formset = ReportFileFormSet(prefix='files', queryset=ReportFile.objects.none())
        comment_form = ReportCommentForm(prefix='comment')
        citizen_form = CitizenForm(prefix='citizen')

    return render_to_response("reports/document.html", {
        "report": report,
        "subscribed": request.user.is_authenticated() and ReportSubscription.objects.filter(report=report, subscriber=request.user).exists(),
        "file_formset": file_formset,
        "comment_form": comment_form,
        "citizen_form": citizen_form,
    }, context_instance=RequestContext(request))

def update(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    # if 'is_fixed' in request.REQUEST:
    #     #Update the status of report
    #     report.status   = Report.SOLVED
    #     report.fixed_at = datetime.datetime.now()
    #     report.save()
    #
    #     if "pro" in request.path:
    #         return HttpResponseRedirect(report.get_absolute_url_pro())
    #     else:
    #         return HttpResponseRedirect(report.get_absolute_url())

    # ????? DEPRECATED ?????
    if request.method == 'POST':
        if request.POST['form-type'] == u"comment-form":
            comment_form = ReportCommentForm(request.POST)
            if comment_form.is_valid():
                comment_form.save(request.user, report)

        if request.POST['form-type'] == u"file-form":
            #set default title if not given
            fileTitle = request.POST.get("title")
            if (fileTitle == ""):
                request.POST.__setitem__("title", request.FILES.get('file').name)
            file_form = ReportFileForm(request.POST, request.FILES)
            if file_form.is_valid:
                file_form.save(request.user, report)

        if "pro" in request.path:
            return HttpResponseRedirect(report.get_absolute_url_pro())
        else:
            return HttpResponseRedirect(report.get_absolute_url())
    raise Http404()


def search_ticket(request):
    try:
        report_id = request.REQUEST.get('report_id')

        if hasattr(request, 'fmsuser') and request.fmsuser.is_pro():
            report = Report.objects.get(id=report_id)

            return HttpResponseRedirect(report.get_absolute_url_pro())

        report = Report.objects.get(id=report_id, private=False)
        return HttpResponseRedirect(report.get_absolute_url())

    except (Report.DoesNotExist, ValueError):
        messages.add_message(request, messages.ERROR, _("No incident found with this ticket number"))
        return HttpResponseRedirect(reverse('home'))


def index(request):
    return render_to_response("reports/reports_map.html", {
        'zipcodes': ZipCode.objects.filter(hide=False).order_by('name_' + get_language())
    }, context_instance=RequestContext(request))
