
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.utils.http import urlquote
from django.utils.translation import get_language
from django.conf import settings

from django_fixmystreet.fixmystreet.models import ZipCode, FaqEntry, FMSUser
from django_fixmystreet.fixmystreet.stats import ReportCountQuery



def home(request, location = None, error_msg =None): 
    if request.GET.has_key('q'):
        location = request.GET["q"]
    
    #wards = Ward.objects.all().order_by('name')
    zipcodes = ZipCode.objects.filter(hide=False).order_by('name_' + get_language())
    return render_to_response("home.html",
            {
                "report_counts": ReportCountQuery('1 year'),
                'search_error': error_msg,
                'zipcodes': zipcodes,
                'location':location
            },
            context_instance=RequestContext(request))


def update_current_language(request):
    old_language = get_language()
    new_language = request.REQUEST.get('language')
    if request.user.is_authenticated():
        request.user.fmsuser.last_used_language = new_language.upper()
        fmsUser.save()

    toURL = request.REQUEST.get('from').replace('/{0}/'.format(old_language), '/{0}/'.format(new_language))
    return HttpResponseRedirect(toURL)


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

