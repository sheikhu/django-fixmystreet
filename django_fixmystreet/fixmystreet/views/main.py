
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.utils.translation import get_language, activate
from django.conf import settings
from django_fixmystreet.fixmystreet.models import ZipCode, FaqEntry, Report
from django_fixmystreet.fixmystreet.stats import ReportCountQuery
from datetime import datetime as dt
import datetime

def home(request, location = None, error_msg =None):
    if request.user.is_authenticated() == True:
        #Default language
        if (not request.LANGUAGE_CODE in ['fr', 'nl', 'en']):
            local_lng = 'fr'
        else:
            local_lng = request.LANGUAGE_CODE
        fromUrl = '/'+local_lng+'/pro/'
        return HttpResponseRedirect(fromUrl)

    if request.GET.has_key('q'):
        location = request.GET["q"]
    last_30_days = dt.today() + datetime.timedelta(days=-30)

    #wards = Ward.objects.all().order_by('name')
    zipcodes = ZipCode.objects.filter(hide=False).order_by('name_' + get_language())

    return render_to_response("home.html",
            {
                #"report_counts": ReportCountQuery('1 year'),
                "report_counts": ReportCountQuery('1 month'),
                'search_error': error_msg,
                'zipcodes': zipcodes,
                'location':location,
                'reports': Report.objects.filter(private=False)[0:5],
                'reports_created': Report.objects.filter(status=Report.CREATED).filter(private=False).filter(created__gt=last_30_days).order_by('-modified')[0:5],
                'reports_in_progress': Report.objects.filter(status__in=Report.REPORT_STATUS_IN_PROGRESS).filter(private=False).filter(created__gt=last_30_days).order_by('-modified')[0:5],
                'reports_closed':Report.objects.filter(status__in=Report.REPORT_STATUS_CLOSED).filter(private=False).filter(created__gt=last_30_days).order_by('-modified')[0:5],
            },
            context_instance=RequestContext(request))


def update_current_language(request):
    if request.user.is_authenticated():
        fmsUser = request.user.fmsuser
        fmsUser.last_used_language = request.REQUEST.get('language').upper()
        fmsUser.save()
    activate(request.REQUEST.get('language'))
    fromUrl = request.REQUEST.get('from')
    if 'pro' in fromUrl:
        fromUrl = '/'+request.REQUEST.get('language')+'/pro/'
    else:
        fromUrl = '/'+request.REQUEST.get('language')+'/'
    return HttpResponseRedirect(fromUrl)


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

