import json
from urllib2 import HTTPError
from exceptions import KeyError

from social_auth.backends import get_backend
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils import simplejson

import settings as fms_settings
from fixmystreet.models import Report, ReportCategory, Ward, dictToPoint


def ssl_required(view_func):
    """Decorator makes sure URL is accessed over https."""
    def _wrapped_view_func(request, *args, **kwargs):
        if not request.is_secure():
            if getattr(settings, 'HTTPS_SUPPORT', True):
                request_url = request.build_absolute_uri(request.get_full_path())
                secure_url = request_url.replace('http://', 'https://')
                return HttpResponseRedirect(secure_url)
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func

def oauthtoken_to_user(backend_name,token,request,*args, **kwargs):
    """Check and retrieve user with given token.
    """
    backend = get_backend(backend_name,request,"")
    response = backend.user_data(token) or {}
    response['access_token'] = token
    kwargs.update({'response': response, backend_name: True})
    user = authenticate(*args, **kwargs)
    return user

@ssl_required
def create_report(request):
    user = None
    if request.user.is_authenticated():
        user = request.user
    try:
        user = user or oauthtoken_to_user(request.REQUEST.get('backend'),request.REQUEST.get('access_token'),request)
    except HTTPError, e:
        return HttpResponse(json.dumps({
            'status': 'error',
            'code': e.code,
            'errortype':'trasaction_error',
            'message': simplejson.loads(e.read())['error']['message']
        }),mimetype="application/json")

    if not user:
        return HttpResponse(json.dumps({
            'status':'error',
            'errortype':'connection_error',
            'message': 'Enable to authenticate user'
        }),mimetype="application/json")

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
    except Exception, e:
        return HttpResponse(json.dumps({
            'status':'error',
            'errortype':'validation_error',
            'message': 'Some data are invalid {}'.format(e)
        }),mimetype="application/json")

    report.save()
    
    
    return HttpResponse(json.dumps({
        'status': 'success',
        'user': user.get_full_name(),
        'report': {
            'id':report.id
        }
    }),mimetype="application/json")
