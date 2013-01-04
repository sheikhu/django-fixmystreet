from datetime import datetime

from django.core import serializers
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.utils import simplejson

from django_fixmystreet.fixmystreet.models import Report, ReportComment, ReportFile, FMSUser
from django_fixmystreet.fixmystreet.utils import JsonHttpResponse

from django.core.exceptions import ObjectDoesNotExist
import csv

def entity_reports(request):
    """entity_reports is a method exporting reports for an entity"""
    entity_username = None
    entity_pass = None
    from_date = None
    to_date = None

    entity_object = None
    
    #Get objects in the POST request
    ################################
    try:
        entity_username    = request.POST.get('entity_username')
        entity_pass        = request.POST.get('entity_pass')
        from_date          = request.POST.get('from_date')
        to_date            = request.POST.get('to_date')
    except ValueError:
        #Catching malformed input request data
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_EXPORT_ENTITY_REPORTS_INVALID_REQUEST","request":request.POST}),mimetype='application/json')
    #Invalid request. Expected values are not present
    if (entity_username == None):
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_EXPORT_ENTITY_REPORTS_MISSING_ENTITY_USERNAME","request":request.POST})	,mimetype='application/json')
    if (entity_pass == None):
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_EXPORT_ENTITY_REPORTS_MISSING_ENTITY_PASS","request":request.POST}),mimetype='application/json')
    if (from_date == None):
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_EXPORT_ENTITY_REPORTS_MISSING_DATE_FROM","request":request.POST}),mimetype='application/json')
    if (to_date == None):
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_EXPORT_ENTITY_REPORTS_MISSING_DATE_TO","request":request.POST}),mimetype='application/json')

    #Verify than the difference betweendate from and to is max 365 days
    ###################################################################
    d1 = datetime.strptime(from_date, "%Y-%m-%d")
    d2 = datetime.strptime(to_date, "%Y-%m-%d")
    date_diff = abs((d2 - d1).days)
    if (date_diff > 365):
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_EXPORT_ENTITY_REPORTS_MORE_THAN_365_DAYS_REQUESTED","request":request.POST}),mimetype='application/json')

    #Get objects in the DB to verify if it exists
    #############################################
    try:            
        entity_object   = FMSUser.objects.get(username=entity_username)
    except ObjectDoesNotExist:
        #The report is unknown
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_EXPORT_ENTITY_REPORTS_ENTITY_NOT_FOUND","entity": entity_username}),mimetype='application/json')

    #Verify is the given user are actives
    if entity_object.is_active == False:
        return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_EXPORT_ENTITY_REPORTS_REPORT_ENTITY_IS_NOT_ACTIVE","entity": entity_username}),mimetype='application/json')
    
    #Verify if the given entity username has the right entity / Leader
    ##################################################################
    if (not entity_object.leader):
        #Bad role
        return HttpResponseForbidden(simplejson.dumps({"error_key":"ERROR_EXPORT_ENTITY_REPORTS_ENTITY_NOT_LEADER","entity": entity_username}),mimetype='application/json')

    #Verify entity password
    #############################################
    if entity_object.check_password(entity_pass) == False:
        #Bad Password
        return HttpResponseForbidden(simplejson.dumps({"error_key":"ERROR_EXPORT_ENTITY_REPORTS_ENTITY_BAD_PASSWORD","entity": entity_username}),mimetype='application/json')

    #If everything is ok, then return all requested reports as XML 
    ##############################################################
    xml_structure = Report.objects.filter(responsible_entity__id = entity_object.organisation.id, created__gte = from_date, created__lte = to_date)
    #Job Done
    #Return signal to the caller
    return JsonHttpResponse({
        'status':'success',
        'reports':export_reports_of_entity(xml_structure)
    })

def contractor_reports(request):
        '''contractor_reports is a method exporting reports for an entity'''
        entity_username = None
        entity_pass = None
        from_date = None
        to_date = None

        entity_object = None
        
        #Get objects in the POST request
        ################################
        try:
            entity_username    = request.POST.get('entity_username')
            entity_pass        = request.POST.get('entity_pass')
            from_date          = request.POST.get('from_date')
            to_date            = request.POST.get('to_date')
        except ValueError:
            #Catching malformed input request data
            return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_EXPORT_ENTITY_REPORTS_INVALID_REQUEST","request":request.POST}),mimetype='application/json')
        #Invalid request. Expected values are not present
        if (entity_username == None):
            return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_EXPORT_ENTITY_REPORTS_MISSING_ENTITY_USERNAME","request":request.POST})	,mimetype='application/json')
        if (entity_pass == None):
            return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_EXPORT_ENTITY_REPORTS_MISSING_ENTITY_PASS","request":request.POST}),mimetype='application/json')
        if (from_date == None):
            return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_EXPORT_ENTITY_REPORTS_MISSING_DATE_FROM","request":request.POST}),mimetype='application/json')
        if (to_date == None):
            return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_EXPORT_ENTITY_REPORTS_MISSING_DATE_TO","request":request.POST}),mimetype='application/json')

        #Get objects in the DB to verify if it exists
        #############################################
        try:            
            entity_object   = FMSUser.objects.get(username=entity_username)
        except ObjectDoesNotExist:
            #The report is unknown
            return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_EXPORT_ENTITY_REPORTS_ENTITY_NOT_FOUND","entity": entity_username}),mimetype='application/json')

        #Verify is the given user are actives
        if entity_object.is_active == False:
            return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_EXPORT_ENTITY_REPORTS_REPORT_ENTITY_IS_NOT_ACTIVE","entity": entity_username}),mimetype='application/json')
        
        #Verify if the given entity username has the right entity / Leader
        ##################################################################
        if (not entity_object.leader):
            #Bad role
            return HttpResponseForbidden(simplejson.dumps({"error_key":"ERROR_EXPORT_ENTITY_REPORTS_ENTITY_NOT_LEADER","entity": entity_username}),mimetype='application/json')

        #Verify entity password
        #############################################
        if entity_object.check_password(entity_pass) == False:
            #Bad Password
            return HttpResponseForbidden(simplejson.dumps({"error_key":"ERROR_EXPORT_ENTITY_REPORTS_ENTITY_BAD_PASSWORD","entity": entity_username}),mimetype='application/json')

        #If everything is ok, then return all requested reports as XML 
        ##############################################################
        xml_structure = Report.objects.filter(responsible_entity__id = entity_object.id, created__gte = from_date, created__lte = to_date)
        
        #Job Done
        #Return signal to the caller
        return JsonHttpResponse({
        'status':'success',
        'reports':export_reports_of_entity(xml_structure)
    })

