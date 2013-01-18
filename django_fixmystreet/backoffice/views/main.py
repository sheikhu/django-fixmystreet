from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import get_language
from django_fixmystreet.fixmystreet.models import ZipCode, Report
from django_fixmystreet.fixmystreet.stats import ReportCountQuery, ReportCountStatsPro


def home(request, location = None, error_msg =None):
    #activate(request.user.fmsuser.last_used_language.lower())
    #wards = Ward.objects.all().order_by('name')
    zipcodes = ZipCode.objects.filter(hide=False).order_by('name_'+get_language())
    statsObject = ReportCountStatsPro()
    stats_result = statsObject.get_result()
    stats = statsObject.get_stats()
    popup_reports = []
    if "stat_type" in request.GET:
        start_date = stats[str(request.GET["stat_type"])]["start_date"]
        end_date = stats[str(request.GET["stat_type"])]["end_date"]
        if str(request.GET["stat_status"]) == 'unpublished':
            print "created"
            popup_reports = Report.objects.filter(status=Report.CREATED).filter(created__gt=str(start_date)).filter(created__lt=str(end_date))
        elif str(request.GET["stat_status"])== 'in_progress':
            print "ongoing"
            popup_reports = Report.objects.filter(status__in=Report.REPORT_STATUS_IN_PROGRESS).filter(created__gt=str(start_date)).filter(created__lt=str(end_date))
        else:
            print 'closed'
            popup_reports = Report.objects.filter(status__in=Report.REPORT_STATUS_CLOSED).filter(created__gt=str(start_date)).filter(created__lt=str(end_date))
    return render_to_response("pro/home.html",
            {
                "report_counts": ReportCountQuery('1 year'),
                'search_error': error_msg,
                'zipcodes': zipcodes,
                'location':location,
                'reports':Report.objects.all(),
                'reports_created': Report.objects.filter(status=Report.CREATED)[0:5],
                'reports_in_progress': Report.objects.filter(status__in=Report.REPORT_STATUS_IN_PROGRESS)[0:5],
                'reports_closed':Report.objects.filter(status__in=Report.REPORT_STATUS_CLOSED)[0:5],
                'stats':stats_result,
                'popup_reports':popup_reports,
            },
            context_instance=RequestContext(request))
