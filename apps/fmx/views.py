import json

from django.shortcuts import render
from django.http import HttpResponse

from apps.fixmystreet.models import Report

def get_response():
    return {
        "_links": {
            "self": {
                # href: "https://api.example.com/api/v1/books/123"
            },
        },
        "response": "OK",
        "exceptions": {
        #   "type":"WARN",
        #   "code":3150300,
        #   "description":"Some warning message"
        },
    }

def return_response(response, status=200):
    del response["exceptions"]

    return HttpResponse(json.dumps(response), content_type="application/json", status=status)

def return_exception(exception, status=500):
    response = get_response()

    del response["response"]
    del response["_links"]

    response["exceptions"] = exception

    return HttpResponse(json.dumps(response), content_type="application/json", status=status)

from django.utils.translation import activate, deactivate

def get_translated_value(object, lang):
    activate(lang)

    if callable(object):
        value = object()
    else:
        value = object

    return value

def ack(request):
    response = get_response()

    return return_response(response)

def attachments(request, report_id):
    response = get_response()
    response['response'] = "attachments of %s" % report_id

    return return_response(response)

def categories(request):
    response = get_response()
    response['response'] = "categories"

    return return_response(response)

from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

def generate_report_response(report):
    response = get_response()

    responsible = "%s - %s (%s)" %(report.responsible_department.name,report.responsible_entity.name, report.responsible_department.phone)

    response['response'] = {
        "id": report.get_ticket_number(),
        "created": report.created.strftime('%d/%m/%Y'),
        "status": {
            "value": report.status,
            "en": get_translated_value(report.get_public_status_display, "fr"),
            "fr": get_translated_value(report.get_public_status_display, "fr"),
            "nl": get_translated_value(report.get_public_status_display, "nl"),
        },
        "category": {
            "en": get_translated_value(report.display_category, "fr"),
            "fr": get_translated_value(report.display_category, "fr"),
            "nl": get_translated_value(report.display_category, "nl"),
        },
        "responsible": {
            "en": get_translated_value(responsible, "fr"),
            "fr": get_translated_value(responsible, "fr"),
            "nl": get_translated_value(responsible, "nl"),
        },
        "address": {
            "en": get_translated_value(report.display_address, "fr"),
            "fr": get_translated_value(report.display_address, "fr"),
            "nl": get_translated_value(report.display_address, "nl"),
        },
        "point": {
            "x": report.point.x,
            "y": report.point.y
        },
    }

    # Generate PDF absolute url
    site = Site.objects.get_current()
    base_url = "http://{}".format(site.domain.rstrip("/"))
    relative_pdf_url = reverse("report_pdf", args=[report.id]).lstrip("/")
    absolute_pdf_url = "{}/{}".format(base_url, relative_pdf_url)

    response['_links'] = {
        "self" : "/%s" % report.id,
        "download" : absolute_pdf_url
    }

    return response

def detail(request, report_id):
    try:
        report = Report.objects.all().public().get(id=report_id)
        response = generate_report_response(report)

        return return_response(response)
    except Report.DoesNotExist:
        exception = {
          "type": "ERROR",
          "code": 404,
          "description": "Report does not exist"
        }

        return return_exception(exception, 404)

from apps.fixmystreet.stats import ReportCountQuery
from apps.fixmystreet.views.main import DEFAULT_SQL_INTERVAL_CITIZEN

def stats(request):
    report_counts = ReportCountQuery(interval=DEFAULT_SQL_INTERVAL_CITIZEN, citizen=True)

    response = get_response()
    response['response'] = {
        "createdCount" : report_counts.recent_new(),
        "inProgressCount": report_counts.recent_updated(),
        "closedCount": report_counts.recent_fixed()
    }

    return return_response(response)

from django.contrib.gis.geos import fromstr
def duplicates(request):

    x = request.GET.get("x", None)
    y = request.GET.get("y", None)

    if x is None or y is None:
        exception = {
          "type": "ERROR",
          "code": 404,
          "description": "Missing coordinates"
        }

        return return_exception(exception, 404)

    try:
        #Check if coordinates are float
        float(x)
        float(y)
    except ValueError as e:
        exception = {
          "type": "ERROR",
          "code": 404,
          "description": "Invalid coordinates"
        }

        return return_exception(exception, 404)

    pnt = fromstr("POINT(" + x + " " + y + ")", srid=31370)
    reports_nearby = Report.objects.all().visible().public().near(pnt, 20).related_fields()[0:6]

    response = get_response()
    response["response"] = []
    for report in reports_nearby:
        res = generate_report_response(report)
        if res.get("response", None) is not None:
            response["response"].append(res.get("response", None))

    return return_response(response)
