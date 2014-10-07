import os
import json

#from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.conf import settings

from django_fixmystreet.fixmystreet.models import ReportMainCategoryClass, Report
from django_fixmystreet.fixmystreet.session_manager import SessionManager


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
    hh = HttpResponse(content='True', mimetype='text/html')
    return hh


def create_file(request):
    SessionManager.createFile(request.POST.get('title'), request.POST.get('file'), request.POST.get("file_creation_date"), request.session)
    hh = HttpResponse(content='True', mimetype='text/html')
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
    hh = HttpResponse(content='True', mimetype='text/html')
    return hh


def get_report_popup_details(request):
    report_id = request.REQUEST.get("report_id")
    report = Report.objects.all().visible().public().related_fields().get(id=report_id)
    return HttpResponse(json.dumps(report.full_marker_detail_JSON()), mimetype="application/json")


def filter_map(request):
    reports = Report.objects.all().visible().public().transform(DEFAULT_SRID)

    features = []
    for report in reports:
        # report.point.transform(DEFAULT_SRID)
        features.append({
            "type": "Feature",
            "properties": {
                "id": report.id,
                "type": report.get_status_for_js_map(),
                #"address": {
                #    "street": report.address,
                #    "number": report.address_number,
                #    "postalCode": report.postalcode,
                #    "city": report.get_address_commune_name(),
                #},
                #"categories": report.get_category_path(),
                #"photo": report.thumbnail,
                #"icons": {
                #    "regionalRoads": report.is_regional(),
                #    "pro": report.is_pro(),
                #    "assigned": report.is_contractor_or_applicant_assigned(),
                #    "priority": report.get_priority(),
                #    "solved": report.is_solved(),
                #},
                #"url": reverse("report_show", args=[report.get_slug(), report.id]),
            },
            "geometry": {
                "type": "Point",
                "coordinates": [report.point.x, report.point.y]
            }
        })

    geo = {
        "type": "FeatureCollection",
        "features": features
    }
    return HttpResponse(json.dumps(geo), mimetype="application/json")
