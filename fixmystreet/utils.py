import json

from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.sites.models import Site
from django.contrib.auth import authenticate

from social_auth.backends import get_backend

import settings


def domain_context_processor(request):
    site = Site.objects.get_current()
    return {'SITE_URL': 'http://{0}'.format(site.domain)}


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

class JsonHttpResponse(HttpResponse):
    data = {}
    def __init__(self, *args, **kwargs):
        args = list(args)
        data = args.pop(0)
        if(isinstance(data, str)):
            self.data['status'] = data
            data = args.pop(0)
        else:
            self.data['status'] = 'success'
            
        self.data.update(data)

        kwargs['mimetype'] = 'application/json'
        super(JsonHttpResponse, self).__init__(json.dumps(self.data), *args, **kwargs)
