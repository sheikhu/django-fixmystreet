import json
from django.shortcuts import render
from django.http import HttpResponse
from apps.fixmystreet.models import Report, FMSUser, ReportFile, Site, ReportSubscription
from apps.fixmystreet.forms import CitizenForm, ReportCommentForm, ReportFileForm
from django.forms.models import inlineformset_factory
from django.utils.translation import activate, deactivate
from django.core.urlresolvers import reverse
from apps.fixmystreet.utils import hack_multi_file
from django.utils.translation import ugettext as _
from datetime import datetime
from django.core.validators import validate_email

def get_response():
    return {
        "_links": {
            "self": {
                # href: "https://api.example.com/api/v1/books/123"
            },
        },
        "response": "OK",
        "exceptions": {
        #   "type":"WARN",
        #   "code":3150300,
        #   "description":"Some warning message"
        },
    }

def return_response(response, status=200):
    del response["exceptions"]

    return HttpResponse(json.dumps(response), content_type="application/json", status=status)

def return_exception(exception, status=500):
    response = get_response()

    del response["response"]
    del response["_links"]

    response["exceptions"] = exception

    return HttpResponse(json.dumps(response), content_type="application/json", status=status)

def exit_with_error(description, code=500, type="ERROR"):
    exception = {
      "type": type,
      "code": code,
      "description": description
    }

    return return_exception(exception, code)

def get_translated_value(object, lang, use_uggetext=False):
    activate(lang)

    if use_uggetext:
        value = _(object)
    else:
        if callable(object):
            value = object()
        else:
            value = object

    return value

def ack(request):
    response = get_response()

    return return_response(response)

def attachments(request, report_id):
    if request.method == "POST":
        return add_attachment(request, report_id)
    else:
        return get_attachments(request, report_id)

def add_attachment(request, report_id):
    if request.POST.get('username', None) != None and  request.POST.get('password', None) != None:
        return add_attachment_pro(request, report_id)
    else:
        return add_attachment_citizen(request, report_id)

def add_attachment_pro(request, report_id):
    #Check login and password
    try:
        user_name    = request.POST.get('username')
        user_password = request.POST.get('password')
    except ValueError:
        return exit_with_error("Attachment is not valid", 400)

    if (user_name == None or user_password == None):
        return exit_with_error("Unauthorized", 401)

    try:
        user_object   = FMSUser.objects.get(username=user_name)
        if user_object.check_password(user_password) == False or not user_object.is_active:
            return exit_with_error("Unauthorized", 401)
    except ObjectDoesNotExist:
        return exit_with_error("Unauthorized", 401)

    try:
        report = Report.objects.all().get(id=report_id)
    except Report.DoesNotExist:
        return exit_with_error("Report does not exist", 404)

    return add_attachment_for_user(request, report, user_object)

def add_attachment_citizen(request, report_id):
    try:
        report = Report.objects.all().public().get(id=report_id)
    except Report.DoesNotExist:
        return exit_with_error("Report does not exist", 404)

    if request.POST.get('citizen-last_name', None) == None and request.POST.get('citizen-quality', None) == None and request.POST.get('citizen-telephone', None) == None and request.POST.get('citizen-email', None) == None :
        # No citizen info was sent. We try to get it from the incident
        if report.is_pro():
            return exit_with_error("Report is pro", 401)
        else:
            citizen = report.get_creator()
    else:
        citizen_form = CitizenForm(request.POST, request.FILES, prefix='citizen')
        if not citizen_form.is_valid():
            return exit_with_error("Attachment is not valid : " + ", ".join(citizen_form.errors), 400)
        else:
            citizen = citizen_form.save()

    return add_attachment_for_user(request, report, citizen)

def add_attachment_for_user(request, report, user):
    ReportFileFormSet = inlineformset_factory(Report, ReportFile, form=ReportFileForm, extra=0)
    comment_form = ReportCommentForm(request.POST, request.FILES, prefix='comment')
    file_formset = ReportFileFormSet(request.POST, hack_multi_file(request), instance=report, prefix='files', queryset=ReportFile.objects.none())

    response = get_response()

    try:
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.created_by = user
            comment.report = report
            comment.save()
            attachment = comment
        elif file_formset.is_valid():
            if len(file_formset.files) > 0:
                files = file_formset.save()
                for report_file in files:
                    report_file.created_by = user
                    report_file.save()
                    attachment = report_file
            else:
                return exit_with_error("Attachment is not valid", 400)
        else:
            return exit_with_error("Attachment is not valid : " +  + ", ".join(comment_form.errors) + ", ".join(file_formset.errors), 400)
    except Exception as e:
        return exit_with_error("Attachment is not valid : " + str(e), 400)

    res = {
        "id": attachment.id,
        "created": attachment.created.strftime('%d/%m/%Y')
    }


    if attachment.created_by is None or attachment.created_by.is_citizen():
        res["created_by"] = {
            "en": get_translated_value("A citizen", "fr", True),
            "fr": get_translated_value("A citizen", "fr", True),
            "nl": get_translated_value("A citizen", "nl", True)
        }
    else:
        res["created_by"] = {
            "en": get_translated_value(attachment.get_display_name_as_citizen, "fr").name,
            "fr": get_translated_value(attachment.get_display_name_as_citizen, "fr").name,
            "nl": get_translated_value(attachment.get_display_name_as_citizen, "nl").name,
        }

    response['response'] = res

    return return_response(response)

