
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import get_language
from django_fixmystreet.fixmystreet.models import ZipCode
from django_fixmystreet.fixmystreet.stats import ReportCountQuery



def home(request, location = None, error_msg =None): 

    #wards = Ward.objects.all().order_by('name')
    zipcodes = ZipCode.objects.filter(hide=False).order_by('name_'+get_language())
    return render_to_response("pro/home.html",
            {
                "report_counts": ReportCountQuery('1 year'),
                'search_error': error_msg,
                'zipcodes': zipcodes
            },
            context_instance=RequestContext(request))
