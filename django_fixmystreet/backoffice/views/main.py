from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import get_language
from django_fixmystreet.fixmystreet.models import ZipCode, Report
from django_fixmystreet.fixmystreet.stats import ReportCountQuery
from django.utils.translation import activate, get_language



def home(request, location = None, error_msg =None): 
    #activate(request.user.fmsuser.last_used_language.lower())
    #wards = Ward.objects.all().order_by('name')
    zipcodes = ZipCode.objects.filter(hide=False).order_by('name_'+get_language())
    return render_to_response("pro/home.html",
            {
                "report_counts": ReportCountQuery('1 year'),
                'search_error': error_msg,
                'zipcodes': zipcodes,
                'location':location,
                'reports':Report.objects.all(),
                'reports_created': Report.objects.filter(status=Report.CREATED)[0:5],
                'reports_in_progress': Report.objects.filter(status__in=Report.REPORT_STATUS_IN_PROGRESS)[0:5],
                'reports_closed':Report.objects.filter(status__in=Report.REPORT_STATUS_CLOSED)[0:5]
            },
            context_instance=RequestContext(request))
