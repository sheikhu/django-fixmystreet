import json

from django.shortcuts import render
from django.http import HttpResponse


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

def return_response(response):
    return HttpResponse(json.dumps(response), content_type="application/json")

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

def detail(request, report_id):
    response = get_response()
    response['response'] = report_id

    return return_response(response)

from apps.fixmystreet.stats import ReportCountQuery
from apps.fixmystreet.views.main import DEFAULT_SQL_INTERVAL_CITIZEN

def stats(request):
    report_counts = ReportCountQuery(interval=DEFAULT_SQL_INTERVAL_CITIZEN, citizen=True)

    response = get_response()
    response['response'] = {
        "created" : report_counts.recent_new(),
        "in_progress": report_counts.recent_updated(),
        "closed": report_counts.recent_fixed()
    }

    return return_response(response)
