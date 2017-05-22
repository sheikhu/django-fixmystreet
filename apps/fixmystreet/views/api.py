from datetime import datetime, timedelta
import json
import urllib2
import socket
import logging
import base64

from django.shortcuts import get_object_or_404

from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from apps.fixmystreet.models import Report, ReportFile, ReportCategory, FMSUser, ZipCode
from apps.fixmystreet.utils import JsonHttpResponse, dict_to_point

logger = logging.getLogger("fixmystreet")

def load_zipcodes(request):
        '''load_zipcodes is a method used by the mobiles to retrieve all usable zipcodes'''
        zips = ZipCode.participates.filter(hide=False)
        return HttpResponse(json.dumps([{'c':z.code, 'p':z.commune.phone} for z in zips]), content_type='application/json')

def load_categories(request):
        '''load_categories is a method used by the mobiles to load available categories and dependencies'''
        all_categories = ReportCategory.objects.all().order_by('category_class','secondary_category_class')
        #Right !
        return HttpResponse(ReportCategory.listToJSON(all_categories), content_type='application/json')

@csrf_exempt
def logout_user(request):
        '''logout_user is a method used by the mobiles to disconnect a user from the application'''
        logout(request);
        #Right ! Logged in :-)
        return HttpResponse({},content_type='application/json')

@csrf_exempt
def login_user(request):
        '''login_user is a method used by the mobiles to connect a user to the application'''
        user_name = None
        user_password = None

        try:
            user_name    = request.POST.get('username')
            user_password = request.POST.get('password')
        except ValueError:
            #Catching malformed input request data
            return HttpResponseBadRequest(json.dumps({"error_key":"ERROR_LOGIN_INVALID_REQUEST","request":request.POST}),content_type='application/json')


        #Invalid request. Expected values are not present
        if (user_name == None or user_password == None):
            return HttpResponseBadRequest(json.dumps({"error_key":"ERROR_LOGIN_INVALID_PARAMETERS","username":user_name}),content_type='application/json')

        try:
            #Search user
            user_object   = FMSUser.objects.get(username=user_name)
            if user_object.check_password(user_password) == False:
                #Bad Password
                return HttpResponseForbidden(json.dumps({"error_key":"ERROR_LOGIN_BAD_PASSWORD","username": user_name}),content_type='application/json')
            if not user_object.is_active:
                return HttpResponseForbidden(json.dumps({"error_key":"ERROR_LOGIN_USER_NOT_ACTIVE","username": user_name}),content_type='application/json')
        except ObjectDoesNotExist:
            #The user has not the right to access the login section (Based user/pass combination
            return HttpResponseForbidden(json.dumps({"error_key":"ERROR_LOGIN_NOT_FOUND","username": user_name}),content_type='application/json')

        #Login the user (for internal correct usage)
        user = authenticate(username=user_name, password=user_password)
        login(request, user)

        #Right ! Logged in :-)
        return HttpResponse(user_object.toJSON(),content_type='application/json')

#Method used to put status of a report from temp to submitted as all pictures were successfully sent.
def commit_report(request):
    reportID = request.POST['reportId']
    report = get_object_or_404(Report, id=reportID)
    report.status = Report.CREATED
    report.save();
    return JsonHttpResponse({
        'status':'success'
    })

#Method used to retrieve nearest reports for pro
def near_reports_pro(request):
    pnt = dict_to_point(request.REQUEST)

    #Max 1 month in the past
    timestamp_from = datetime.now().date() - timedelta(days=31)
    reports = Report.objects.filter(Q(created__gte=timestamp_from)).distance(pnt).filter('distance',1000).order_by('distance')

    result = []
    for i,report in enumerate(reports):
        result.append(report.to_object())

    return JsonHttpResponse({
        'status':'success',
        'results':result
    })


#Method used to retrieve nearest reports for citizens
def near_reports_citizen(request):
    pnt = dict_to_point(request.REQUEST)

    #Max 1 month in the past
    timestamp_from = datetime.now().date() - timedelta(days=31)
    reports = Report.objects.filter(Q(created__gte=timestamp_from) & Q(private=False)).distance(pnt).order_by('distance')[:20]

    result = []
    for i,report in enumerate(reports):
        result.append(report.to_object())

    return JsonHttpResponse({
        'status':'success',
        'results':result
    })


