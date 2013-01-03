import json
import tempfile
import datetime
import os
import logging
import shutil
from threading import local

from django.http import HttpResponse, HttpResponseRedirect
from django.db.models.signals import post_save
from django.template.loader import render_to_string
from django.conf import settings
from django.template.defaultfilters import slugify
from django.utils.translation import activate, deactivate

import transmeta
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
    from PIL.ExifTags import TAGS

    ret = {}
    info = None
    try:
        info = img._getexif()
    except:
        print 'no jpg'
    if(not info):
        return ret
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


def autoslug_transmeta(populate_from, populate_to):
    """
    Return a connectable signal function that copy a slugify version of
    "instance.populate_from" to "instance.populate_to".

    This function can be connected to a pre_save singal. Don't forget to
    keep a strong reference to this return value or pass weak=False to connect function
    """
    def autoslug_transmeta_func(sender, instance, *args, **kwargs):
        for lang, _ in getattr(settings, 'LANGUAGES', ()):
            activate(lang)
            value = slugify(getattr(instance, populate_from))
            setattr(instance, transmeta.get_real_fieldname(populate_to, lang), value)
            deactivate()

    return autoslug_transmeta_func





_thread_locals = local()

def set_current_user(user):
    _thread_locals.user=user

def get_current_user():
    return getattr(_thread_locals, 'user', None)


class CurrentUserMiddleware:
    def process_request(self, request):
        set_current_user(getattr(request, 'fmsuser', None))


def save_file_to_server(file_name, file_type, file_extension,file_index,report_id):
        date = datetime.datetime.now()
        filepath = "files/%s/%s/" % (date.year,date.month);
        if not os.path.exists(os.path.join(settings.MEDIA_ROOT,filepath)):
            os.makedirs(os.path.join(settings.MEDIA_ROOT,filepath))
        filepath += "%s_%s_%s.%s" % (file_type,report_id,file_index,file_extension)
        srcpath = str(file_name)
        if not "media" in srcpath:
            srcpath = ("media/%s")%(srcpath)
        srcpath = os.path.join(settings.PROJECT_PATH,srcpath)
        if not os.path.exists(srcpath):
            srcpath = str(file_name)
            if not "media" in srcpath:
                srcpath = ("media/%s")%(srcpath)
            srcpath = os.path.join(settings.MEDIA_ROOT,srcpath)
        if os.path.exists(srcpath):
            shutil.move(srcpath,os.path.join(settings.MEDIA_ROOT,filepath))
            return filepath
        else:
            return str(file_name)
