
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.utils import simplejson
from django.db.models import Q
from datetime import datetime, timedelta
from django.contrib.gis.geos import fromstr
from django.contrib.auth import authenticate, login, logout
from  django.core.exceptions import ValidationError, ObjectDoesNotExist

from piston.handler import BaseHandler
from piston.utils import validate

from django_fixmystreet.fixmystreet.models import ReportSubscription, Report, ReportFile, ReportCategory, ReportMainCategoryClass, dictToPoint, FMSUser, ZipCode, ReportComment
from django_fixmystreet.fixmystreet.forms import CitizenForm, CitizenReportForm, ProReportForm
from django_fixmystreet.fixmystreet.utils import JsonHttpResponse
from django.views.decorators.csrf import csrf_exempt

def load_zipcodes(request):
        '''load_zipcodes is a method used by the mobiles to retrieve all usable zipcodes'''
        zips = ZipCode.participates.filter(hide=False)
        return HttpResponse(simplejson.dumps([{'c':z.code, 'p':z.commune.phone} for z in zips]), mimetype='application/json')

def load_categories(request):
        '''load_categories is a method used by the mobiles to load available categories and dependencies'''
        all_categories = ReportCategory.objects.all().order_by('category_class','secondary_category_class')
        #Right !
        return HttpResponse(ReportCategory.listToJSON(all_categories), mimetype='application/json')

@csrf_exempt
def logout_user(request):
        '''logout_user is a method used by the mobiles to disconnect a user from the application'''
        logout(request);
        #Right ! Logged in :-)
        return HttpResponse({},mimetype='application/json')

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
            return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_LOGIN_INVALID_REQUEST","request":request.POST}),mimetype='application/json')


        #Invalid request. Expected values are not present
        if (user_name == None or user_password == None):
            return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_LOGIN_INVALID_PARAMETERS","username":user_name}),mimetype='application/json')

        try:
            #Search user
            user_object   = FMSUser.objects.get(username=user_name)
            if user_object.check_password(user_password) == False:
                #Bad Password
                return HttpResponseForbidden(simplejson.dumps({"error_key":"ERROR_LOGIN_BAD_PASSWORD","username": user_name}),mimetype='application/json')
            if not user_object.is_active:
                return HttpResponseForbidden(simplejson.dumps({"error_key":"ERROR_LOGIN_USER_NOT_ACTIVE","username": user_name}),mimetype='application/json')
        except ObjectDoesNotExist:
            #The user has not the right to access the login section (Based user/pass combination
            return HttpResponseForbidden(simplejson.dumps({"error_key":"ERROR_LOGIN_NOT_FOUND","username": user_name}),mimetype='application/json')

        #Login the user (for internal correct usage)
        user = authenticate(username=user_name, password=user_password)
        login(request, user)

        #Right ! Logged in :-)
        return HttpResponse(user_object.toJSON(),mimetype='application/json')



#Method used to retrieve nearest reports for pro
def near_reports_pro(request):
    pnt = dictToPoint(request.REQUEST)

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
    pnt = dictToPoint(request.REQUEST)

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
    pnt = dictToPoint(request.REQUEST)

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
    pnt = dictToPoint(request.REQUEST)
    reports = Report.objects.filter().distance(pnt).order_by('distance')

    #Max 1 month in the past
    timestamp_from = datetime.now().date() - timedelta(days=31)
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
    pnt = dictToPoint(request.REQUEST)
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


@csrf_exempt
def create_report_photo(request):
    '''This method is used to create citizens reports. Validation included.'''
    #Test the submit content size (max 2MB)
    if (int(request.META.get('CONTENT_LENGTH')) > 15000000):
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_REPORT_FILE_EXCEED_SIZE","request":request.POST}),mimetype='application/json')

    data_report_id = request.POST.get('report_id')
    data_file_content = request.FILES.get('report_file')

    report_file = ReportFile()
    #Verify that everything has been posted to create a citizen report.
    if (data_report_id == None):
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_REPORT_FILE_MISSING_DATA_REPORT_ID","request":request.POST}),mimetype='application/json')
    if (data_file_content == None):
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_REPORT_FILE_MISSING_DATA_REPORT_FILE","request":request.POST}),mimetype='application/json')

    try:
        #Retrieve the report
        reference_report = Report.objects.get(id=data_report_id)
    except Exception as e:
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_REPORT_FILE_NOT_FOUND","request":request.POST}),mimetype='application/json')
    try:
        report_file.title = "Mobile Upload"
        report_file.file = data_file_content
        report_file.report = reference_report
        report_file.file_creation_date = datetime.now()
        #Either posted by a citizen or a pro...
        if (reference_report.citizen):
            report_file.created_by = reference_report.citizen
        else:
            report_file.created_by = reference_report.created_by
        #Save given data
        report_file.save()

    except Exception:
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_REPORT_FILE_PROBLEM_DATA","request":request.POST}),mimetype='application/json')
    #Return the report ID
    return JsonHttpResponse({
        'report_photo': report_file.id
    })
