from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect,Http404
from fixmystreet.models import dictToPoint, Report, ReportSubscription
from fixmystreet.forms import ReportForm, ReportUpdateForm
from django.template import RequestContext
from django.contrib.gis.geos import *
import settings
from django.utils.translation import ugettext as _
import datetime
from django.contrib.gis.measure import D
from django.contrib.sites.models import Site


def new(request):
    pnt = dictToPoint(request.REQUEST)
    if request.method == "POST":
        report_form = ReportForm(request.POST, request.FILES)
        # this checks update is_valid too
        if report_form.is_valid():
            # this saves the update as part of the report.
            report = report_form.save(request.user)
            if report:
                return HttpResponseRedirect(report.get_absolute_url())
    else:
        report_form = ReportForm(initial={
            'x': request.REQUEST.get('x'),
            'y': request.REQUEST.get('y')
        })

    reports = Report.objects.filter(is_fixed = False).distance(pnt).order_by('distance')[0:10]
    return render_to_response("reports/new.html",
            {
                "report_form": report_form,
                "pnt":pnt,
                "reports":reports
            },
            context_instance=RequestContext(request))


def show(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    return render_to_response("reports/show.html",
            {
                "report": report,
                "subscribed": request.user.is_authenticated() and ReportSubscription.objects.filter(report=report, subscriber=request.user).exists(),
                "update_form": ReportUpdateForm()
            },
            context_instance=RequestContext(request))

