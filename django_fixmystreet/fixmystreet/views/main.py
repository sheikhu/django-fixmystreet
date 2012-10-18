
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.utils.http import urlquote
from django.utils.translation import get_language

from django_fixmystreet.fixmystreet.models import ZipCode, ReportCountQuery, City, FaqEntry
from django.conf import settings

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
    return render_to_response("about.html", {'faq_entries' : FaqEntry.objects.all().order_by('order')},
            context_instance=RequestContext(request)) 
   
def posters(request): 
    return render_to_response("posters.html",
            {'languages': settings.LANGUAGES },
            context_instance=RequestContext(request))

def terms_of_use(request): 
    return render_to_response("term_of_use.html",
            context_instance=RequestContext(request))
      
def robot(request): 
    return HttpResponse("""User-Agent: *
Disallow: /
""", mimetype="text/plain")

