from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.utils.http import urlquote
from django.utils.translation import get_language
from django.contrib.auth.decorators import login_required
from django_fixmystreet.fixmystreet.models import ZipCode, ReportCountQuery, FaqEntry
from django.conf import settings

@login_required(login_url='/pro/accounts/login/')
def home(request, location = None, error_msg =None): 
    if request.GET.has_key('q'):
        location = request.GET["q"]
    
    #wards = Ward.objects.all().order_by('name')
    zipcodes = ZipCode.objects.filter(hide=False).order_by('name_'+get_language())
    return render_to_response("home_pro.html",
            {
                "report_counts": ReportCountQuery('1 year'),
#                "cities": City.objects.all(),
                'search_error': error_msg,
                'zipcodes': zipcodes,
                'location':location
            },
            context_instance=RequestContext(request))
