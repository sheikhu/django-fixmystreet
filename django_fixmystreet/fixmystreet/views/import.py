import httplib
from urllib2 import HTTPError

from django.contrib.gis.measure import D
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.utils import simplejson
from django.db.models import Q
from datetime import datetime, timedelta
from django.contrib.gis.geos import fromstr

from django_fixmystreet.fixmystreet.models import Report, ReportFile, ReportCategory, ReportMainCategoryClass, ReportSecondaryCategoryClass, dictToPoint, FMSUser
from django_fixmystreet.fixmystreet.utils import ssl_required, JsonHttpResponse

from django.core.exceptions import ObjectDoesNotExist

def close_report(request):
        '''close_report is a method accessible by 3td party app to close a report'''
        report_id = None
        entity_username = None
        entity_pass = None

        report_object = None
        entity_object = None
        
        #Get objects in the POST request
        ################################
        try:
            report_id          = request.POST.get('report_id')
            entity_username    = request.POST.get('entity_username')
            entity_pass        = request.POST.get('entity_pass')
        except ValueError:
            #Catching malformed input request data
            return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_IMPORT_CLOSE_REPORT_INVALID_REQUEST","request":request.POST}),mimetype='application/json')
        #Invalid request. Expected values are not present
        if (report_id == None):
            return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_IMPORT_CLOSE_REPORT_MISSING_REPORT_ID","request":request.POST})	,mimetype='application/json')
        if (entity_username == None):
            return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_IMPORT_CLOSE_REPORT_MISSING_ENTITY_USERNAME","request":request.POST})	,mimetype='application/json')
        if (entity_pass == None):
            return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_IMPORT_CLOSE_REPORT_MISSING_ENTITY_PASS","request":request.POST}),mimetype='application/json')

        #Get objects in the DB to verify if it exists
        #############################################
        try:            
            report_object   = Report.objects.get(id=report_id)
        except ObjectDoesNotExist:
            #The report is unknown
            return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_IMPORT_CLOSE_REPORT_REPORT_NOT_FOUND","report": report_id}),mimetype='application/json')
        try:            
            entity_object   = FMSUser.objects.get(username=entity_username)
        except ObjectDoesNotExist:
            #The report is unknown
            return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_IMPORT_CLOSE_REPORT_ENTITY_NOT_FOUND","entity": entity_username}),mimetype='application/json')

        #Verify if the report is not already closed
        ###########################################
        if (report_object.status == Report.PROCESSED):
            #The report is already closed
            return HttpResponseBadRequest(simplejson.dumps({"error_key":"ERROR_IMPORT_CLOSE_REPORT_ALREADY_CLOSED","report": report_id}),mimetype='application/json')

        #Verify if the given entity username has the right entity / Leader
        ##################################################################
        if (not entity_object.leader):
            #Bad role
            return HttpResponseForbidden(simplejson.dumps({"error_key":"ERROR_IMPORT_CLOSE_REPORT_ENTITY_NOT_LEADER","entity": entity_username}),mimetype='application/json')

        #Verify if the given entity id is the one responsible for the given report
        ##########################################################################
        if (not report_object.responsible_entity.id == entity_object.organisation.id):
            #Bad entity id to handle this report
            return HttpResponseForbidden(simplejson.dumps({"error_key":"ERROR_IMPORT_CLOSE_REPORT_ENTITY_DIFFERENT_THAN_THE_ONE_RESPONSIBLE_FOR_THE_REPORT","entity": entity_username}),mimetype='application/json')

        #Verify entity password
        #############################################
        if entity_object.check_password(entity_pass) == False:
            #Bad Password
            return HttpResponseForbidden(simplejson.dumps({"error_key":"ERROR_IMPORT_CLOSE_REPORT_ENTITY_BAD_PASSWORD","entity": entity_username}),mimetype='application/json')

        #If everything is ok, then close the report and update closing date
        ###################################################################
        report_object.status = Report.PROCESSED
        report_object.close_date = datetime.now()
        report_object.save()
        
        #Job Done
        #Return signal to the caller
        return JsonHttpResponse({
        'status':'success',
        'report':report_object.to_full_JSON()
    })