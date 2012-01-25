import json

from social_auth.backends import get_backend
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.conf import settings
from django.http import HttpResponseRedirect
import settings as fms_settings


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
    user = oauthtoken_to_user(request.REQUEST.get('backend'),request.REQUEST.get('access_token'),request)
    if not user:
        return HttpResponse(json.dumps({
            'status':'error',
            'user':user.get_full_name()
        }),mimetype="application/json")
    
    return HttpResponse(json.dumps({
        'status':'success',
        'user':user.get_full_name()
    }),mimetype="application/json")
