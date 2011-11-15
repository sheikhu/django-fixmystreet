from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from mainapp.models import DictToPoint, Report, ReportUpdate, Ward, ReportCountQuery, City, FaqEntry
from mainapp import search
from django.template import Context, RequestContext
from django.contrib.gis.measure import D 
from django.contrib.gis.geos import *
import settings
import datetime
from django.utils.translation import ugettext as _
from django.utils.http import urlquote
from django.utils.encoding import iri_to_uri
from mainapp.views.cities import home as city_home
import logging
import os
import urllib
from django.http import HttpResponse


def home(request, location = None, error_msg =None): 

    if request.subdomain:
        matching_cities = City.objects.filter(name__iexact=request.subdomain)
        if matching_cities:
            return( city_home(request, matching_cities[0], error_msg, disambiguate ) )

    if request.GET.has_key('q'):
        location = request.GET["q"]
    
    wards = Ward.objects.all().order_by('name')
    return render_to_response("home.html",
            {
                "report_counts": ReportCountQuery('1 year'),
                "cities": City.objects.all(),
                'search_error': error_msg,
                'wards': wards,
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
      
def robot(request): 
    return HTTPResponse(""" 
    User-Agent: *
    Disallow: /
    """)

def googleCheck(request): 
    return HTTPResponse("google-site-verification: google8f518780d83abb68.html")
