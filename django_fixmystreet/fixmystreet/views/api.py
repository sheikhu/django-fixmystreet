import httplib
from urllib2 import HTTPError

from django.contrib.gis.measure import D
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.utils import simplejson
from django.db.models import Q
from datetime import datetime, timedelta

from django_fixmystreet.fixmystreet.models import Report, ReportCategory, dictToPoint, FMSUser
from django_fixmystreet.fixmystreet.utils import ssl_required, JsonHttpResponse

from django.core.exceptions import ObjectDoesNotExist

def login_user(request):
        '''login_user is a method used by the mobiles to connect a user to the application'''
        try:
            postedData = simplejson.loads(request.POST.items()[0][0])
        except ValueError:
            #Catching malformed input request data
            return HttpResponseBadRequest(simplejson.dumps({"request":request.POST.items()[0][0]}),mimetype='application/json')
        
        user_email    = postedData.get('email')
        user_password = postedData.get('password')
        
        #Invalid request. Expected values are not present
        if (user_email == None or user_password == None):
            return HttpResponseBadRequest(simplejson.dumps({"email":user_email}),mimetype='application/json')
        
        try:
            #Search user
            user_object   = FMSUser.objects.get(email=user_email)
            if user_object.check_password(user_password) == False:
                #Bad Password
                return HttpResponseForbidden(simplejson.dumps({"email": user_email}),mimetype='application/json')
        except ObjectDoesNotExist:
            #The user has not the right to access the login section (Based user/pass combination
            return HttpResponseForbidden(simplejson.dumps({"email": user_email}),mimetype='application/json')
        
        #Right ! Logged in :-)
        return HttpResponse(user_object.toJSON(),mimetype='application/json')


# deprecated ! service.gis.irisnet.be support jsonp
"""
def search(request): 
    conn = httplib.HTTPConnection(settings.LOCAL_API)
    #conn.request("POST", "/WSGeoloc/Rest/Localize/getstreet", request.raw_post_data.decode('utf-8').encode('iso-8859-15'))
    conn.request("POST", "/urbis/Rest/Localize/getstreet", request.raw_post_data.decode('utf-8'))
    response = conn.getresponse()
    data = response.read()

    conn.close()
    #try:
        #return HttpResponse(data.decode('iso-8859-15'))
    #except UnicodeError:
    return HttpResponse(data,mimetype="text/json")


def locate(request): 
    conn = httplib.HTTPConnection(settings.LOCAL_API)

    #conn.request("POST", "/WSGeoloc/Rest/Localize/getaddressfromcoord", request.raw_post_data)
    conn.request("POST", "/urbis/Rest/Localize/getaddressfromcoord", request.raw_post_data)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    #try:
        #return HttpResponse(data.decode('iso-8859-15'))
    #except UnicodeError:
    return HttpResponse(data,mimetype="text/json")
"""

#Method used to retrieve nearest reports for pro
def near_reports_pro(request):
    pnt = dictToPoint(request.REQUEST)
   
    #Max 1 month in the past 
    timestamp_from = datetime.now().date() - timedelta(days=31)
    reports = Report.objects.filter(Q(created_at__gte=timestamp_from)).distance(pnt).filter('distance',1000).order_by('distance')
    
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
    reports = Report.objects.filter(Q(created_at__gte=timestamp_from) & Q(private=False)).distance(pnt).order_by('distance')[:20]
    
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
    reports = Report.objects.filter(Q(created_at__gte=timestamp_from) & Q(private=False)).distance(pnt).order_by('distance')[:20]
    
    result = []
    
    for i,report in enumerate(reports):
        result.append(report.to_object())

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
    reports = Report.objects.filter(Q(created_at__gte=timestamp_from)).distance(pnt).order_by('distance')[:20]
    result = []
    
    for i,report in enumerate(reports):
        result.append(report.to_object())

    return JsonHttpResponse({
        'status':'success',
        'results':result
    })


@ssl_required
def create_report(request):
    user = None
    if request.user.is_authenticated():
        user = request.user

    data = request.POST
    report = Report()
    report.author = user

    try:
        # Category
        report.category = ReportCategory.objects.get(id=data['category'])
        # Address
        report.point = dictToPoint(data)
        report.postalcode = data['postalcode']
        report.ward = Ward.objects.get(zipcode__code=data['postalcode'])
        report.address = data['address']
        # Photo
        report.photo = request.FILES.get('photo')
        # Description
        report.desc = data.get('description')
    except Exception as e:
        return JsonHttpResponse('error', {
            'errortype':'validation_error',
            'message': 'Some data are invalid {0}'.format(e)
        })

    report.save()
    
    
    return JsonHttpResponse({
        'user': user.get_full_name(),
        'report': {
            'id':report.id
        }
    })
