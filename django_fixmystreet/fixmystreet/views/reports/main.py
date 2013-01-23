from django.db.models import Q
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.forms.models import modelformset_factory
from django.template import RequestContext
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from django_fixmystreet.fixmystreet.models import dictToPoint, Report, ReportFile, ReportSubscription, OrganisationEntity, ZipCode, ReportMainCategoryClass
from django_fixmystreet.fixmystreet.forms import CitizenReportForm, CitizenForm, ReportCommentForm, ReportFileForm, MarkAsDoneForm



def new(request):
    ReportFileFormSet = modelformset_factory(ReportFile, form=ReportFileForm, extra=0)
    pnt = dictToPoint(request.REQUEST)
    report=None
    if request.method == "POST":
        report_form = CitizenReportForm(request.POST, request.FILES, prefix='report')
        file_formset = ReportFileFormSet(request.POST, request.FILES, prefix='files', queryset=ReportFile.objects.none())
        comment_form = ReportCommentForm(request.POST, request.FILES, prefix='comment')
        citizen_form = CitizenForm(request.POST, request.FILES, prefix='citizen')
        # this checks update is_valid too
        if report_form.is_valid() and file_formset.is_valid() and (not request.POST["comment-text"] or comment_form.is_valid()) and citizen_form.is_valid():
                # this saves the update as part of the report.
                citizen = citizen_form.save()

                report = report_form.save(commit=False)
                report.citizen = citizen
                report.save()
                if request.POST["comment-text"]:
                    comment = comment_form.save(commit=False)
                    comment.created_by = citizen 
                    comment.report = report
                    comment.save()

                files = file_formset.save(commit=False)
                for report_file in files:
                    report_file.report = report
                    report_file.created_by = citizen
                    #if no content the user the filename as description
                    if (report_file.title == ''):
                        report_file.title = str(report_file.file.name)
                    report_file.save()
                if "citizen-subscription" in request.POST:
                    if request.POST["citizen-subscription"]=="on":
                        ReportSubscription(report=report, subscriber=report.citizen).save()


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
                "available_zips":ZipCode().get_usable_zipcodes(),
                "all_zips":ZipCode.objects.filter(hide=False),
                "category_classes":ReportMainCategoryClass.objects.prefetch_related('categories').all(),
                "comment_form":comment_form,
                "file_formset":file_formset,
                "report_form": report_form,
                "citizen_form": citizen_form,
                "pnt":pnt,
                "reports":reports[0:5]
            },
            context_instance=RequestContext(request))

def report_prepare(request):
    '''Used to redirect pro users when clicking home. See backoffice version'''
    return render_to_response("pro/home.html",
            {},
            context_instance=RequestContext(request))

def show(request, slug, report_id):
    ReportFileFormSet = modelformset_factory(ReportFile, form=ReportFileForm, extra=0)
    report = get_object_or_404(Report, id=report_id)
    if report.citizen:
        user_to_show = report.citizen
    else:
        user_to_show = report.created_by
    
    if request.method == "POST":
        file_formset = ReportFileFormSet(request.POST, request.FILES, prefix='files', queryset=ReportFile.objects.none())
        comment_form = ReportCommentForm(request.POST, request.FILES, prefix='comment')
        # citizen_form = CitizenForm(request.POST, request.FILES, prefix='citizen')
        # this checks update is_valid too
        if file_formset.is_valid() and (not request.POST["comment-text"] or comment_form.is_valid()): # and citizen_form.is_valid():
            # this saves the update as part of the report.
            # citizen = citizen_form.save()

            if request.POST["comment-text"]:
                comment = comment_form.save(commit=False)
                comment.report = report
                comment.save()

            files = file_formset.save(commit=False)
            for report_file in files:
                report_file.report = report
                #if no content the user the filename as description
                if (report_file.title == ''):
                    report_file.title = str(report_file.file.name)
                report_file.save()

            if request.POST.get("citizen_subscription", False):
                ReportSubscription(report=report, subscriber=report.created_by).save()

            messages.add_message(request, messages.SUCCESS, _("You attachments has been sent"))
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
        entity = OrganisationEntity.objects.get(id=commune_id)
        return render_to_response("reports/list.html", {
            #"reports": entity.reports_in_charge.order_by('address').filter(Q(private=False, status__in=Report.REPORT_STATUS_IN_PROGRESS) | Q(private=False, status__in=Report.CREATED, citizen__isnull=False)).all(),
            #"reports": entity.reports_in_charge.filter(private=False).filter((Q(status__in=Report.REPORT_STATUS_IN_PROGRESS)) | (Q(status=Report.CREATED, citizen__isnull=False))).order_by('address', 'address_number'),
            "reports": entity.reports_in_charge.filter(private=False).filter((Q(status__in=Report.REPORT_STATUS_IN_PROGRESS)) | (Q(status=Report.CREATED, citizen__isnull=False))).order_by('-created'),
            "entity":entity,
        }, context_instance=RequestContext(request))

    communes = OrganisationEntity.objects.filter(commune=True)
    return render_to_response("reports/index.html", {
        "communes": communes
    }, context_instance=RequestContext(request))
