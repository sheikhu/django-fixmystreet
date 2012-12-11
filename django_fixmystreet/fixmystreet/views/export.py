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
            user_object   = FMSUser.objects.get(username=user_name)
        except ObjectDoesNotExist:
            #The user has not the right to access the login section (Based user/pass combination
            return HttpResponseForbidden(simplejson.dumps({"error_key":"ERROR_CATEGORY_INVALID_USER","username": user_name}),mimetype='application/json')
        all_categories = ReportCategory.objects.all().order_by('category_class','secondary_category_class')
 
        #Right ! Logged in :-)
        return HttpResponse(ReportCategory.listToJSON(all_categories),mimetype='application/json')