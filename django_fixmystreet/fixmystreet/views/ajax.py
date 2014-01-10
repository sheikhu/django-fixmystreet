import os
import json

from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.conf import settings

from django_fixmystreet.fixmystreet.models import ReportMainCategoryClass, Report
from django_fixmystreet.fixmystreet.session_manager import SessionManager


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
    print request.POST
    SessionManager.createFile(request.POST.get('title'), request.POST.get('file'), request.POST.get("file_creation_date"), request.session)
    hh = HttpResponse(content='True', mimetype='text/html')
    return hh

def uploadFile(request):
    for file_code in request.FILES:
        upfile = request.FILES[file_code]
        path = os.path.join(settings.PROJECT_PATH,'media/files/')
        print os.path.exists(path)
        if not os.path.exists(path):
            os.makedirs(path)
        with open(path+upfile.name, 'wb+') as destination:
            for chunk in upfile.chunks():
                destination.write(chunk)
    hh = HttpResponse(content='True',mimetype='text/html')
    return hh

def get_report_popup_details(request):
    report_id = request.REQUEST.get("report_id")
    report = Report.objects.get(id=report_id)
    return HttpResponse(json.dumps(report.full_marker_detail_JSON()), mimetype="application/json")

def filter_map(request):
    mFilter = request.GET["filter"]
    result = []
    if "created" in mFilter:
        result += Report.visibles.all().filter(status=Report.CREATED).public()
    if "in_progress" in mFilter:
        result += Report.visibles.all().filter(status__in=Report.REPORT_STATUS_IN_PROGRESS).public()
    if "closed" in mFilter:
        result+= Report.visibles.all().filter(status__in= Report.REPORT_STATUS_CLOSED).public()
    if mFilter == "":
        result += Report.objects.none()

    jsonString= "["
    for report in result:
        jsonString+= json.dumps(report.marker_detail_short())+","

    jsonString = jsonString[:-1]
    jsonString+= "]"

    return HttpResponse(jsonString,mimetype="application/json")

    # mFilter = request.GET["filter"]
    # result = []
    # # if "created" in mFilter:
    # #     result += Report.objects.all().filter(status=Report.CREATED).public()
    # # if "in_progress" in mFilter:
    # #     result += Report.objects.all().filter(status__in=Report.REPORT_STATUS_IN_PROGRESS).public()
    # # if "closed" in mFilter:
    # #     result+= Report.objects.all().filter(status__in= Report.REPORT_STATUS_CLOSED).public()
    # # if mFilter == "":
    # #     result += Report.objects.none()
    # result = Report.visibles.all().public()

    # import time
    # start = time.time()
    # jsonArray = []
    # for report in result:
    #     jsonArray += report.marker_detail_short()
    # duration = time.time() - start
    # print duration

    # jsonString = json.dumps(jsonArray)

    # return HttpResponse(jsonString, mimetype="application/json")
