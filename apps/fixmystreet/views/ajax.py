import os
import json

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseNotFound
from django.utils.translation import ugettext as _
from django.conf import settings

from apps.fixmystreet.models import ReportMainCategoryClass, Report
from apps.fixmystreet.session_manager import SessionManager


SRID_SPHERICAL_MERCATOR = 3857
SRID_EQUIRECTANGULAR = 4326
SRID_ELLIPTICAL_MERCATOR = 3395
DEFAULT_SRID = SRID_EQUIRECTANGULAR


def report_category_note(request, id):
    cat = ReportMainCategoryClass.objects.get(id=id)
    if not cat.hint:
        return HttpResponse("")
    return HttpResponse("<div class='note'><strong>{0}</strong><p>{1}</p></div>".format(
        _("Please Note"),
        cat.hint.label
    ))


def create_comment(request):
    SessionManager.createComment(request.POST.get('title'), request.POST.get('text'), request.session)
    hh = HttpResponse(content='True', content_type='text/html')
    return hh


def create_file(request):
    SessionManager.createFile(request.POST.get('title'), request.POST.get('file'), request.POST.get("file_creation_date"), request.session)
    hh = HttpResponse(content='True', content_type='text/html')
    return hh


def uploadFile(request):
    for file_code in request.FILES:
        upfile = request.FILES[file_code]
        path = os.path.join(settings.PROJECT_PATH, 'media/files/')
        if not os.path.exists(path):
            os.makedirs(path)
        with open(path + upfile.name, 'wb+') as destination:
            for chunk in upfile.chunks():
                destination.write(chunk)
    hh = HttpResponse(content='True', content_type='text/html')
    return hh


def get_report_popup_details(request):
    try:
        report = Report.objects.all().related_fields().visible().public().transform(DEFAULT_SRID).get(id=request.REQUEST.get("id"))
    except Report.DoesNotExist:
        return HttpResponseNotFound()

    response = {
        "id": report.id,
        "type": report.get_status_for_js_map(),
        "latlng": [report.point.x, report.point.y],
        "address": {
            "street": report.address,
            "number": report.address_number,
            "postalCode": report.postalcode,
            "city": report.get_address_commune_name(),
        },
        "categories": report.get_category_path(),
        "photo": report.thumbnail,
        "icons": report.get_icons_for_js_map(),
        "url": reverse("report_show", args=[report.get_slug(), report.id]),
    }
    response_json = json.dumps(response)
    return HttpResponse(response_json, content_type="application/json")


def filter_map(request):  # pylint: disable=W0613
    reports = Report.objects.all().visible().public().transform(DEFAULT_SRID).values("id", "status", "point")

    features = []
    for report in reports:
        # report.point.transform(DEFAULT_SRID)
        features.append({
            "type": "Feature",
            "properties": {
                "id": report["id"],
                # "type": report.get_status_for_js_map(),
                "type": Report.static_get_status_for_js_map(report["status"]),
                # "address": {
                #     "street": report.address,
                #     "number": report.address_number,
                #     "postalCode": report.postalcode,
                #     "city": report.get_address_commune_name(),
                # },
                # "categories": report.get_category_path(),
                # "photo": report.thumbnail,
                # "icons": report.get_icons_for_js_map(),
                # "url": reverse("report_show", args=[report.get_slug(), report.id]),
            },
            "geometry": {
                "type": "Point",
                "coordinates": [report["point"].x, report["point"].y]
            }
        })

    geo = {
        "type": "FeatureCollection",
        "features": features
    }
    geo_json = json.dumps(geo)
    return HttpResponse(geo_json, content_type="application/json")
