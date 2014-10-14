import json
import csv
import tempfile
import datetime
import hashlib
import os
import re
import logging
from threading import local

from django.http import HttpResponse, HttpResponseForbidden, QueryDict
from django.db.models.signals import post_save
from django.template.loader import render_to_string
from django.shortcuts import render_to_response
from django.conf import settings
from django.template.defaultfilters import slugify, urlize, date as date_filter
from django.utils import simplejson
from django.utils.translation import ugettext as _
from django.utils.translation import activate, deactivate, get_language
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.contrib.gis.geos import fromstr
from django.http import Http404

from south.modelsinspector import add_introspection_rules
import transmeta
from stdimage import StdImageField

import logging
logger = logging.getLogger(__name__)


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
    ["^django_fixmystreet.fixmystreet.utils.FixStdImageField", ])


def render_to_pdf(*args, **kwargs):
    context_instance = kwargs.get('context_instance', None)
    if 'request' in context_instance and 'output' in context_instance.get('request').GET:
        return render_to_response(*args, **kwargs)

    pdf_tmp_file = generate_pdf(*args, **kwargs)
    response = HttpResponse(pdf_tmp_file.read(), mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=%s%s.pdf' % (u"export-incident-"+str((args[1]['report']).id)+"-date-", datetime.date.today().isoformat())
    pdf_tmp_file.close()
    return response


def generate_pdf(*args, **kwargs):
    tmpfolder = tempfile.mkdtemp()
    html_tmp_file_path = "%s/export.html" % (tmpfolder)
    html_tmp_file = file(html_tmp_file_path, "w")
    html_tmp_file.write(render_to_string(*args, **kwargs).encode("utf-8"))
    html_tmp_file.close()

    pdf_tmp_file_path = "%s/export.pdf" % (tmpfolder)
    cmd = """wkhtmltopdf -s A4 -T 5 -L 5 -R 5 -B 10\
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
    return pdf_tmp_file


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
    _thread_locals.user = user


def get_current_user():
    return getattr(_thread_locals, 'user', None)

from django.contrib.auth import authenticate, login


class CurrentUserMiddleware:
    def process_request(self, request):
        if re.compile('^/(.*)/api/').search(request.path_info) and request.method == 'POST' and request.POST.get('username', False) and request.POST.get('password', False):
            user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))

            if user and user.is_active:
                login(request, user)
            else:
                return HttpResponseForbidden(simplejson.dumps({"error_key": "ERROR_LOGIN_INVALID_PARAMETERS", "username": request.POST.get('username')}), mimetype='application/json')

            set_current_user(user.fmsuser)
            request.fmsuser = user.fmsuser
        else:
            set_current_user(getattr(request, 'fmsuser', None))

    def process_response(self, request, response):
        set_current_user(None)
        return response


def transform_notification_user_display(display_pro, to_show):
    if to_show is None:
        return _("a citizen")

    entity_name = ''
    show_department = to_show.__class__.__name__ == 'OrganisationEntity'

    if show_department:
        entity_name = to_show.dependency
    elif to_show.is_pro() and to_show.get_organisation():
        entity_name = unicode(to_show.get_organisation())

    if display_pro:
        if show_department:
            return u"{0} {1} ({2})".format(entity_name, to_show.name, to_show.email).strip()
        else:
            return u"{0} {1} ({2})".format(entity_name, to_show.get_full_name(), to_show.email).strip()
    else:
        if entity_name:
            return entity_name
        else:
            return _("a citizen")


# ! Unused, but needed. It just to generate translations in .po
mail_titles = {
    _('acknowledge-creation'),

    _('announcement-affectation'),
    _('announcement-processed'),

    _('informations_published'),

    _('mail-pdf'),
    _('mark-as-done'),

    _('notify-affectation'),
    _('notify-became-private'),
    _('notify-creation'),
    _('notify-merged'),
    _('notify-planned'),
    _('notify-refused'),
    _('notify-reopen'),
    _('notify-subscription'),
    _('notify-updates'),
    _('notify-validation'),
    _('notify-reopen-request'),
}

def transform_notification_template(template_mail, report, user, old_responsible=None, updater=None, comment=None, files=None, date_planned=None, merged_with=None, reopen_reason=None):
    # Define site url
    SITE_URL = "https://{0}".format(Site.objects.get_current().domain)

    # Prepare data for mail
    display_pro = not user  # send to department
    display_pro = display_pro or user.is_pro()
    data = {
        "user": user
    }
    title = list()
    content = list()

    data["report"] = report
    data["created_at"] = date_filter(report.created)

    #NOTE : the lambda functions below allows translation to be done in the proper language in the template
    data["created_by"] = lambda: transform_notification_user_display(display_pro, report.citizen or report.created_by)
    data["responsible"] = lambda: transform_notification_user_display(display_pro, report.responsible_department)
    data["address"] = lambda: u"{street}, {num} ({code} {commune})".format(street=report.address, num=report.address_number, code=report.postalcode, commune=report.get_address_commune_name())
    data["category"] = lambda: report.display_category()

    if display_pro:
        data["status"] = lambda: report.get_status_display()
    else:
        data["status"] = lambda: report.get_public_status_display()

    if display_pro:
        data["display_url"] = lambda: "{0}{1}".format(SITE_URL, report.get_absolute_url_pro())
        data["pdf_url"] = lambda: "{0}{1}".format(SITE_URL, report.get_pdf_url_pro())
    else:
        data["display_url"] = lambda: "{0}{1}".format(SITE_URL, report.get_absolute_url())
        data["pdf_url"] = lambda: "{0}{1}".format(SITE_URL, report.get_pdf_url())

    if display_pro:
        data["unsubscribe_url"] = lambda: "{0}{1}".format(SITE_URL, reverse("unsubscribe_pro", args=[report.id]))
    else:
        data["unsubscribe_url"] = lambda: "{0}{1}?citizen_email={2}".format(SITE_URL, reverse("unsubscribe", args=[report.id]), user.email)

    if template_mail == "announcement-processed":
        if display_pro:
            data["reopen_request_url"] = lambda: "{0}{1}".format(SITE_URL,reverse('report_reopen_request_pro', kwargs={'report_id': report.id, 'slug':report.get_slug()}))
        else:
            data["reopen_request_url"] = lambda: "{0}{1}".format(SITE_URL,reverse('report_reopen_request', kwargs={'report_id': report.id, 'slug':report.get_slug()}))

    if template_mail == "mark-as-done":
        if updater and updater.is_pro():
            from django_fixmystreet.fixmystreet.models import ReportAttachment, ReportComment
            data["done_motivation"] = ReportComment.objects.filter(report=report, type=ReportAttachment.MARK_AS_DONE).latest('created').text
            data["resolver"] = lambda: transform_notification_user_display(display_pro, updater)
        else:
            data["resolver"] = lambda: _("a citizen")

    if old_responsible:
        data["old_responsible"] = lambda: transform_notification_user_display(display_pro, old_responsible)

    if comment is not None:  # can be ''
        data["comment"] = comment
        data["updater"] = lambda: transform_notification_user_display(display_pro, updater)

    if date_planned:
        data["date_planned"] = date_planned

    if merged_with:
        data["merged_with"] = merged_with.id

    if reopen_reason:
        data["reopen_reason"] = lambda: reopen_reason.get_reason_display()
        # data["reopen_reason_nl"] =
        data["reopen_comment"] = reopen_reason.text
    if template_mail == "notify-refused":
        from django_fixmystreet.fixmystreet.models import ReportAttachment, ReportComment
        data["comment"] = ReportComment.objects.filter(report=report, type=ReportAttachment.REFUSED).latest('created').text


    # Subject mail for each languages.
    # Don't forget to update mail_titles variable (above) to support translations in .po.
    trickystuff = get_language()
    for l in settings.LANGUAGES:
        activate(l[0])
        title.append(_(template_mail).format(user=user))
        deactivate()
    activate(trickystuff)

    subject = u"incident #{0} - {1}".format(report.id, " / ".join(title))

    # Content mail
    content_html = render_to_string("emails/notifications/html/%s.html" % template_mail, data)
    content_txt  = render_to_string("emails/notifications/txt/%s.txt" % template_mail, data)

    return (subject, content_html, content_txt)


def dict_to_point(data):
    if 'x' not in data or 'y' not in data:
        raise Http404('<h1>Location not found</h1>')
    px = data.get('x')
    py = data.get('y')

    return fromstr("POINT(" + px + " " + py + ")", srid=31370)


class RequestFingerprint:
    def __init__(self, request):
        # assume that request.method == "POST":
        self.request = request
        md5 = hashlib.md5()
        md5.update(request.path)
        md5.update(unicode(request.POST))
        self.request_fingerprint = md5.hexdigest()
        if 'request_fingerprint_expire' in request.session and request.session['request_fingerprint_expire'] < datetime.datetime.now():
            # fingerprint expired
            del request.session['request_fingerprint']
            del request.session['request_fingerprint_expire']

    def is_duplicate(self):
        if ('isretry' in self.request.POST):
            return 'request_fingerprint' in self.request.session and self.request.session['request_fingerprint'] == self.request_fingerprint and self.request.POST['isretry'] != 'true'
        return 'request_fingerprint' in self.request.session and self.request.session['request_fingerprint'] == self.request_fingerprint

    def save(self):
        self.request.session['request_fingerprint'] = self.request_fingerprint
        self.request.session['request_fingerprint_expire'] = datetime.datetime.now() + datetime.timedelta(minutes=2)


def export_as_csv_action(description="Export selected objects as CSV file",
                         fields=None, exclude=None, header=True):
    """
    This function returns an export csv action
    'fields' and 'exclude' work like in django ModelForm
    'header' is whether or not to output the column names as the first row
    """
    def export_as_csv(modeladmin, request, queryset):
        """
        Generic csv export admin action.
        based on http://djangosnippets.org/snippets/1697/
        """
        opts = modeladmin.model._meta
        field_names = set([field.name for field in opts.fields])
        if fields:
            fieldset = set(fields)
            field_names = field_names & fieldset
        elif exclude:
            excludeset = set(exclude)
            field_names = field_names - excludeset

        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % unicode(opts).replace('.', '_')

        writer = csv.writer(response)
        if header:
            writer.writerow(list(field_names))
        for obj in queryset:
            writer.writerow([unicode(getattr(obj, field)).encode("utf-8", "replace") for field in field_names])
        return response
    export_as_csv.short_description = description
    return export_as_csv

class CorsMiddleware(object):

    def process_response(self, request, response):
        response['Access-Control-Allow-Origin'] = "*"
        return response


def hack_multi_file(request):
    """
    Transform a ``request.FILES`` containing several lists of files into independent single files.

    Goal: Allow users to select multiple files at once, and to perform that action several times.
    Constraint: A single HTTP request containing form data and files. No Ajax calls.
    Problem: <input:file> cannot be modified in JavaScript.
    Solution:
        Use several <input:file multiple> from which user can have removed some files.
        ``request.FILES`` can therefore contain multiple keys that contains each several files.
        Scan ``request.FILES``, extract (only) the files we need and name keys according to ``ReportFileFormSet``.
        Return a ``QueryDict`` equivalent to ``request.FILES``.

    Example:
        request.POST: {
            ...
            'files-0-file_creation_date': [u'2005-4-1 4:32'],
            'files-0-reportattachment_ptr': [u''],
            'files-0-title': [u''],

            // User has removed "files-1"

            'files-2-file_creation_date': [u'2011-8-18 23:34'],
            'files-2-reportattachment_ptr': [u''],
            'files-2-title': [u''],

            'files-3-file_creation_date': [u'2005-4-5 1:46'],
            'files-3-reportattachment_ptr': [u''],
            'files-3-title': [u''],
            ...
        }
        request.FILES: {
            'files-files-0': [
                <InMemoryUploadedFile: filename-0.jpg (image/jpeg)>,
                <InMemoryUploadedFile: filename-1.jpg (image/jpeg)>,  // Removed by user but sent anyway in request, cf. "problem"
                <InMemoryUploadedFile: filename-2.jpg (image/jpeg)>
            ],
            'files-files-1': [
                <InMemoryUploadedFile: filename-3.jpg (image/jpeg)>
            ]
        }
        request_files: {
            'files-0-file': [<InMemoryUploadedFile: filename-0.jpg (image/jpeg)>],
            'files-2-file': [<InMemoryUploadedFile: filename-2.jpg (image/jpeg)>],
            'files-3-file': [<InMemoryUploadedFile: filename-3.jpg (image/jpeg)>]
        }
    """
    qd = {}  # The hacked request.FILES that will be returned.

    # Collect keys related to this hack and copy as-is the others in `qd`.
    files_keys = []
    for k in request.FILES.keys():
        if k.startswith("files-files-"):
            files_keys.append(k)
        else:
            # Copy as-is the keys that are not related to this hack.
            qd[k] = request.FILES[k]  # Or request.FILES.getlist(k) ?
    # Sort the keys to keep the file index coherent with the JS side.
    files_keys.sort()

    # Loop over uploaded files and keep only the ones that have not been removed by the user.
    file_index = 0
    for k in files_keys:
        for f in request.FILES.getlist(k):
            # If there is a "title" field for this file_index, assume the file has not been removed from the form.
            if request.POST.has_key("files-{}-title".format(file_index)):
                qd["files-{}-file".format(file_index)] = f
            file_index += 1

    # Convert dict to QueryDict (to be equivalent to request.FILES).
    request_files = QueryDict("")
    request_files = request_files.copy()
    request_files.update(qd)

    return request_files

# Decorator: only responsibles can do some action
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

def responsible_permission(func):

    def wrapper(request, report_id):
        from django_fixmystreet.fixmystreet.models import Report, UserOrganisationMembership

        report = get_object_or_404(Report, id=report_id)

        if not UserOrganisationMembership.objects.filter(organisation=report.responsible_department, user=request.user).exists():
            return HttpResponseRedirect(report.get_absolute_url_pro())

        return func(request, report_id)

    return wrapper

from django.core.mail import EmailMultiAlternatives
def send_digest(user, activity, activities_list, date_digest):
    # Render digest mail
    SITE_URL = "https://{0}".format(Site.objects.get_current().domain)

    # Activate the last language used by the user
    activate(user.last_used_language)

    if user.is_pro():
        display_url     = lambda: "{0}{1}".format(SITE_URL, activity.report.get_absolute_url_pro())
        unsubscribe_url = lambda: "{0}{1}".format(SITE_URL, reverse("unsubscribe_pro", args=[activity.report.id]))
    else:
        display_url     = lambda: "{0}{1}".format(SITE_URL, activity.report.get_absolute_url())
        unsubscribe_url = lambda: "{0}{1}?citizen_email={2}".format(SITE_URL, reverse("unsubscribe", args=[activity.report.id]), user.email)

    digests_subscriptions = render_to_string("emails/digest.html", {'activities_list': activities_list, 'display_url': display_url, 'unsubscribe_url': unsubscribe_url, 'date_digest': date_digest})

    logger.info('Sending digest to %s' % user.email)

    msg = EmailMultiAlternatives(_("Digest of the day on Fix My Street"), digests_subscriptions, settings.DEFAULT_FROM_EMAIL, (user.email,))
    msg.send()

    deactivate()
