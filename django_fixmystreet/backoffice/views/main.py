from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.utils.translation import get_language, activate
from django_fixmystreet.fixmystreet.models import ZipCode, Report
from django_fixmystreet.fixmystreet.stats import ReportCountQuery, ReportCountStatsPro
from django.core.urlresolvers import reverse


def home(request, location = None, error_msg =None):
    # if not request.LANGUAGE_CODE == request.user.fmsuser.last_used_language.lower():
    #     activate(request.user.fmsuser.last_used_language.lower())
    #     request.LANGUAGE_CODE = request.user.fmsuser.last_used_language.lower()
    #     fromUrl = '/'+request.user.fmsuser.last_used_language.lower()+'/pro/'
    #     return HttpResponseRedirect(fromUrl)
    #wards = Ward.objects.all().order_by('name')

    #Default language
    if (not request.LANGUAGE_CODE in ['fr', 'nl', 'en']):
        local_lng = 'fr'
    else:
        local_lng = request.LANGUAGE_CODE

    #Redirect to pro section: list of reports if the user has the role manager
    if (request.user.fmsuser.manager):
        fromUrl = reverse('report_list_pro', args=['all'])+'?page=1'
        return HttpResponseRedirect(fromUrl)

    zipcodes = ZipCode.objects.filter(hide=False).order_by('name_'+get_language())
    statsObject = ReportCountStatsPro()
    stats_result = statsObject.get_result()
    stats = statsObject.get_stats()
    popup_reports = []
    if "stat_type" in request.GET:
        start_date = stats[str(request.GET["stat_type"])]["start_date"]
        end_date = stats[str(request.GET["stat_type"])]["end_date"]
        if str(request.GET["stat_status"]) == 'unpublished':
            popup_reports = Report.objects.filter(status=Report.CREATED).filter(created__gt=str(start_date)).filter(created__lt=str(end_date))
        elif str(request.GET["stat_status"])== 'in_progress':
            popup_reports = Report.objects.filter(status__in=Report.REPORT_STATUS_IN_PROGRESS).filter(created__gt=str(start_date)).filter(created__lt=str(end_date))
        else:
            popup_reports = Report.objects.filter(status__in=Report.REPORT_STATUS_CLOSED).filter(created__gt=str(start_date)).filter(created__lt=str(end_date))

    return render_to_response("pro/home.html",
            {
                "report_counts": ReportCountQuery('1 year'),
                'search_error': error_msg,
                'zipcodes': zipcodes,
                'location':location,
                'reports':Report.objects.all(),
                'reports_created': Report.objects.filter(status=Report.CREATED).order_by('-modified')[0:5],
                'reports_in_progress': Report.objects.filter(status__in=Report.REPORT_STATUS_IN_PROGRESS).order_by('-modified')[0:5],
                'reports_closed':Report.objects.filter(status__in=Report.REPORT_STATUS_CLOSED).order_by('-modified')[0:5],
                'stats':stats_result,
                'popup_reports':popup_reports,
            },
            context_instance=RequestContext(request))