def get_attachments(request, report_id):
    try:
        report = Report.objects.all().public().get(id=report_id)
    except Report.DoesNotExist:
        return exit_with_error("Report does not exist", 404)

    response = get_response()
    response['response'] = []
    attachments = report.active_attachments()
    for attachment in attachments:
        res = {
            "id": attachment.id,
            "created": attachment.created.strftime('%d/%m/%Y')
        }


        if attachment.created_by is None or attachment.created_by.is_citizen():
            res["created_by"] = {
                "en": get_translated_value("A citizen", "fr", True),
                "fr": get_translated_value("A citizen", "fr", True),
                "nl": get_translated_value("A citizen", "nl", True)
            }
        else:
            res["created_by"] = {
                "en": get_translated_value(attachment.get_display_name_as_citizen, "fr").name,
                "fr": get_translated_value(attachment.get_display_name_as_citizen, "fr").name,
                "nl": get_translated_value(attachment.get_display_name_as_citizen, "nl").name,
            }

        if hasattr(attachment, 'reportfile'):
            res["type"] = "attachment"
            if attachment.reportfile.is_pdf():
                res["file-type"] = "PDF"
            elif attachment.reportfile.is_word():
                res["file-type"] = "WORD"
            elif attachment.reportfile.is_excel():
                res["file-type"] = "EXCEL"
            elif attachment.reportfile.is_image():
                res["file-type"] = "IMG"

            if attachment.reportfile.is_image():
                res["url"] = attachment.reportfile.image.url
                res["thumbnail"] = attachment.reportfile.image.thumbnail.url
            else:
                res["url"] = attachment.reportfile.file.url

            res["title"] =  attachment.reportfile.title
        else:
            res["type"] = "comment"
            res["comment"] = attachment.reportcomment.text
        response['response'].append(res)

    return return_response(response)


def categories(request):
    response = get_response()
    response['response'] = "categories"

    return return_response(response)

def generate_report_response(report):
    response = get_response()

    response['response'] = {
        "id": report.get_ticket_number(),
        "creationDate": report.created.isoformat(),
        "status": report.status,
        "duplicates": report.duplicates,
        "category": {
            "id": report.secondary_category.id,
            "nameEn": get_translated_value(report.display_category, "fr"),
            "nameFr": get_translated_value(report.display_category, "fr"),
            "nameNl": get_translated_value(report.display_category, "nl"),
        },
        "location": {
            "coordinates": {
                "x": report.point.x,
                "y": report.point.y
            },
            "address": {
                "addressType": "REGIONAL" if report.is_regional() else "MUNICIPALITY",
                "streetNameEn": get_translated_value(report, "fr").address,
                "streetNameFr": get_translated_value(report, "fr").address,
                "streetNameNl": get_translated_value(report, "nl").address,
                "streetNumber": report.address_number,
                "postalCode": report.postalcode
            }
        },
        "assignee": {
            "nameEn": "%s - %s (%s)" %(
                get_translated_value(report.responsible_department, "fr").name,
                get_translated_value(report.responsible_entity, "fr").name,
                report.responsible_department.phone
            ),
            "nameFr": "%s - %s (%s)" %(
                get_translated_value(report.responsible_department, "fr").name,
                get_translated_value(report.responsible_entity, "fr").name,
                report.responsible_department.phone
            ),
            "nameNl": "%s - %s (%s)" %(
                get_translated_value(report.responsible_department, "nl").name,
                get_translated_value(report.responsible_entity, "nl").name,
                report.responsible_department.phone
            ),
            "phoneNumber": "029876543"
        }
    }

    # Generate PDF absolute url
    site = Site.objects.get_current()
    base_url = "http://{}".format(site.domain.rstrip("/"))
    relative_pdf_url = reverse("report_pdf", args=[report.id]).lstrip("/")
    absolute_pdf_url = "{}/{}".format(base_url, relative_pdf_url)

    response['_links'] = {
        "self" : "/%s" % report.id,
        "download" : absolute_pdf_url
    }

    return response