#Method used to retrieve all reports for citizens
def reports_citizen(request):
    pnt = dict_to_point(request.REQUEST)

    #Max 1 month in the past
    timestamp_from = datetime.now().date() - timedelta(days=31)
    reports = Report.objects.filter(Q(created__gte=timestamp_from) & Q(private=False)).distance(pnt).order_by('distance')[:20]

    result = []

    for i,report in enumerate(reports):
        result.append(report.to_object())

    return JsonHttpResponse({
        'status':'success',
        'results':result
    })

#Method used to retrieve all reports for pros on mobiles
def reports_pro_mobile(request):
    pnt = dict_to_point(request.REQUEST)
    reports = Report.objects.filter().distance(pnt).order_by('distance')

    #Max 20 reports
    reports = Report.objects.distance(pnt).order_by('distance')[:30]
    result = []

    for i,report in enumerate(reports):
        result.append(report.to_mobile_JSON())

    return JsonHttpResponse({
        'status':'success',
        'results':result
    })

#Method used to retrieve all reports for pros
def reports_pro(request):
    pnt = dict_to_point(request.REQUEST)
    reports = Report.objects.filter().distance(pnt).order_by('distance')

    #Max 1 month in the past
    timestamp_from = datetime.now().date() - timedelta(days=31)
    reports = Report.objects.filter(Q(created__gte=timestamp_from)).distance(pnt).order_by('distance')[:20]
    result = []

    for i,report in enumerate(reports):
        result.append(report.to_JSON())

    return JsonHttpResponse({
        'status':'success',
        'results':result
    })


from apps.fixmystreet.forms import CitizenForm, CitizenReportForm, ProReportForm, ReportCommentForm
from apps.fixmystreet.utils import RequestFingerprint
from django.core.serializers.json import DjangoJSONEncoder

def create_report(request, several_occurences=False):
    fingerprint = RequestFingerprint(request)

    if not fingerprint.is_duplicate():
        fingerprint.save()

        # Check if citizen or pro
        if request.POST.get('username', False):
            report = create_pro(request, several_occurences)
        else:
            report = create_citizen(request, several_occurences)

        if isinstance(report, HttpResponse):
            return report

        # Set source
        if request.POST.get('source', '').lower() == 'web':
            report.source = Report.SOURCES['WEB']
        else:
            report.source = Report.SOURCES['MOBILE']
        report.save()

        # Return json response
        response = {
            'id': report.id,
            'point': [report.point.x, report.point.y],
            'status': report.status,
            'get_public_status_display': report.get_public_status_display(),
            'get_status_display': report.get_status_display(),
            'created': report.created,
            'created_by': report.created_by.get_display_name() if report.created_by else "",
            'is_pro': report.is_pro(),
            'contractor': report.contractor,
            'category': report.category.name,
            'secondary_category': report.secondary_category.name,
            'sub_category': report.sub_category.name if report.sub_category else "",
            'address': report.display_address(),
            'address_number': report.address_number,
            'address_regional': report.is_regional(),
            'postalcode': report.postalcode,
            'source': report.source,
        }

        return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), content_type="application/json; charset=utf-8")

    response = { "error" : "Duplicate fingerprint"}
    return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), content_type="application/json; charset=utf-8")

def create_citizen(request, several_occurences=False):
    # Get user in DB or create it

    citizen_form = CitizenForm(request.POST, prefix='citizen')

    if not citizen_form.is_valid():
        return HttpResponse(unicode(citizen_form.errors), status=400)

    citizen = citizen_form.save()

    # Create report
    report_form = CitizenReportForm(request.POST, prefix='report')
    comment_form = ReportCommentForm(request.POST, prefix='comment')

    if not report_form.is_valid():
        return HttpResponse(unicode(report_form.errors), status=400)

    report = report_form.save(commit=False)
    report.citizen = citizen
    report.several_occurences = several_occurences
    report.save()

    # Subscribe if wanted
    if (request.POST.get('subscription') == 'true'):
        report.subscribe_author_ws()

    # Create the comment if exists
    if ((request.POST["comment-text"] or comment_form.is_valid()) and request.POST["comment-text"] != ''):
        comment = comment_form.save(commit=False)
        comment.created_by = citizen
        comment.report = report
        comment.is_new_report = True
        comment.save()

    return report

