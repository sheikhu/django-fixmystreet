from datetime import datetime as dt
import datetime

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.utils.translation import get_language, activate
from django.core.urlresolvers import reverse
from django_fixmystreet.fixmystreet.models import ZipCode, FaqEntry, Report, ReportFile, ReportAttachment
from django_fixmystreet.fixmystreet.stats import ReportCountQuery


def home(request, location=None, error_msg=None):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('home_pro'))

    if request.GET.has_key('q'):
        location = request.GET["q"]
    last_30_days = dt.today() + datetime.timedelta(days=-30)

    #wards = Ward.objects.all().order_by('name')
    zipcodes = ZipCode.objects.filter(hide=False).order_by('name_' + get_language())

    # Get report closed with photos only
    reports_closed = Report.objects.filter(
        status__in=Report.REPORT_STATUS_CLOSED,
        private=False,
        created__gt=last_30_days).order_by('thumbnail', '-modified')[0:4]

    return render_to_response("home.html",
            {
                #"report_counts": ReportCountQuery('1 year'),
                "report_counts": ReportCountQuery('1 month'),
                'search_error': error_msg,
                'zipcodes': zipcodes,
                'all_zipcodes': ZipCode.objects.all(),
                'location': location,
                'reports_created': Report.objects.filter(status=Report.CREATED, private=False, created__gt=last_30_days).order_by('thumbnail', '-modified')[0:4],
                'reports_in_progress': Report.objects.filter(status__in=Report.REPORT_STATUS_IN_PROGRESS, private=False, created__gt=last_30_days).order_by('thumbnail', '-modified')[0:4],
                'reports_closed': reports_closed,
            },
            context_instance=RequestContext(request))


def update_current_language(request):
    activate(request.REQUEST.get('language'))

    if request.user.is_authenticated():
        fmsUser = request.user.fmsuser
        fmsUser.last_used_language = request.REQUEST.get('language').upper()
        fmsUser.save()
        return HttpResponseRedirect(reverse('home_pro'))

    return HttpResponseRedirect(reverse('home'))


def about(request):
    return render_to_response("about.html", {
        'faq_entries': FaqEntry.objects.all().order_by('order')
    }, context_instance=RequestContext(request))


def faq(request):
    return render_to_response("about.html", {
        'faq_entries': FaqEntry.objects.all().order_by('order')
    }, context_instance=RequestContext(request))


def terms_of_use(request):
    return render_to_response("terms_of_use.html", context_instance=RequestContext(request))