def detail(request, report_id):
    try:
        report = Report.objects.all().public().get(id=report_id)
        response = generate_report_response(report)

        return return_response(response)
    except Report.DoesNotExist:
        return exit_with_error("Report does not exist", 404)


from apps.fixmystreet.stats import ReportCountQuery
from apps.fixmystreet.views.main import DEFAULT_SQL_INTERVAL_CITIZEN

def stats(request):
    report_counts = ReportCountQuery(interval=DEFAULT_SQL_INTERVAL_CITIZEN, citizen=True)

    response = get_response()
    response['response'] = {
        "createdCount" : report_counts.recent_new(),
        "inProgressCount": report_counts.recent_updated(),
        "closedCount": report_counts.recent_fixed()
    }

    return return_response(response)

from django.contrib.gis.geos import fromstr
def duplicates(request):

    x = request.GET.get("x", None)
    y = request.GET.get("y", None)

    if x is None or y is None:
        return exit_with_error("Missing coordinates", 400)

    try:
        #Check if coordinates are float
        float(x)
        float(y)
    except ValueError as e:
        return exit_with_error("Invalid coordinates", 400)

    pnt = fromstr("POINT(" + x + " " + y + ")", srid=31370)
    reports_nearby = Report.objects.all().visible().public().near(pnt, 20).related_fields()[0:6]

    response = get_response()
    response["response"] = []
    for report in reports_nearby:
        res = generate_report_response(report)
        if res.get("response", None) is not None:
            rep = res.get("response", None)
            attachments = report.active_attachments().order_by('created')
            for attachment in attachments:
                if attachment.reportfile.is_image():
                    rep['oldest_attachment'] = attachment.reportfile.image.thumbnail.url
                    break
            response["response"].append(rep)

    return return_response(response)

def history(request, report_id):
    try:
        report = Report.objects.all().public().get(id=report_id)
    except Report.DoesNotExist:
        return exit_with_error("Report does not exist", 404)

    response = get_response()
    response["response"] = []

    activities = report.activities.all().order_by('-event_at')
    for activity in activities:
        if activity.is_public_visible():
            act ={
                "id": activity.id,
                "date": activity.event_at.isoformat(),
                "actorEn":  get_translated_value(activity.organisation, "fr").name,
                "actorFr":  get_translated_value(activity.organisation, "fr").name,
                "actorNl":  get_translated_value(activity.organisation, "nl").name,
                "eventEn": get_translated_value(activity.get_public_activity_text, "fr"),
                "eventFr": get_translated_value(activity.get_public_activity_text, "fr"),
                "eventNl": get_translated_value(activity.get_public_activity_text, "nl")
            }
            response["response"].append(act)
    return return_response(response)

def last_reports(request):
    nbr = request.GET.get('n', None)
    if not nbr:
        nbr = 10
    try:
        nbr = int(nbr)
    except ValueError as e:
        return exit_with_error("Invalid number of reports", 400)

    reports = Report.objects.all().public().visible().order_by('-created')[:nbr]
    response = get_response()
    response["response"] = []
    for report in reports:
        res = generate_report_response(report)
        if res.get("response", None) is not None:
            response["response"].append(res.get("response", None))
    return return_response(response)

def reports(request):
    #Page number
    REPORTS_BY_PAGE = 12
    page = request.GET.get('p', None)
    if not page:
        page = 1
    try:
        page = int(page)
    except ValueError as e:
        return exit_with_error("Invalid page parameter", 400)

    #Get filters
    status = request.GET.get('status', None)
    category = request.GET.get('category', None)
    municipality = request.GET.get('municipality', None)
    date_start = request.GET.get('date_start', None)
    date_end = request.GET.get('date_end', None)

    reports = Report.objects.all().public().visible().order_by('-created')
    if(status is not None):
        reports = reports.filter(status=status)

    if(category is not None):
        reports = reports.filter(category_id=category)

    if(municipality is not None):
        reports = reports.filter(postalcode=municipality)

    if(date_start is not None):
        date_start_date = datetime.strptime(date_start, '%Y-%M-%d')
        reports = reports.filter(created__gte=date_start_date)

    if(date_end is not None):
        date_end_date = datetime.strptime(date_end, '%Y-%M-%d')
        reports = reports.filter(created__lte=date_end_date)

    offset = (page -1) * REPORTS_BY_PAGE
    # [offset:offset + REPORTS_BY_PAGE]
    response = get_response()
    response["response"] = {
        "reports": [],
        "count": reports.count()
    }
    for report in reports[offset:offset + REPORTS_BY_PAGE]:
        res = generate_report_response(report)
        if res.get("response", None) is not None:
            response["response"]["reports"].append(res.get("response", None))
    return return_response(response)

