import logging
import os
import urllib
import datetime

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.template import Context, RequestContext
from django.contrib.gis.measure import D 
from django.contrib.gis.geos import *
from django.utils.translation import ugettext as _
from django.utils.http import urlquote
from django.utils.encoding import iri_to_uri
from django.utils.translation import get_language

import settings
from fixmystreet.models import dictToPoint, Report, ReportUpdate, ZipCode, ReportCountQuery, City, FaqEntry


def home(request, location = None, error_msg =None): 
    if request.GET.has_key('q'):
        location = request.GET["q"]
    
    #wards = Ward.objects.all().order_by('name')
    zipcodes = ZipCode.objects.filter(hide=False).order_by('name_'+get_language())
    return render_to_response("home.html",
            {
                "report_counts": ReportCountQuery('1 year'),
                "cities": City.objects.all(),
                'search_error': error_msg,
                'zipcodes': zipcodes,
                'location':location
            },
            context_instance=RequestContext(request))

def about(request):
    return render_to_response("about.html",{'faq_entries' : FaqEntry.objects.all().order_by('order')},
            context_instance=RequestContext(request)) 
   
def posters(request): 
    return render_to_response("posters.html",
            {'languages': settings.LANGUAGES },
            context_instance=RequestContext(request))

def termOfUse(request): 
    return render_to_response("term_of_use.html",
            context_instance=RequestContext(request))
      
def robot(request): 
    return HttpResponse("""User-Agent: *
Disallow: /
""",mimetype="text/plain")

def googleCheck(request): 
    return HttpResponse("google-site-verification: google8f518780d83abb68.html")
