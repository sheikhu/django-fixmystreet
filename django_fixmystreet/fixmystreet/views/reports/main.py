from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.forms.models import inlineformset_factory
from django.template import RequestContext
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from datetime import datetime as dt
import datetime
from django.utils.translation import get_language
from django_fixmystreet.fixmystreet.stats import ReportCountQuery
from django.conf import settings
import math

from django_fixmystreet.fixmystreet.models import dictToPoint, Report, ReportFile, ReportSubscription, OrganisationEntity, ZipCode, ReportMainCategoryClass
from django_fixmystreet.fixmystreet.forms import CitizenReportForm, CitizenForm, ReportCommentForm, ReportFileForm, MarkAsDoneForm


def new(request):
    ReportFileFormSet = inlineformset_factory(Report, ReportFile, form=ReportFileForm, extra=0)

    pnt = dictToPoint(request.REQUEST)
    report=None
    if request.method == "POST":
        report_form = CitizenReportForm(request.POST, request.FILES, prefix='report')
        comment_form = ReportCommentForm(request.POST, request.FILES, prefix='comment')
        citizen_form = CitizenForm(request.POST, request.FILES, prefix='citizen')
        # this checks update is_valid too
        if report_form.is_valid() and (not request.POST["comment-text"] or comment_form.is_valid()) and citizen_form.is_valid():
            # this saves the update as part of the report.
            report = report_form.save(commit=False)

            file_formset = ReportFileFormSet(request.POST, request.FILES, instance=report, prefix='files', queryset=ReportFile.objects.none())
            if file_formset.is_valid():
                citizen = citizen_form.save()

                report.citizen = citizen
                report.save()
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

    else:
        report_form = CitizenReportForm(initial={
            'x': request.REQUEST.get('x'),
            'y': request.REQUEST.get('y')
        }, prefix='report')
    file_formset = ReportFileFormSet(prefix='files', queryset=ReportFile.objects.none())
    comment_form = ReportCommentForm(prefix='comment')
    citizen_form = CitizenForm(prefix='citizen')

    reports = Report.objects.all().distance(pnt).filter(point__distance_lte=(pnt, 1000)).order_by('distance')
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
                "reports":reports[0:5]
            },
            context_instance=RequestContext(request))


def report_prepare(request, location = None, error_msg = None):
    '''Used to redirect pro users when clicking home. See backoffice version'''
    if request.GET.has_key('q'):
        location = request.GET["q"]
    last_30_days = dt.today() + datetime.timedelta(days=-30)

    #wards = Ward.objects.all().order_by('name')
    zipcodes = ZipCode.objects.filter(hide=False).select_related('commune').order_by('name_' + get_language())

    return render_to_response("home.html",
            {
                #"report_counts": ReportCountQuery('1 year'),
                "report_counts": ReportCountQuery('1 month'),
                'search_error': error_msg,
                'zipcodes': zipcodes,
                'location':location,
                'reports': Report.objects.all()[0:5],
                'reports_created': Report.objects.filter(status=Report.CREATED).filter(private=False).filter(modified__gt=last_30_days).order_by('-modified')[0:5],
                'reports_in_progress': Report.objects.filter(status__in=Report.REPORT_STATUS_IN_PROGRESS).filter(private=False).filter(modified__gt=last_30_days).order_by('-modified')[0:5],
                'reports_closed':Report.objects.filter(status__in=Report.REPORT_STATUS_CLOSED).filter(private=False).filter(modified__gt=last_30_days).order_by('-modified')[0:5],
            },
            context_instance=RequestContext(request))


def show(request, slug, report_id):
    ReportFileFormSet = inlineformset_factory(Report, ReportFile, form=ReportFileForm, extra=0)
    report = get_object_or_404(Report, id=report_id)
    if report.citizen:
        user_to_show = report.citizen
    else:
        user_to_show = report.created_by

    if request.method == "POST":
        comment_form = ReportCommentForm(request.POST, request.FILES, prefix='comment')
        file_formset = ReportFileFormSet(request.POST, request.FILES, instance=report, prefix='files', queryset=ReportFile.objects.none())
        # citizen_form = CitizenForm(request.POST, request.FILES, prefix='citizen')
        # this checks update is_valid too
        if file_formset.is_valid() and (not request.POST["comment-text"] or comment_form.is_valid()): # and citizen_form.is_valid():
            # this saves the update as part of the report.
            # citizen = citizen_form.save()

            if request.POST["comment-text"]:
                comment = comment_form.save(commit=False)
                comment.report = report
                comment.save()

            file_formset.save()

            # if request.POST.get("citizen_subscription", False):
            #     ReportSubscription(report=report, subscriber=report.created_by).save()


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
            page_number = int(request.GET.get("page", 1))

            entity = OrganisationEntity.objects.get(id=commune_id)
            reports = Report.objects.all().entity_territory(entity).public().order_by('-created')

            pages_list = range(1,int(math.ceil(len(reports)/settings.MAX_ITEMS_PAGE))+1+int(len(reports)%settings.MAX_ITEMS_PAGE != 0))

            return render_to_response("reports/list.html", {
                "reports": reports[int((page_number-1)*settings.MAX_ITEMS_PAGE):int(page_number*settings.MAX_ITEMS_PAGE)],
                "entity":entity,
                "pages_list":pages_list,
                "page_number": page_number,
            }, context_instance=RequestContext(request))

    communes = OrganisationEntity.objects.filter(commune=True).order_by('name_' + get_language())
    return render_to_response("reports/index.html", {
        "communes": communes
    }, context_instance=RequestContext(request))
