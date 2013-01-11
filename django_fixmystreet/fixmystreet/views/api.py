
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.utils import simplejson
from django.db.models import Q
from datetime import datetime, timedelta
from django.contrib.gis.geos import fromstr
from django.contrib.auth import authenticate, login

from django_fixmystreet.fixmystreet.models import Report, ReportFile, ReportCategory, ReportMainCategoryClass, dictToPoint, FMSUser, ZipCode
from django_fixmystreet.fixmystreet.utils import JsonHttpResponse

from django.core.exceptions import ObjectDoesNotExist

def load_zipcodes(request):
        '''load_zipcodes is a method used by the mobiles to retrieve all usable zipcodes'''
        #Right !
        return HttpResponse(ZipCode().get_usable_zipcodes_to_mobile_json(),mimetype='application/json')

def load_categories(request):
        '''load_categories is a method used by the mobiles to load available categories and dependencies'''
        user_name = None
        try:
            user_name    = request.POST.get('user_name')
        except ValueError:
            #Catching malformed input request data
            return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_CATEGORY_INVALID_REQUEST","request":request.POST}),mimetype='application/json')
        #Invalid request. Expected values are not present
        if (user_name == None):
            return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_CATEGORY_INVALID_PARAMETERS","request":request.POST}),mimetype='application/json')
        
        try:
            #Search user
            FMSUser.objects.filter(username=user_name).exists()
        except ObjectDoesNotExist:
            #The user has not the right to access the login section (Based user/pass combination
            return HttpResponseForbidden(simplejson.dumps({"error_key":"ERROR_CATEGORY_INVALID_USER","username": user_name}),mimetype='application/json')
        all_categories = ReportCategory.objects.all().order_by('category_class','secondary_category_class')
 
        #Right ! Logged in :-)
        return HttpResponse(ReportCategory.listToJSON(all_categories), mimetype='application/json')

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
        except ObjectDoesNotExist:
            #The user has not the right to access the login section (Based user/pass combination
            return HttpResponseForbidden(simplejson.dumps({"error_key":"ERROR_LOGIN_NOT_FOUND","username": user_name}),mimetype='application/json')
        
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
    reports = Report.objects.filter(Q(created__gte=timestamp_from)).distance(pnt).order_by('distance')[:20]
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

def create_report_citizen(request):
    """Create a citizens reports. Validation included."""
    data_email                       = request.POST.get('user_email')
    #data_firstname                   = request.POST.get('user_firstname')
    data_firstname               = ''
    data_lastname                 = request.POST.get('user_lastname')
    data_category_id              = request.POST.get('report_category_id')
    data_main_category_id         = request.POST.get('report_main_category_id')
    data_description              = request.POST.get('report_description')
    data_address                  = request.POST.get('report_address')
    data_address_number           = request.POST.get('report_address_number')
    data_zip                      = request.POST.get('report_zipcode')
    data_quality                  = request.POST.get('report_quality')
    data_x                        = request.POST.get('report_x')
    data_y                        = request.POST.get('report_y')
    #data_subscription             = request.POST.get('report_subscription')
    #create a new object
    report = Report()    

    #Verify that everything has been posted to create a citizen report.
    if (data_email == None):
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_REPORT_MISSING_DATA_EMAIL","request":request.POST}),mimetype='application/json')
    #if (data_firstname == None):
    #    return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_REPORT_MISSING_DATA_FIRSTNAME","request":request.POST}),mimetype='application/json')
    if (data_lastname == None):
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_REPORT_MISSING_DATA_LASTNAME","request":request.POST}),mimetype='application/json')
    if (data_category_id == None):
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_REPORT_MISSING_DATA_CATEGORY_ID","request":request.POST}),mimetype='application/json')
    if (data_main_category_id == None):
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_REPORT_MISSING_DATA_MAIN_CATEGORY_ID","request":request.POST}),mimetype='application/json')        
    if (data_description == None):
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_REPORT_MISSING_DATA_DESCRIPTION","request":request.POST}),mimetype='application/json')        
    if (data_address == None):
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_REPORT_MISSING_DATA_ADDRESS","request":request.POST}),mimetype='application/json')        
    if (data_address_number == None):
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_REPORT_MISSING_DATA_ADDRESS_NUMBER","request":request.POST}),mimetype='application/json')        
    if (data_zip == None):
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_REPORT_MISSING_DATA_ZIP","request":request.POST}),mimetype='application/json')        
    if (data_quality == None):
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_REPORT_MISSING_DATA_QUALITY","request":request.POST}),mimetype='application/json')                
    if (data_x == None):
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_REPORT_MISSING_DATA_X","request":request.POST}),mimetype='application/json')                
    if (data_y == None):
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_REPORT_MISSING_DATA_Y","request":request.POST}),mimetype='application/json')                
    #if (data_subscription == None):
    #    return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_REPORT_MISSING_DATA_SUBSCRIPTION","request":request.POST}),mimetype='application/json')                
        
    #Verify if the citizen profile exists
    #Create it if necessary and assign value to citizen attribute.
    try:
        existingUser = FMSUser.objects.get(email=data_email);
        #Assign citizen
        report.citizen = existingUser
    except FMSUser.DoesNotExist:
        #Add information about the citizen connected if it does not exist
        report.citizen = FMSUser.objects.create(username=data_email, email=data_email, first_name=data_firstname, last_name=data_lastname, agent=False, contractor=False, manager=False, leader=False)

    #Assign values to the report.        
    try:
        # Status
        report.status = Report.CREATED
        # Category
        report.category           = ReportMainCategoryClass.objects.get(id=data_main_category_id)
        report.secondary_category = ReportCategory.objects.get(id=data_category_id)
        # Description
        report.description = data_description
        # Address
        report.point = fromstr("POINT(" + data_x + " " + data_y + ")", srid=31370)
        report.postalcode = data_zip
        report.address = data_address
        report.address_number = data_address_number
        report.quality = data_quality
        report.private = False
        #Subscription is automatic.
        #Save given data
        report.save()
    except Exception:
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_REPORT_PROBLEM_DATA","request":request.POST}),mimetype='application/json')    

    #Return the report ID
    return JsonHttpResponse({        
        'report_id': report.id        
    })
    
