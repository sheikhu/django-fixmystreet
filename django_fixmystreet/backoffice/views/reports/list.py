from collections import OrderedDict
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import get_language
from django.core.exceptions import PermissionDenied

from django_fixmystreet.fixmystreet.models import Report, ZipCode
from django_fixmystreet.fixmystreet.utils import dict_to_point

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

    reports = Report.visibles.all().filter(merged_with__isnull=True)


    #if the user is an contractor then user the dependent organisation id
    #If the manager is connected then filter on manager
    # if user.agent or user.manager or user.leader:
    if ownership == "responsible":
        reports = reports.responsible(user)
    elif ownership == "subscribed":
        reports = reports.subscribed(user)
    elif ownership == "transfered":
        #List of transfered reports (previous reports)
        reports = user.previous_reports.all()
    elif ownership == "contractor_responsible":
        reports = reports.responsible_contractor(user)
    elif user.organisation:  # ownership == entity
        reports = reports.entity_responsible(user)
    # elif user.contractor or user.applicant:
        #if the user is an contractor then display only report where He is responsible
        #reports = reports.responsible(user)
    # else:
        # raise PermissionDenied()


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


def all_reports(request):
    zipcodes = ZipCode.objects.filter(hide=False).order_by('name_'+get_language())

    return render_to_response("pro/reports/table.html", {
        'zipcodes': zipcodes,
        'all_zipcodes': ZipCode.objects.all(),
    }, context_instance=RequestContext(request))


def table_content(request):
    # reports.annotate(subscribed = Count(subscribers__contains=request.fmsuser))
    # reports.annotate(transfered = Count(transfered__contains=request.fmsuser))

    reports = Report.visibles.all()
    if request.fmsuser.agent or request.fmsuser.manager or request.fmsuser.leader:
        reports = reports.entity_responsible(request.fmsuser) | reports.entity_territory(request.fmsuser.organisation)
    elif request.fmsuser.contractor or request.fmsuser.applicant:
        reports = reports.responsible_contractor(request.fmsuser)
    elif not request.fmsuser.is_superuser:
        raise PermissionDenied()

    # reports, pnt = filter_reports(request.fmsuser, request.GET)

    reports = reports.extra(
        select = OrderedDict([
            ('subscribed',
                """SELECT COUNT(subscription.ID)
                    FROM fixmystreet_reportsubscription subscription
                    WHERE subscription.subscriber_id = %s
                    AND subscription.report_id = fixmystreet_report.id
                """),
            # ('transfered',
            #     'SELECT COUNT(previous.ID) \
            #         FROM fixmystreet_report_previous_managers previous \
            #         WHERE previous.fmsuser_id = %s \
            #         AND previous.report_id = fixmystreet_report.id'),
        ]),
        select_params = (
            str(request.fmsuser.id),
            # str(request.fmsuser.id),
        )
    )

    zipcodes = ZipCode.objects.order_by('name_' + get_language())
    zipcodes = dict([(z.code, z.name) for z in zipcodes])

    return render_to_response("pro/reports/table_content.html",
        {
            "zipcodes": zipcodes,
            "reports": reports,
        },
        context_instance=RequestContext(request))
