
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.utils.translation import get_language, activate
from django.conf import settings

from django_fixmystreet.fixmystreet.models import ZipCode, FaqEntry, Report
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
                'location':location,
                'reports': Report.objects.all()[0:5],
                'reports_created': Report.objects.filter(status=Report.CREATED)[0:5],
                'reports_in_progress': Report.objects.filter(status__in=Report.REPORT_STATUS_IN_PROGRESS)[0:5],
                'reports_closed':Report.objects.filter(status__in=Report.REPORT_STATUS_CLOSED)[0:5]
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

