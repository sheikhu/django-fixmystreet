from datetime import datetime, timedelta

from django.core.urlresolvers import reverse
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import get_language, activate

from django_fixmystreet.fixmystreet.models import ZipCode, Report, Page
from django_fixmystreet.fixmystreet.stats import ReportCountQuery


DEFAULT_TIMEDELTA_CITIZEN = {"days": -30}
DEFAULT_SQL_INTERVAL_CITIZEN = "30 days"
REPORTS_MAX_RESULTS = 4


def home(request, location=None, error_msg=None):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse("home_pro"))

    if "location" in request.GET:
        location = request.GET["location"]
    last_30_days = datetime.today() + timedelta(**DEFAULT_TIMEDELTA_CITIZEN)

    #wards = Ward.objects.all().order_by("name")
    zipcodes = ZipCode.objects.filter(hide=False).order_by("name_" + get_language())

    # Queryset common to all reports
    qs = Report.objects.filter(private=False) \
         .extra(select={"has_thumbnail": "CASE WHEN thumbnail IS NULL OR thumbnail = '' THEN 0 ELSE 1 END"}) \
         .order_by("-has_thumbnail", "-modified")

    return render_to_response("home.html", {
        #"report_counts": ReportCountQuery("1 year"),
        "report_counts": ReportCountQuery(interval=DEFAULT_SQL_INTERVAL_CITIZEN, citizen=True),
        'search_error': error_msg,
        'zipcodes': zipcodes,
        'all_zipcodes': ZipCode.objects.all(),
        'location': location,
        'zipcode': request.GET.get("ward"),
        'reports_created': qs.filter(status=Report.CREATED, created__gte=last_30_days)[:REPORTS_MAX_RESULTS],
        'reports_in_progress': qs.filter(status__in=Report.REPORT_STATUS_IN_PROGRESS, modified__gte=last_30_days)[:REPORTS_MAX_RESULTS],
        'reports_closed': qs.filter(status=Report.PROCESSED, close_date__gte=last_30_days)[:REPORTS_MAX_RESULTS],
    }, context_instance=RequestContext(request))


def page(request):
    try:
        params = {"slug_" + get_language(): request.path[3:].strip("/")}
        p = Page.objects.get(**params)
    except Page.DoesNotExist:
        raise Http404()
    return render_to_response("page.html", {
        "page": p
    }, context_instance=RequestContext(request))


def update_current_language(request):
    activate(request.REQUEST.get("language"))

    if request.user.is_authenticated():
        fms_user = request.user.fmsuser
        fms_user.last_used_language = request.REQUEST.get("language").upper()
        fms_user.save()
        return HttpResponseRedirect(reverse("home_pro"))

    return HttpResponseRedirect(reverse("home"))
