from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.utils.http import urlquote
from django.utils.translation import get_language
from django.contrib.auth.decorators import login_required
from django_fixmystreet.fixmystreet.models import ZipCode, FaqEntry
from django_fixmystreet.fixmystreet.stats import ReportCountQuery
from django.conf import settings


def home(request, location = None, error_msg =None): 
    if request.GET.has_key('q'):
        location = request.GET["q"]
    
    #wards = Ward.objects.all().order_by('name')
    zipcodes = ZipCode.objects.filter(hide=False).order_by('name_'+get_language())
    return render_to_response("pro/home.html",
            {
                "report_counts": ReportCountQuery('1 year'),
                'search_error': error_msg,
                'zipcodes': zipcodes,
                'location':location
            },
            context_instance=RequestContext(request))