def manager_reports(request):
        '''manager_reports is a method exporting reports for an entity'''
        entity_username = None
        entity_pass = None
        from_date = None
        to_date = None

        entity_object = None
        
        #Get objects in the POST request
        ################################
        try:
            entity_username    = request.POST.get('entity_username')
            entity_pass        = request.POST.get('entity_pass')
            from_date          = request.POST.get('from_date')
            to_date            = request.POST.get('to_date')
        except ValueError:
            #Catching malformed input request data
            return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_EXPORT_ENTITY_REPORTS_INVALID_REQUEST","request":request.POST}),mimetype='application/json')
        #Invalid request. Expected values are not present
        if (entity_username == None):
            return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_EXPORT_ENTITY_REPORTS_MISSING_ENTITY_USERNAME","request":request.POST})	,mimetype='application/json')
        if (entity_pass == None):
            return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_EXPORT_ENTITY_REPORTS_MISSING_ENTITY_PASS","request":request.POST}),mimetype='application/json')
        if (from_date == None):
            return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_EXPORT_ENTITY_REPORTS_MISSING_DATE_FROM","request":request.POST}),mimetype='application/json')
        if (to_date == None):
            return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_EXPORT_ENTITY_REPORTS_MISSING_DATE_TO","request":request.POST}),mimetype='application/json')

        #Get objects in the DB to verify if it exists
        #############################################
        try:            
            entity_object   = FMSUser.objects.get(username=entity_username)
        except ObjectDoesNotExist:
            #The report is unknown
            return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_EXPORT_ENTITY_REPORTS_ENTITY_NOT_FOUND","entity": entity_username}),mimetype='application/json')

        #Verify is the given user are actives
        if entity_object.is_active == False:
            return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_EXPORT_ENTITY_REPORTS_REPORT_ENTITY_IS_NOT_ACTIVE","entity": entity_username}),mimetype='application/json')
        
        #Verify if the given entity username has the right entity / Leader
        ##################################################################
        if (not entity_object.leader):
            #Bad role
            return HttpResponseForbidden(simplejson.dumps({"error_key":"ERROR_EXPORT_ENTITY_REPORTS_ENTITY_NOT_LEADER","entity": entity_username}),mimetype='application/json')

        #Verify entity password
        #############################################
        if entity_object.check_password(entity_pass) == False:
            #Bad Password
            return HttpResponseForbidden(simplejson.dumps({"error_key":"ERROR_EXPORT_ENTITY_REPORTS_ENTITY_BAD_PASSWORD","entity": entity_username}),mimetype='application/json')

        #If everything is ok, then return all requested reports as XML 
        ##############################################################
        xml_structure = Report.objects.filter(responsible_entity__id = entity_object.id, created__gte = from_date, created__lte = to_date)
        
        #Job Done
        #Return signal to the caller
        return JsonHttpResponse({
        'status':'success',
        'reports':export_reports_of_entity(xml_structure)
    })

def export_reports_of_entity(list_of_reports):
    ''' loop over all reports to get files and comments (Structure result data in correct manner)'''
    #define xml object serializer
    XMLSerializer = serializers.get_serializer("xml")
    xml_serializer = XMLSerializer()
    #Starting tag
    d="<Reports>"
    #For each found report
    for report in list_of_reports:
        d = d+ "<Report>"
        #Get the info of the report
        data1 = Report.objects.filter(id=report.id)
        d1= xml_serializer.serialize(data1,fields=('id','category', 'description', 'created_at', 'updated', 'status'))
        #Get comments of the report
        data2 = ReportComment.objects.filter(report_id=data1[0].id)
        d2 = xml_serializer.serialize(data2,fields=('title','text'))
        #Get files of the report
        data3 = ReportFile.objects.filter(report_id=data1[0].id)
        d3 = xml_serializer.serialize(data3,fields=('title','file'))
        #Concat serialized data
        d = d+ d1+"<Comments>"+d2+"</Comments><Files>"+d3+"</Files>"
        d = d + "</Report>"
    #Add closing tag
    d = d+"</Reports>"
    #Return the XML structure
    return d

def export_reports_to_csv(list_of_reports):
    filename = 'test.csv'
    with open(filename, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['ReportId','Category','Description','Created_at','Updated','Status'])
        for report in list_of_reports:
            row = [report.id,report.category,report.description,report.created_at,report.updated,report.status]
            writer.writerow(row)
    return filename



