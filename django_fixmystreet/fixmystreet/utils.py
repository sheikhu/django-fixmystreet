import json
import tempfile
import datetime
import os
import logging
from threading import local

from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate
from django.core.files import File
from django.core.files.base import ContentFile
from django.db.models.signals import post_save
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.conf import settings

from django.core.mail import EmailMultiAlternatives

from stdimage import StdImageField


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
        # if not issubclass(cls, )
        post_save.connect(self.fix_exif_data, sender=cls)
        super(FixStdImageField, self).contribute_to_class(cls, name)


def render_to_pdf(request, *args, **kwargs):
    tmpfolder = tempfile.mkdtemp()
    html_tmp_file_path = "%s/export.html" %(tmpfolder)
    html_tmp_file = file(html_tmp_file_path, "w")
    html_tmp_file.write(render_to_string(request, *args, **kwargs).encode("utf-8"))
    html_tmp_file.close()

    pdf_tmp_file_path = "%s/export.pdf" % (tmpfolder)

    cmd = """wkhtmltopdf -s A4 -T 5 -L 5 -R 5 -B 10 \
            --footer-font-size 8 \
            --footer-left '{0}' \
            --footer-center '' \
            --footer-right '[page]/[toPage]' {1} {2}
            """.format(
                datetime.date.today().strftime("%d/%m/%y"),
                html_tmp_file_path,
                pdf_tmp_file_path
            )
    logging.info(cmd)
    os.system(cmd)


    pdf_tmp_file = file(pdf_tmp_file_path, "r")
    response = HttpResponse(pdf_tmp_file.read(), mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=%s_%s.pdf' %(u"export", datetime.date.today().isoformat())
    pdf_tmp_file.close()
    return response




_thread_locals = local()

def set_current_user(user):
    _thread_locals.user=user

def get_current_user():
    return getattr(_thread_locals, 'user', None)


class CurrentUserMiddleware:
    def process_request(self, request):
        set_current_user(getattr(request, 'user', None))
