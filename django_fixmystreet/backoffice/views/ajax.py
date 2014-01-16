
import re
import json

from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template import RequestContext

from django_fixmystreet.fixmystreet.models import (
    OrganisationEntity, ReportCategory,
    Report, ReportMainCategoryClass, MailNotificationTemplate)
from django_fixmystreet.fixmystreet.utils import get_current_user, transform_notification_template
from django_fixmystreet.fixmystreet.utils import generate_pdf


def saveCategoryConfiguration(request):
    categoriesList = request.REQUEST.getlist("category")
    groupsList = request.REQUEST.getlist("group")

    # Assign new groups to categories. So for each group, add category to dispatch_categories
    for idx, groupParam in enumerate(groupsList):
        newGroup = OrganisationEntity.objects.get(id=groupParam)
        category = ReportCategory.objects.get(pk=categoriesList[idx])

        # Before add, need to remove this category from the old group.
        oldGroups = category.assigned_to_department.filter(dependency=request.user.fmsuser.get_organisation)
        for group in oldGroups:
            group.dispatch_categories.remove(category)

        newGroup.dispatch_categories.add(category)

    return HttpResponseRedirect(reverse("category_gestionnaire_configuration"))


def get_report_popup_details(request):
    report_id = request.REQUEST.get("report_id")
    report = Report.objects.all().related_fields().get(id=report_id)
    return HttpResponse(json.dumps(report.full_marker_detail_pro_JSON()), mimetype="application/json")


def updatePriority(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    report.gravity = int(request.GET["gravity"])
    report.probability = int(request.GET["probability"])
    report.save()
    return HttpResponse(json.dumps({"priority": report.get_priority()}), mimetype="application/json")


def report_false_address(request, report_id):
    if request.method == "POST":
        report = get_object_or_404(Report, id=report_id)

        false_address = request.POST.get('false_address')
        report.false_address = false_address
        report.save()

        return HttpResponse(report.false_address)


def secondary_category_for_main_category(request):
    main_category_id = int(request.GET["main_category"])
    secondary_categories = ReportCategory.objects.filter(category_class=main_category_id)
    jsonstring = ReportCategory.listToJSON(secondary_categories)
    return HttpResponse(jsonstring, mimetype="application/json")


def update_category_for_report(request, report_id):
    main_category_id = int(request.POST["main_category"])
    secondary_category_id = int(request.POST["secondary_category"])
    report = get_object_or_404(Report, id=report_id)
    report.category = ReportMainCategoryClass.objects.get(id=main_category_id)
    report.secondary_category = ReportCategory.objects.get(id=secondary_category_id)
    report.save()
    return HttpResponse(json.dumps({"returntype": "ok"}), mimetype="application/json")


def send_pdf(request, report_id):
    user = get_current_user()
    recipients = request.POST.get('to')
    comments = request.POST.get('comments')
    privacy = request.POST.get('privacy')
    report = get_object_or_404(Report, id=report_id)
    #generate the pdf
    pdffile = generate_pdf("reports/pdf.html", {
        'report': report,
        'files': report.files(),
        'comments': report.comments(),
        'activity_list': report.activities.all(),
        'privacy': privacy
    }, context_instance=RequestContext(request))

    template = MailNotificationTemplate.objects.get(name="mail-pdf")

    subject, html, text = transform_notification_template(template, report, user, comment=comments)
    recepients = re.compile("[\\s,;]+").split(recipients)

    for recepient in recepients:

        msg = EmailMultiAlternatives(subject, text, settings.DEFAULT_FROM_EMAIL, (recepient,))

        if html:
            msg.attach_alternative(html, "text/html")

        #reset the seek to 0 to be able to read multiple times the same file
        pdffile.seek(0)
        msg.attach(pdffile.name, pdffile.read(), 'application/pdf')

        msg.send()

    return HttpResponse(_("PDF sent as email"), mimetype="application/text")
