import datetime

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404, HttpResponseForbidden
from django.template import Context, RequestContext
from django.contrib.gis.geos import *
from django.utils.translation import ugettext as _
from django.contrib.gis.measure import D 

from fixmystreet.models import dictToPoint,Report, ReportUpdate, Ward, ReportCategory
from fixmystreet.forms import ReportForm,ReportUpdateForm
import settings


def new( request ):
    pnt = dictToPoint(request.REQUEST)

    if request.method == "POST":
        report_form = ReportForm( request.POST, request.FILES )
        # this checks update is_valid too
        if report_form.is_valid():
            # this saves the update as part of the report.
            report = report_form.save()
            if report:
                return( HttpResponseRedirect( report.get_mobile_absolute_url() ))
    else:
        report_form = ReportForm(initial={ 'lat': request.GET.get('lat',request.POST.get('lat')),
                                           'lon': request.GET.get('lon',request.POST.get('lon')),
                                           #'postalcode': request.GET['postalcode'],
                                           #'address': request.GET.get('address',None)
                                })

    return render_to_response("reports/mobile/new.html",
                {
                    "report_form": report_form,
                    "update_form": report_form.update_form,
                    "pnt":pnt
                },
                context_instance=RequestContext(request))


def show(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    subscribers = report.reportsubscriber_set.count() + 1
    return render_to_response("reports/mobile/show.html",
            {
                "report": report,
                "subscribers": subscribers,
                "ward":report.ward,
                "updates": ReportUpdate.objects.filter(report=report, is_confirmed=True).order_by("created_at")[1:], 
                "update_form": ReportUpdateForm(), 
                "pnt":report.point
                #"google":  FixMyStreetMap((report.point))
            },
            context_instance=RequestContext(request))


