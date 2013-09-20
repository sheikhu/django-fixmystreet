from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from django.utils.translation import get_language
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.exceptions import PermissionDenied

from django_fixmystreet.fixmystreet.models import Report, ZipCode
from django_fixmystreet.fixmystreet.utils import dict_to_point
from django_fixmystreet.backoffice.forms import SearchIncidentForm

default_position = {
    'x': '148954.431',
    'y': '170458.371'
}

def filter_reports(user, criteria):
    ownership = criteria.get("ownership", "entity")

    search_street = criteria.get("street", "")
    search_street_number = criteria.get("streetNumber", "")
    search_radius = int(criteria.get("rayon", 0))
    status = criteria.get("status", "")
    is_default_position = False

    if 'x' in criteria and 'y' in criteria:
        pnt = dict_to_point(criteria)
    else:
        pnt = dict_to_point(default_position)
        is_default_position = True

    reports = Report.objects.all()

    #List of transfered reports (previous reports)
    previous_reports = connectedUser.previous_reports.all()

    #if the user is an contractor then user the dependent organisation id
    #If the manager is connected then filter on manager
    if user.agent or user.manager or user.leader:
        if ownership == "responsible":
            reports = reports.responsible(user)
        elif ownership == "subscribed":
            reports = reports.subscribed(user)
        elif user.organisation:  # ownership == entity
            reports = reports.entity_responsible(user)
    elif user.contractor or user.applicant:
        #if the user is an contractor then display only report where He is responsible
        reports = reports.entity_responsible(user)
    else:
        raise PermissionDenied()

    if status == 'created':
        reports = reports.created()
    elif status == 'in_progress':
        reports = reports.in_progress()
    elif status == 'in_progress_and_assigned':
        reports = reports.in_progress().assigned()
    elif status == 'closed':
        reports = reports.closed()
    # else: # all

    if search_street:
        reports = reports.filter(address__contains=search_street)

        if search_street_number:
            reports = reports.filter(address_number=search_street_number)

    if len(reports) > 0 and is_default_position:
        pnt = reports[0].point

    reports = reports.distance(pnt)

    if search_radius:
        reports = reports.filter(point__distance_lte=(pnt, search_radius))

    reports = reports.distance(pnt).order_by('-created')
    return (reports, pnt)


def list(request):
    search_form = SearchIncidentForm(request.GET)
    reports, pnt = filter_reports(request.fmsuser, request.GET)

    zipcodes = ZipCode.objects.filter(hide=False).select_related('commune').order_by('name_' + get_language())

    page_number = request.GET.get("page", 1)
    paginator = Paginator(reports, settings.MAX_ITEMS_PAGE)
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    
    return render_to_response("pro/reports/list.html",
            {
                "pnt":pnt,
                "zipcodes": zipcodes,
                "reports": page,
                "search_form": search_form
            },
            context_instance=RequestContext(request))


def table(request):
    search_form = SearchIncidentForm(request.GET)
    reports, pnt = filter_reports(request.fmsuser, request.GET)

    zipcodes = ZipCode.objects.filter(hide=False).select_related('commune').order_by('name_' + get_language())
    return render_to_response("pro/reports/table.html",
            {
                "pnt":pnt,
                "zipcodes": zipcodes,
                "reports": reports,
                "search_form": search_form
            },
            context_instance=RequestContext(request))
