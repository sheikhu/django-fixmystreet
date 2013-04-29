import json
import tempfile
import datetime
import os
import logging
from threading import local

from django.http import HttpResponse, HttpResponseRedirect
from django.db.models.signals import post_save
from django.template.loader import render_to_string
from django.conf import settings
from django.template.defaultfilters import slugify, urlize, date as date_filter
from django.utils.translation import ugettext as _
from django.utils.translation import activate, deactivate
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.contrib.gis.geos import fromstr
from django.http import Http404

from south.modelsinspector import add_introspection_rules
import transmeta
from stdimage import StdImageField
from markdown import markdown




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


add_introspection_rules(
    [
        (
            (FixStdImageField, ),
            [],
            {
                "verbose_name": ["verbose_name", {"default": None}],
                "name":         ["name",         {"default": None}],
            },
        ),
    ],
    ["^django_fixmystreet.fixmystreet.utils.FixStdImageField",])

def render_to_pdf(*args, **kwargs):
    tmpfolder = tempfile.mkdtemp()
    html_tmp_file_path = "%s/export.html" %(tmpfolder)
    html_tmp_file = file(html_tmp_file_path, "w")
    html_tmp_file.write(render_to_string(*args, **kwargs).encode("utf-8"))
    html_tmp_file.close()

    pdf_tmp_file_path = "%s/export.pdf" % (tmpfolder)
    cmd = """wkhtmltopdf -s A4 -T 5 -L 5 -R 5 -B 10 \
            --encoding utf-8 \
            --footer-font-size 8 \
            --footer-left '{0}' \
            --footer-center 'Incident: {1}' \
            --footer-right '[page]/[toPage]' {2} {3}
            """.format(
                datetime.date.today().strftime("%d/%m/%y"),
                args[1]['report'].get_ticket_number(),
                html_tmp_file_path,
                pdf_tmp_file_path
            )
    logging.info(cmd)
    os.system(cmd)


    pdf_tmp_file = file(pdf_tmp_file_path, "r")
    response = HttpResponse(pdf_tmp_file.read(), mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=%s%s.pdf' %(u"export-incident-"+str((args[1]['report']).id)+"-date-", datetime.date.today().isoformat())
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

    def process_response(self, request, response):
        set_current_user(None)
        return response


# class AccessControlAllowOriginMiddleware:

#     def process_request(self, request):
#         if 'HTTP_ACCESS_CONTROL_REQUEST_METHOD' in request.META:
#             response = HttpResponse()
#             response['Access-Control-Allow-Methods'] = "GET,POST,OPTIONS"
#             response['Access-Control-Allow-Origin'] = "http://gis.irisnet.be"
#             return response

#     def process_response(self, request, response):
#         '''Add the respective CORS headers'''
#         response['Access-Control-Allow-Methods'] = "GET,POST,OPTIONS"
#         response['Access-Control-Allow-Origin'] = "http://gis.irisnet.be"
#         return response


def transform_notification_user_display(user, to_show):
    if  to_show is None:
        return _("a citizen")

    if to_show.is_pro() and to_show.get_organisation():
        entity_name = to_show.get_organisation().name
    else:
        entity_name = ''

    if user.is_pro():
        return u"{0} {1} ({2})".format(entity_name, to_show.get_full_name(), to_show.email)
    else:
        if to_show.is_pro():
            return entity_name
        else:
            return _("a citizen")

def transform_notification_template(template, report, user, **kwargs):
    from django_fixmystreet.fixmystreet.models import MailNotificationTemplate
    SITE_URL = "http://{0}".format(Site.objects.get_current().domain)

    data = {
        "user": user
    }
    title = list()
    content = list()

    overview_tmp = MailNotificationTemplate.objects.get(name='report-overview')
    opening_tmp = MailNotificationTemplate.objects.get(name='opening')
    closing_tmp = MailNotificationTemplate.objects.get(name='closing')

    trickystuff = get_language()
    for l in settings.LANGUAGES:
        activate(l[0])

        data["report"] = report
        data["created_at"] = date_filter(report.created)
        data["created_by"] = transform_notification_user_display(user, report.citizen or report.created_by)
        data["responsible"] = transform_notification_user_display(user, report.responsible_manager)
        data["address"] = u"{street}, {num} ({code} {commune})".format(street=report.address, num=report.address_number, code=report.postalcode, commune=report.get_address_commune_name())
        data["category"] = report.display_category()

        if user.is_pro():
            data["status"] = report.get_status_display()
        else:
            data["status"] = report.get_public_status_display()

        data["report_overview"] = overview_tmp.content.format(**data)
        opening = opening_tmp.content.format(**data)
        closing = closing_tmp.content.format(**data)

        if user.is_pro():
            data["display_url"] = "{0}{1}".format(SITE_URL, report.get_absolute_url_pro())
            data["pdf_url"]     = "{0}{1}".format(SITE_URL, report.get_pdf_url_pro())
        else:
            data["display_url"] = "{0}{1}".format(SITE_URL, report.get_absolute_url())
            data["pdf_url"]     = "{0}{1}".format(SITE_URL, report.get_pdf_url())


        if user.is_pro():
            data["unsubscribe_url"] = "{0}{1}".format(SITE_URL, reverse("unsubscribe_pro",args=[report.id]))
        else:
            data["unsubscribe_url"] = "{0}{1}?citizen_email={2}".format(SITE_URL, reverse("unsubscribe",args=[report.id]), user.email)

        if user.is_active and template.name == "mark-as-done":
            data["done_motivation"] = report.mark_as_done_motivation
            data["resolver"] = transform_notification_user_display(user, report.mark_as_done_user)

        if 'old_responsible' in kwargs:
            data["old_responsible"] = transform_notification_user_display(user, kwargs['old_responsible'])

        if 'updater' in kwargs:
            data["updater"] = transform_notification_user_display(user, kwargs['updater'])

        title.append(template.title.format(**data))
        content.append(u"{opening}\n\n{content}\n\n{closing}\n".format(content=template.content.format(**data), opening=opening, closing=closing))

        deactivate()

    activate(trickystuff)

    subject = u"incident #{0} - {1}".format(report.id, " / ".join(title))
    text = "\n\n---------------------------\n\n".join(content)
    html = markdown(urlize(text))


    return (subject, html, text)



def dict_to_point(data):
    if not data.has_key('x') or not data.has_key('y'):
        raise Http404('<h1>Location not found</h1>')
    px = data.get('x')
    py = data.get('y')

    return fromstr("POINT(" + px + " " + py + ")", srid=31370)
