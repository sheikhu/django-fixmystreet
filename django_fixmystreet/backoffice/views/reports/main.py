from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.forms.models import modelformset_factory
from django_fixmystreet.fixmystreet.models import ZipCode, dictToPoint, Report, ReportSubscription, ReportFile, ReportComment, OrganisationEntity, FMSUser
from django_fixmystreet.fixmystreet.forms import ProReportForm, ReportFileForm, ReportCommentForm, FileUploadForm, MarkAsDoneForm, ReportFileForm, ReportMainCategoryClass
from django_fixmystreet.backoffice.forms import  RefuseForm
from django.template import RequestContext
from django_fixmystreet.fixmystreet.session_manager import SessionManager
from django.conf import settings


def new(request):
    pnt = dictToPoint(request.REQUEST)
    ReportFileFormSet = modelformset_factory(ReportFile, form=ReportFileForm, extra=0)
    report = None
    if request.method == "POST":
        print request.POST
        report_form = ProReportForm(request.POST, request.FILES, prefix='report')
        file_formset = ReportFileFormSet(request.POST, request.FILES, prefix='files', queryset=ReportFile.objects.none())
        comment_form = ReportCommentForm(request.POST, request.FILES, prefix='comment')
        # this checks update is_valid too
        if report_form.is_valid() and file_formset.is_valid() and (not request.POST["comment-text"] or comment_form.is_valid()):
            # this saves the update as part of the report.
            report = report_form.save()
            
            if request.POST["comment-text"]:
                comment = comment_form.save(commit=False)
                comment.created_by = FMSUser.objects.get(pk=request.user.id)
                comment.report = report
                comment.save()

            files = file_formset.save(commit=False)
            for report_file in files:
                report_file.report = report
                report_file.created_by = FMSUser.objects.get(pk=request.user.id)
                #if no content the user the filename as description
                if (report_file.title == ''):
                    report_file.title = str(report_file.file.name)
                report_file.save()

    report_form = ProReportForm(initial={
        'x': request.REQUEST.get('x'),
        'y': request.REQUEST.get('y')
    }, prefix='report')

    file_formset = ReportFileFormSet(prefix='files', queryset=ReportFile.objects.none())
    comment_form = ReportCommentForm(prefix='comment')
    reports = Report.objects.all().distance(pnt).filter(point__distance_lte=(pnt, 1000)).order_by('distance')
    return render_to_response("pro/reports/new.html",
            {
                "report":report,
                "available_zips":ZipCode.objects.all(),
                "category_classes":ReportMainCategoryClass.objects.prefetch_related('categories').all(),
                "report_form": report_form,
                "pnt":pnt,
                "reports":reports[0:5],
                "file_formset":file_formset,
                "comment_form":comment_form,
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
    ReportFileFormSet = modelformset_factory(ReportFile, form=ReportFileForm, extra=0)
    report = get_object_or_404(Report, id=report_id)
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
                comment.created_by = FMSUser.objects.get(pk=request.user.id)
                comment.report = report
                comment.save()
            files = file_formset.save(commit=False)
            for report_file in files:
                report_file.report = report
                report_file.created_by = FMSUser.objects.get(pk=request.user.id)
                #if no content the user the filename as description
                if (report_file.title == ''):
                    report_file.title = str(report_file.file.name)
                report_file.save()
    
    file_formset = ReportFileFormSet(prefix='files', queryset=ReportFile.objects.none())
    comment_form = ReportCommentForm(prefix='comment')

    if request.GET.get("page"):
        page_number= int(request.GET.get("page"))
    else :
        page_number=1

    organisationId = FMSUser.objects.get(pk=request.user.id).organisation_id
    
    managers = FMSUser.objects.filter(organisation_id = organisationId).filter(manager=True)
    fms_managers = FMSUser.objects.filter(manager=True).values_list('organisation', flat=True);
    entitiesHavingManager = OrganisationEntity.objects.filter(id__in=fms_managers).values_list('pk', flat=True)  

    region_institution = OrganisationEntity.objects.filter(region=True).filter(id__in=entitiesHavingManager)
    entities = OrganisationEntity.objects.exclude(pk=organisationId).filter(commune=True).filter(id__in=entitiesHavingManager)
    
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
            },
            context_instance=RequestContext(request))