def create_pro(request, several_occurences=False):
    # Login the user
    user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))

    if user and user.is_active:
        login(request, user)
    else:
        return HttpResponseForbidden('invalid username or password')

    # Create report
    report_form = ProReportForm(request.POST, prefix='report')
    comment_form = ReportCommentForm(request.POST, prefix='comment')

    if not report_form.is_valid():
        return HttpResponse(unicode(report_form.errors), status=400)
    report = report_form.save(commit=False)

    report.private = True
    report.several_occurences = several_occurences
    report.save()
    report.subscribe_author()

    # Create the comment if exists
    if ((request.POST["comment-text"] or comment_form.is_valid()) and request.POST["comment-text"] != ''):
        comment = comment_form.save(commit=False)
        comment.report = report
        comment.is_new_report = True
        comment.save()

    return report

@csrf_exempt
def create_report_photo(request):
    '''This method is used to create citizens reports. Validation included.'''
    #Test the submit content size (max 2MB)

    if (int(request.META.get('CONTENT_LENGTH')) > 15000000):
        return HttpResponseBadRequest(json.dumps({"error_key": "ERROR_REPORT_FILE_EXCEED_SIZE", "request":request.POST}),content_type='application/json')

    data_report_id = request.POST.get('report_id')

    # Check if the photo is base64 encoded
    if request.POST.get('base64', False):
        image_data_base64 = request.POST.get('report_file')

        # Extract content and metadata from base64 info
        metadata, file_base64 = image_data_base64.split(';base64,')
        metadata = metadata.replace("data:", "")

        # Extract name and type from metadata
        data_file_type, data_file_name = metadata.split(',')

        # Set (meta)data to file object
        data_file_content = ContentFile(file_base64.decode('base64'), name=data_file_name)
        data_file_content.content_type = data_file_type
    else:
        data_file_content = request.FILES.get('report_file')

    #Verify that everything has been posted to create a citizen report.
    if (data_report_id == None):
        return HttpResponseBadRequest(json.dumps({"error_key": "ERROR_REPORT_FILE_MISSING_DATA_REPORT_ID", "request":request.POST}),content_type='application/json')
    if (data_file_content == None):
        return HttpResponseBadRequest(json.dumps({"error_key": "ERROR_REPORT_FILE_MISSING_DATA_REPORT_FILE", "request":request.POST}),content_type='application/json')

    try:
        #Retrieve the report
        reference_report = Report.objects.get(id=data_report_id)
    except Exception:
        return HttpResponseBadRequest(json.dumps({"error_key": "ERROR_REPORT_FILE_NOT_FOUND", "request":request.POST}),content_type='application/json')

    report_file = ReportFile()
    try:
        report_file.title  = "Mobile Upload"
        report_file.file   = data_file_content
        report_file.report = reference_report
        report_file.file_creation_date = datetime.now()

        # Set same creator than report creator
        report_file.created_by = reference_report.citizen or reference_report.created_by

        #Save given data
        report_file.is_new_report = True
        report_file.save()
    except Exception:
        return HttpResponseBadRequest(json.dumps({"error_key": "ERROR_REPORT_FILE_PROBLEM_DATA", "request":request.POST}),content_type='application/json')

    #Return the report ID
    return JsonHttpResponse({
        'report_photo': report_file.id
    })


def proxy(request, path):
    URL = settings.PROXY_URL

    query = request.META['QUERY_STRING']
    if query:
        path = '{0}{1}?{2}'.format(URL, path, query)
    else:
        path = '{0}{1}'.format(URL, path)

    if request.method == 'POST':
        urbisRequest = urllib2.Request(path, request.raw_post_data)
    else:
        urbisRequest = urllib2.Request(path)

    # logger.warning('PROXY URL {0}'.format(path))

    if request.META.get("HTTP_SOAPACTION"):
        urbisRequest.add_header("SOAPAction", request.META.get("HTTP_SOAPACTION"))
    if request.META.get("CONTENT_TYPE"):
        urbisRequest.add_header("Content-Type", request.META.get("CONTENT_TYPE"))

    try:
        oldtimeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(7)

        opener = urllib2.build_opener()

        try:
            urbis_response = opener.open(urbisRequest)
        except urllib2.HTTPError, e:
            urbis_response = e
    finally:
        socket.setdefaulttimeout(oldtimeout)

    data = urbis_response.read()
    response = HttpResponse(data)
    for key, value in urbis_response.headers.items():
        if key not in ["server", "connection", "transfer-encoding"]:
            response[key] = value

    return response
