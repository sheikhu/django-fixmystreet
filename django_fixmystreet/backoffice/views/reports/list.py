from collections import OrderedDict

from django.db.models import Q
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import get_language
from django.core.exceptions import PermissionDenied

from django_fixmystreet.fixmystreet.models import Report, ZipCode

default_position = {
    'x': '148954.431',
    'y': '170458.371'
}


def table(request):
    zipcodes = ZipCode.objects.filter(hide=False).order_by('name_'+get_language())

    return render_to_response("pro/reports/table.html", {
        'zipcodes': zipcodes,
        'all_zipcodes': ZipCode.objects.all(),
    }, context_instance=RequestContext(request))

def table_content(request, selection=""):
    user = request.fmsuser
    reports = Report.objects.all().visible().related_fields()

    if selection != "subscribed" and selection != "creator":
        if user.organisation:
            reports = reports.entity_responsible(user) | reports.entity_territory(user.organisation)
        elif user.contractor or user.applicant:
            reports = reports.responsible_contractor(user)
        elif not user.is_superuser:
            raise PermissionDenied()

    if selection == "responsible" and user.manager:
        reports = reports.responsible(user)
        reports = reports.filter(pending=False).exclude(Q(status__in=Report.REPORT_STATUS_CLOSED) | Q(status__in=Report.REPORT_STATUS_OFF) | Q(status=Report.REFUSED))
    elif selection == "subscribed":
        reports = reports.subscribed(user)
    elif selection == "contractor_responsible":
        reports = reports.responsible_contractor(user)
    elif selection == "creator":
        reports = reports.filter(created_by=user)
    elif selection == "all":
        # all reports
        pass
    else:
        raise Exception('Bad paramettre selection ' + selection)

    reports = reports.extra(
        select=OrderedDict([
            ('subscribed',
                """SELECT COUNT(subscription.ID)
                    FROM fixmystreet_reportsubscription subscription
                    WHERE subscription.subscriber_id = %s
                    AND subscription.report_id = fixmystreet_report.id
                """),
            # ('transfered',
            #     'SELECT COUNT(previous.ID)
            #         FROM fixmystreet_report_previous_managers previous
            #         WHERE previous.fmsuser_id = %s
            #         AND previous.report_id = fixmystreet_report.id'),
        ]),
        select_params=(
            str(request.fmsuser.id),
            # str(request.fmsuser.id),
        )
    )

    zipcodes = ZipCode.objects.order_by('name_' + get_language())
    zipcodes = dict([(z.code, z.name) for z in zipcodes])

    return render_to_response("pro/reports/table_content.html", {
        "zipcodes": zipcodes,
        "reports": reports.related_fields(),
    }, context_instance=RequestContext(request))