def subscribe(request, report_id):
    # get the report
    try:
        report = Report.objects.all().public().get(id=report_id)
    except Report.DoesNotExist:
        return exit_with_error("Report does not exist", 404)

    # get or create citizen
    email = request.POST.get('citizen-email', 'unvalid-email')
    username = request.POST.get('username', None)
    password = request.POST.get('password', None)

    if username is not None:
        return subscribe_pro(report, username, password)
    else:
        return subscribe_citizen(report, email)

def subscribe_citizen(report, email):
    try:
        validate_email(email)
    except Error as e:
        return exit_with_error("Email is not valid - " + str(e), 400)

    try:
        user = FMSUser.objects.get(email=email)
    except FMSUser.DoesNotExist:
        #Add information about the citizen connected if it does not exist
        user = FMSUser.objects.create(username=email, email=email, first_name='ANONYMOUS', last_name='ANONYMOUS', agent=False, contractor=False, manager=False, leader=False)
    return subscribe_user(report, user)

def subscribe_pro(report, username, password):
    try:
        user_object   = FMSUser.objects.get(username=username)
        if user_object.check_password(password) == False or not user_object.is_active:
            return exit_with_error("Unauthorized", 401)
    except ObjectDoesNotExist:
        return exit_with_error("Unauthorized", 401)

    return subscribe_user(report, user_object)


def subscribe_user(report, user):
    #VERIFY THAT A SUBSCRIPTION DOES NOT ALREADY EXIST
    if not ReportSubscription.objects.filter(subscriber=user, report=report).exists():
        subscriber = ReportSubscription(subscriber=user, report=report)
        subscriber.save()

    # Return code 200
    response = get_response()

    return return_response(response)


def unsubscribe(request, report_id):
    # get the report
    try:
        report = Report.objects.all().public().get(id=report_id)
    except Report.DoesNotExist:
        return exit_with_error("Report does not exist", 404)

    # Get the user
    email = request.POST.get('citizen-email', 'unvalid-email')
    username = request.POST.get('username', None)
    password = request.POST.get('password', None)

    if username is not None:
        return unsubscribe_pro(report, username, password)
    else:
        return unsubscibe_citizen(report, email)

def unsubscibe_citizen(report, email):
    try:
        validate_email(email)
    except Error as e:
        return exit_with_error("Email is not valid - " + str(e), 400)

    try:
        user = FMSUser.objects.get(email=email)
    except FMSUser.DoesNotExist:
        return exit_with_error("Subscription does not exist", 404)
    return unsubscribe_user(report, user)

def unsubscribe_pro(report, username, password):
    try:
        user_object   = FMSUser.objects.get(username=username)
        if user_object.check_password(password) == False or not user_object.is_active:
            return exit_with_error("Unauthorized", 401)
    except ObjectDoesNotExist:
        return exit_with_error("Unauthorized", 401)

    return unsubscribe_user(report, user_object)


def unsubscribe_user(report, user):
    response = get_response()
    try:
        subscription = ReportSubscription.objects.get(subscriber=user, report=report)
        subscription.delete()
        # Return code 200
        return return_response(response)
    except ReportSubscription.DoesNotExist:
        # Return code 200
        return return_response(response)

def subscription_count(request, report_id):
    try:
        subscription_count = ReportSubscription.objects.filter(report=report_id).count()
    except Report.DoesNotExist:
        return exit_with_error("Report does not exist", 404)

    response = get_response()
    response['response'] = {
        'count': subscription_count
    }
    # Return code 200
    return return_response(response)

def isFixed(request, report_id):
    # get the report
    try:
        report = Report.objects.all().public().get(id=report_id)
    except Report.DoesNotExist:
        return exit_with_error("Report does not exist", 404)

    report.status = Report.SOLVED
    report.fixed_at = datetime.now()
    report.save()
    # Return code 200
    return return_response(generate_report_response(report))

def incDuplicateCounter(request, report_id):
    try:
        report = Report.objects.all().public().get(id=report_id)
    except Report.DoesNotExist:
        return exit_with_error("Report does not exist", 404)

    report.duplicates = report.duplicates + 1
    report.save()
    # Return code 200
    return return_response(generate_report_response(report))
