import httplib
from urllib2 import HTTPError

from django.core import serializers
from django.contrib.gis.measure import D
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.utils import simplejson
from django.db.models import Q
from datetime import datetime, timedelta
from django.contrib.gis.geos import fromstr

from django_fixmystreet.fixmystreet.models import Report, ReportFile, ReportCategory, ReportMainCategoryClass, ReportSecondaryCategoryClass, dictToPoint, FMSUser
from django_fixmystreet.fixmystreet.utils import ssl_required, JsonHttpResponse

from django.core.exceptions import ObjectDoesNotExist

def entity_reports(request):
        '''entity_reports is a method exporting reports for an entity'''
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
            import pdb
            pdb.set_trace()
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
        d1= xml_serializer.serialize(Report.objects.filter(id=report.id),fields=('id','category', 'description', 'created_at', 'updated', 'status'))
        #Get comments of the report
        data2 = Comment.objects.filter(report_id=data1[0].id)
        d2 = xml_serializer.serialize(data2,fields=('title','text'))
        #Get files of the report
        data3 = File.objects.filter(report_id=data1[0].id)
        d3 = xml_serializer.serialize(data3,fields=('title','file'))
        #Concat serialized data
        d = d+ d1+"<Comments>"+d2+"</Comments><Files>"+d3+"</Files>"
        d = d + "</Report>"
    #Add closing tag
    d = d+"</Reports>"
    #Return the XML structure
    return d