def create_report_pro(request):
    '''This method is used to create citizens reports. Validation included.'''
    data_username              = request.POST.get('user_name')
    data_password              = request.POST.get('user_p')
    data_category_id              = request.POST.get('report_category_id')
    data_main_category_id         = request.POST.get('report_main_category_id')
    data_description              = request.POST.get('report_description')
    data_address                  = request.POST.get('report_address')
    data_address_number           = request.POST.get('report_address_number')
    data_zip                      = request.POST.get('report_zipcode')
    data_x                        = request.POST.get('report_x')
    data_y                        = request.POST.get('report_y')
    #data_subscription             = request.POST.get('report_subscription')
    #create a new object
    report = Report()    

    #Verify that everything has been posted to create a citizen report.
    if (data_username == None):
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_REPORT_MISSING_DATA_USERNAME","request":request.POST}),mimetype='application/json')
    #if (data_password == None):
    #    return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_REPORT_MISSING_DATA_PASSWORD","request":request.POST}),mimetype='application/json')
    if (data_category_id == None):
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_REPORT_MISSING_DATA_CATEGORY_ID","request":request.POST}),mimetype='application/json')
    if (data_main_category_id == None):
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_REPORT_MISSING_DATA_MAIN_CATEGORY_ID","request":request.POST}),mimetype='application/json')        
    if (data_description == None):
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_REPORT_MISSING_DATA_DESCRIPTION","request":request.POST}),mimetype='application/json')        
    if (data_address == None):
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_REPORT_MISSING_DATA_ADDRESS","request":request.POST}),mimetype='application/json')        
    if (data_address_number == None):
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_REPORT_MISSING_DATA_ADDRESS_NUMBER","request":request.POST}),mimetype='application/json')        
    if (data_zip == None):
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_REPORT_MISSING_DATA_ZIP","request":request.POST}),mimetype='application/json')        
    if (data_x == None):
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_REPORT_MISSING_DATA_X","request":request.POST}),mimetype='application/json')                
    if (data_y == None):
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_REPORT_MISSING_DATA_Y","request":request.POST}),mimetype='application/json')                
        
    #Verify if the citizen profile exists
    #Create it if necessary and assign value to citizen attribute.
    try:
        existingUser = FMSUser.objects.get(username=data_username)
        #Assign creator (as pro user)
        report.created_by = existingUser
    except FMSUser.DoesNotExist:
        #The user has not the right to create a report
        return HttpResponseForbidden(simplejson.dumps({"error_key":"ERROR_REPORT_UNKNOWN_PRO_USER","username": data_username}),mimetype='application/json')

    #Login the user
    user = authenticate(username=data_username, password=data_password)
    if user is not None:
        if user.is_active:
            login(request, user)
        else:
            return HttpResponseForbidden(simplejson.dumps({"error_key":"ERROR_REPORT_USER_NOT_ACTIVE","username": data_username}),mimetype='application/json')
    else:
        return HttpResponseForbidden(simplejson.dumps({"error_key":"ERROR_REPORT_UNKNOWN_PRO_USER","username": data_username}),mimetype='application/json')

    #Assign values to the report.        
    try:
        # Status
        report.status = Report.CREATED
        # Category
        report.category = ReportMainCategoryClass.objects.get(id=data_main_category_id)
        report.secondary_category = ReportCategory.objects.get(id=data_category_id)
        # Description
        report.description = data_description
        # Address
        report.point = fromstr("POINT(" + data_x + " " + data_y + ")", srid=31370)
        report.postalcode = data_zip        
        report.address = data_address        
        report.address_number = data_address_number
        report.private = True
        #Subscription is automatic.
        #Save given data        
        report.save()
    except Exception as e:
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_REPORT_PROBLEM_DATA","request":request.POST, "message": e.message}),mimetype='application/json')    

    #Return the report ID
    return JsonHttpResponse({        
        'report_id': report.id        
    })
    
def create_report_photo(request):
    '''This method is used to create citizens reports. Validation included.'''    
    #Test the submit content size (max 2MB)
    if (int(request.META.get('CONTENT_LENGTH')) > 2000000):
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
        report_file.file_type = ReportFile.IMAGE
        report_file.file = data_file_content
        report_file.report = reference_report
        
        #Save given data        
        report_file.save()
    except Exception:
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_REPORT_FILE_PROBLEM_DATA","request":request.POST}),mimetype='application/json')

    #Return the report ID
    return JsonHttpResponse({
        'report_photo': report_file.id
    })
