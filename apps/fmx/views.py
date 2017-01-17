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

def detail(request, report_id):
    response = get_response()

    try:
        report = Report.objects.all().public().get(id=report_id)

        responsible = "%s - %s (%s)" %(report.responsible_department.name,report.responsible_entity.name, report.responsible_department.phone)

        response['response'] = {
            "id": report.get_ticket_number(),
            "status": report.status,
            "statusLabel": report.get_public_status_display(),
            "category": report.display_category(),
            "created": report.created.strftime('%d/%m/%Y'),
            "responsible": responsible,
            "address": report.display_address(),
            "point": {
                "x": report.point.x,
                "y": report.point.y
            },
        }

        # Generate PDF absolute url
        site = Site.objects.get_current()
        base_url = "http://{}".format(site.domain.rstrip("/"))
        relative_pdf_url = reverse("report_pdf", args=[report_id]).lstrip("/")
        absolute_pdf_url = "{}/{}".format(base_url, relative_pdf_url)

        response['_links'] = {
            "self" : "/%s" % report.id,
            "download" : absolute_pdf_url
        }
    except Report.DoesNotExist:
        exception = {
          "type": "ERROR",
          "code": 404,
          "description": "Report does not exist"
        }

        return return_exception(exception, 404)

    return return_response(response)

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
