
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.forms.models import inlineformset_factory
from django.template import RequestContext
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.utils.translation import get_language
from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from django_fixmystreet.fixmystreet.models import Report, ReportFile, ReportSubscription, OrganisationEntity, ZipCode, ReportMainCategoryClass
from django_fixmystreet.fixmystreet.forms import CitizenReportForm, CitizenForm, ReportCommentForm, ReportFileForm, MarkAsDoneForm
from django_fixmystreet.fixmystreet.utils import dict_to_point, RequestFingerprint

import logging
logger = logging.getLogger(__name__)

def new(request):
    ReportFileFormSet = inlineformset_factory(Report, ReportFile, form=ReportFileForm, extra=0)

    pnt = dict_to_point(request.REQUEST)
    report=None
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
                # messages.add_message(request, messages.SUCCESS, _("Newly created report successfull"))
                # return HttpResponseRedirect(report.get_absolute_url_pro())
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

    reports = Report.objects.all().distance(pnt).filter(point__distance_lte=(pnt, 150)).order_by('distance').public()

    return render_to_response("reports/new.html",
            {
                "report":report,
                "available_zips":ZipCode.objects,
                "all_zips":ZipCode.objects.all(),
                "category_classes":ReportMainCategoryClass.objects.prefetch_related('categories').all().order_by('name_'+ get_language()),
                "comment_form":comment_form,
                "file_formset":file_formset,
                "report_form": report_form,
                "citizen_form": citizen_form,
                "pnt":pnt,
                "reports":reports
            },
            context_instance=RequestContext(request))


def report_prepare(request, location = None, error_msg = None):
    '''Deprecated, no sense'''
    return HttpResponseRedirect(reverse('home'))


def show(request, slug, report_id):
    ReportFileFormSet = inlineformset_factory(Report, ReportFile, form=ReportFileForm, extra=0)
    report = get_object_or_404(Report, id=report_id)
    if report.citizen:
        user_to_show = report.citizen
    else:
        user_to_show = report.created_by

    if request.method == "POST":
        comment = None
        comment_form = ReportCommentForm(request.POST, request.FILES, prefix='comment')
        file_formset = ReportFileFormSet(request.POST, request.FILES, instance=report, prefix='files', queryset=ReportFile.objects.none())
        # citizen_form = CitizenForm(request.POST, request.FILES, prefix='citizen')
        # this checks update is_valid too
        if file_formset.is_valid() and (not request.POST["comment-text"] or comment_form.is_valid()): # and citizen_form.is_valid():
            # this saves the update as part of the report.
            # citizen = citizen_form.save()

            if request.POST["comment-text"] and len(request.POST["comment-text"]) > 0:
                comment = comment_form.save(commit=False)
                comment.report = report
                comment.save()

            files = file_formset.save()

            # if request.POST.get("citizen_subscription", False):
            #     ReportSubscription(report=report, subscriber=report.created_by).save()

            report.trigger_updates_added(files=files, comment=comment)

            messages.add_message(request, messages.SUCCESS, _("You attachments has been sent"))
            return HttpResponseRedirect(report.get_absolute_url())
    else:
        file_formset = ReportFileFormSet(prefix='files', queryset=ReportFile.objects.none())
        comment_form = ReportCommentForm(prefix='comment')
        # citizen_form = CitizenForm(prefix='citizen')        

    return render_to_response("reports/show.html",
            {
                "report": report,
                "subscribed": request.user.is_authenticated() and ReportSubscription.objects.filter(report=report, subscriber=request.user).exists(),
                "author": user_to_show,
                "file_formset": file_formset,
                "comment_form": comment_form,
                "mark_as_done_form":MarkAsDoneForm(),
                'activity_list' : report.activities.all(),
            },
            context_instance=RequestContext(request))

def update( request, report_id):
    report = get_object_or_404(Report, id=report_id)
    if request.REQUEST.has_key('is_fixed'):
        form = MarkAsDoneForm(request.POST, instance=report)
        #Save the mark as done motivation in the database
        form.save()

        if "pro" in request.path:
            return HttpResponseRedirect(report.get_absolute_url_pro())
        else:
            return HttpResponseRedirect(report.get_absolute_url())

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
                  request.POST.__setitem__("title",request.FILES.get('file').name)
            file_form = ReportFileForm(request.POST,request.FILES)
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
        report = Report.objects.filter(private=False).get(id=report_id)

        return HttpResponseRedirect(report.get_absolute_url())
    except:
        messages.add_message(request, messages.ERROR, _("No incident found with this ticket number"))
        return HttpResponseRedirect(reverse('home'))


def index(request, slug=None, commune_id=None):
    if commune_id:
        exception = request.GET.get("exception")
        commune_phone = request.GET.get("phone")

        if exception!=None and exception=='true':
            #Exception parameter is used to show error message for communes not participating...
            error_message = _("Does not participate to FixMyStreet yet with details")+' '+commune_phone
            messages.add_message(request, messages.ERROR, error_message)
        else:

            entity = OrganisationEntity.objects.get(id=commune_id)
            reports = Report.objects.all().entity_territory(entity).public().order_by('-created')
            page_number = request.GET.get("page", 1)
            paginator = Paginator(reports, settings.MAX_ITEMS_PAGE)
            try:
                page = paginator.page(page_number)
            except PageNotAnInteger:
                page = paginator.page(1)
            except EmptyPage:
                page = paginator.page(paginator.num_pages)

            return render_to_response("reports/list.html", {
                "reports": page,
                "all_reports":reports,
                "entity":entity,
            }, context_instance=RequestContext(request))

    communes = OrganisationEntity.objects.filter(commune=True).order_by('name_' + get_language())
    return render_to_response("reports/index.html", {
        "communes": communes
    }, context_instance=RequestContext(request))
