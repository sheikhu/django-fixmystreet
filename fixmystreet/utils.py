import json

from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.sites.models import Site
from django.contrib.auth import authenticate
from django.core.files import File
from django.core.files.base import ContentFile
from django.db.models.signals import post_save

from social_auth.backends import get_backend

from stdimage import StdImageField
import settings


def domain_context_processor(request):
    site = Site.objects.get_current()
    

    return {
        'SITE_URL': 'http://{0}'.format(site.domain),
        'GEOSERVER': settings.GEOSERVER,
        'SERVICE_GIS': settings.SERVICE_GIS
    }


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


def get_exifs(img):
    from PIL import Image
    from PIL.ExifTags import TAGS

    ret = {}
    info = img._getexif()
    if(not info):
        return ret
    #import pdb;pdb.set_trace()
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        ret[decoded] = value
    return ret

class FixStdImageField(StdImageField):
    def fix_exif_data(self, instance=None, **kwargs):
        img_file = getattr(instance, self.name)
        if img_file:
            path = img_file.path
            #print 'path:',path
            from PIL import Image, ImageOps
            img = Image.open(path)

            exifs = get_exifs(img)
            orientation = 1
            if('Orientation' in exifs):
                orientation = exifs['Orientation']
                
                if(orientation == 3 or orientation == 4):
                    img = img.rotate(180)
                elif(orientation == 5 or orientation == 6):
                    img = img.rotate(-90)
                elif(orientation == 7 or orientation == 8):
                    img = img.rotate(90)

                if(orientation == 2 or orientation == 4 or orientation == 5 or orientation == 7):
                    img = ImageOps.mirror(img)
                
                img.save(path)

    def contribute_to_class(self, cls, name):
        """Call methods for generating all operations on specified signals"""
        post_save.connect(self.fix_exif_data, sender=cls)
        super(FixStdImageField, self).contribute_to_class(cls, name)
