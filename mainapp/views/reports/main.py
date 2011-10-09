from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect,Http404
from mainapp.models import DictToPoint,Report, ReportUpdate, Ward, ReportCategory
from mainapp.forms import ReportForm,ReportUpdateForm
from django.template import Context, RequestContext
from django.contrib.gis.geos import *
from fixmystreet import settings
from django.utils.translation import ugettext as _
import datetime
from django.contrib.gis.measure import D 
from mainapp.views.main import _search_url
from django.contrib.sites.models import Site

def new( request ):
    d2p = DictToPoint( request.REQUEST )
    pnt = d2p.pnt()
    current_site = Site.objects.get_current()
    if request.method == "POST":
        report_form = ReportForm( request.POST, request.FILES )
        # this checks update is_valid too
        if report_form.is_valid():
            # this saves the update as part of the report.
            report = report_form.save()
            if report:
                return( HttpResponseRedirect( report.get_absolute_url() ))
    else:
        report_form = ReportForm(initial={ 'lat': request.GET.get('lat',request.POST.get('lat')),
                                           'lon': request.GET.get('lon',request.POST.get('lon')),
                                           #'postalcode': request.GET['postalcode'],
                                           #'address': request.GET.get('address',None)
                                           } )


    # calculate date range for which to return reports
    if request.GET.has_key('years_ago'):
        years_ago = int(request.GET['years_ago'])
    else:
        years_ago = 0
    yearoffset = datetime.timedelta(days = 365 * years_ago )
    
    date_range_end = datetime.datetime.now() - yearoffset
    date_range_start = date_range_end - datetime.timedelta(days =365)
    
    # do we want to show older reports?
    if Report.objects.filter(created_at__lte = date_range_start, is_confirmed = True, point__distance_lte=(pnt,D(km=2))).count() > 1:
    #if Report.objects.filter(ward=report_form.ward,created_at__lte=date_range_start).count() > 1:
        older_reports_link = _search_url(request, years_ago - 1)
    else:
        older_reports_link = None

    reports = Report.objects.filter(created_at__gte = date_range_start, created_at__lte = date_range_end, is_confirmed = True,point__distance_lte=(pnt,D(km=2))).distance(pnt).order_by('-created_at')
    
    return render_to_response("reports/new.html",
            {
                "report_form": report_form,
                "update_form": report_form.update_form,
                #"ward": report_form.ward,
                "pnt":pnt,
                "reports":reports,
                "date_range_start": date_range_start,
                "date_range_end": date_range_end,
                "older_reports_link": older_reports_link 
            },
            context_instance=RequestContext(request))


def show( request, report_id ):
    report = get_object_or_404(Report, id=report_id)
    subscribers = report.reportsubscriber_set.count() + 1
    return render_to_response("reports/show.html",
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

