from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django_fixmystreet.fixmystreet.models import dictToPoint, Report, ReportSubscription, OrganisationEntity, ReportComment, ReportFile, ZipCode
from django_fixmystreet.fixmystreet.forms import CitizenReportForm, ReportCommentForm, ReportFileForm, FileUploadForm
from django.template import RequestContext
from django_fixmystreet.fixmystreet.session_manager import SessionManager


def new(request):
    pnt = dictToPoint(request.REQUEST)
    if request.method == "POST":
        report_form = CitizenReportForm(request.POST, request.FILES)
	# this checks update is_valid too
        if report_form.is_valid():
            # this saves the update as part of the report.
            report = report_form.save(request.user)
            session_manager = SessionManager()
            session_manager.saveComments(request.session.session_key, report.id)
            session_manager.saveFiles(request.session.session_key, report.id)
            comments = ReportComment.objects.filter(report_id=report.id)
            files = ReportFile.objects.filter(report_id=report.id)
            if report:
                return HttpResponseRedirect(report.get_absolute_url())
    else:
        session_manager = SessionManager()
        session_manager.clearSession(request.session.session_key)
        report_form = CitizenReportForm(initial={
            'x': request.REQUEST.get('x'),
            'y': request.REQUEST.get('y')
        })

    reports = Report.objects.all().distance(pnt).filter(point__distance_lte=(pnt, 1000)).order_by('distance')
    
    return render_to_response("reports/new.html",
            {
                "available_zips":ZipCode().get_usable_zipcodes(),
                "comment_form":ReportCommentForm(),
                "file_form":ReportFileForm(),
                "report_form": report_form,
                "pnt":pnt,
                "reports":reports,
                "file_upload_Form":FileUploadForm()
            },
            context_instance=RequestContext(request))


def show(request, slug, report_id):
    report = get_object_or_404(Report, id=report_id)
    return render_to_response("reports/show.html",
            {
                "report": report,
                "subscribed": request.user.is_authenticated() and ReportSubscription.objects.filter(report=report, subscriber=request.user).exists(),
                "update_form": ReportCommentForm(),
                "comment_form": ReportCommentForm(),
                "file_form":ReportFileForm(),
            },
            context_instance=RequestContext(request))


def index(request,slug=None, commune_id=None):
    if commune_id:
        entity = OrganisationEntity.objects.get(id=commune_id)
        return render_to_response("reports/list.html", {
            "reports": entity.reports_in_charge.all(),
            "entity":entity,
        }, context_instance=RequestContext(request))

    communes = OrganisationEntity.objects.filter(commune=True)
    return render_to_response("reports/index.html", {
        "communes": communes
    }, context_instance=RequestContext(request))
