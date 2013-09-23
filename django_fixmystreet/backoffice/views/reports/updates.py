from datetime import datetime
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.db import transaction
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from django_fixmystreet.fixmystreet.models import Report, FMSUser, OrganisationEntity, ReportComment, ReportFile, ReportAttachment
from django_fixmystreet.fixmystreet.forms import MarkAsDoneForm
from django_fixmystreet.backoffice.forms import RefuseForm

from datetime import datetime, timedelta

import logging
logger = logging.getLogger(__name__)

# TODO move to backoffice/views/reports/main.py

@transaction.commit_on_success
def accept( request, report_id, redirect=True):
    report = get_object_or_404(Report, id=report_id)
    #Test if the report is created...
    if report.status == Report.CREATED:
        #Update the status and persist to the database
        report.status = Report.MANAGER_ASSIGNED
        report.accepted_at = datetime.now()
        report.save()

    #Redirect to the report show page
    if redirect:
        if "pro" in request.path:
            return HttpResponseRedirect(report.get_absolute_url_pro())
        else:
            return HttpResponseRedirect(report.get_absolute_url())

def refuse( request, report_id ):
    report = get_object_or_404(Report, id=report_id)

    #Test if the report is created...
    if report.status == Report.CREATED:
        #Update the status
        report.status = Report.REFUSED
        form = RefuseForm(request)
        #Save the refusal motivation in the database
        report.refusal_motivation = form.data.POST.get('refusal_motivation')
        report.save()

    #Redirect to the report show page
    if "pro" in request.path:
        return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
        return HttpResponseRedirect(report.get_absolute_url())

def fixed( request, report_id ):
    report = get_object_or_404(Report, id=report_id)
    if request.REQUEST.has_key('is_fixed'):
        form = MarkAsDoneForm(request.POST, instance=report)
        # Save the mark as done motivation in the database
        form.save() # Redirect to the report show page

    if "pro" in request.path:
        return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
        return HttpResponseRedirect(report.get_absolute_url())


def close( request, report_id ):
    report = get_object_or_404(Report, id=report_id)
    #Update the status and set the close date
    report.status = Report.PROCESSED
    report.close_date = datetime.now()
    report.save()
    #Redirect to the report show page
    if "pro" in request.path:
        return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
        return HttpResponseRedirect(report.get_absolute_url())

def planned( request, report_id ):
    report = get_object_or_404(Report, id=report_id)

    #Update the status and set the planned
    date_planned = request.GET.get("date_planned", False)
    if (date_planned):
        date_planned = datetime.strptime(date_planned, "%d-%m-%Y")

        report.planned = True
        report.date_planned = date_planned
        report.save()

    #Redirect to the report show page
    if "pro" in request.path:
        return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
        return HttpResponseRedirect(report.get_absolute_url())

def switchPrivacy(request,report_id):
    report = get_object_or_404(Report, id=report_id)
    privacy = request.REQUEST.get("privacy")
    report.private = ('true' == privacy)
    report.save()
    if "pro" in request.path:
            return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
            return HttpResponseRedirect(report.get_absolute_url())

def changeManager(request,report_id):
    report = Report.objects.get(pk=report_id)
    report.status = Report.MANAGER_ASSIGNED
    old_resp_man = report.responsible_manager
    report.previous_managers.add(old_resp_man)
    manId = request.REQUEST.get("manId")
    if manId.split("_")[0] == "manager":
        newRespMan = FMSUser.objects.get(pk=int(manId.split("_")[1]))
        report.responsible_manager = newRespMan
        report.save()
    if manId.split("_")[0] == "entity":
        orgId = int(manId.split("_")[1])
        report.responsible_entity = OrganisationEntity.objects.get(id=orgId)
        managers = FMSUser.objects.filter(organisation_id = orgId).filter(manager=True)
        for manager in managers:
            if manager.categories.all().filter(id = report.category.id):
                report.responsible_manager = manager
                report.save()
                break

    if "pro" in request.path:
            return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
            return HttpResponseRedirect(report.get_absolute_url())

def changeContractor(request,report_id):
    report = get_object_or_404(Report, id=report_id)
    contractorId = request.REQUEST.get("contractorId")

    if contractorId == 'None':
        report.contractor = None
        #Restore status to IN_PROGRESS
        report.status = Report.IN_PROGRESS
    else:
        organisation = OrganisationEntity.objects.get(pk=int(contractorId))
        report.contractor = organisation
        if organisation.subcontractor:
            report.status = Report.CONTRACTOR_ASSIGNED
        else:
            report.status = Report.APPLICANT_RESPONSIBLE

    report.save()
    if "pro" in request.path:
            return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
            return HttpResponseRedirect(report.get_absolute_url())


def publish(request, report_id):
    # Accept first
    accept(request, report_id, redirect=False)

    # Publish
    report = get_object_or_404(Report, id=report_id)
    report.status = Report.MANAGER_ASSIGNED
    report.private = False
    report.save()

    comments = ReportComment.objects.filter(report_id=report_id)
    for comment in comments:
        comment.security_level = ReportAttachment.PUBLIC
        comment.save()

    files = ReportFile.objects.filter(report_id=report_id)
    for f in files:
        f.security_level = ReportAttachment.PUBLIC
        f.save()

    if "pro" in request.path:
            return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
            return HttpResponseRedirect(report.get_absolute_url())

def validateAll(request,report_id):
    '''Set all annexes to public'''
    report = get_object_or_404(Report, id=report_id)

    comments = ReportComment.objects.filter(report_id=report_id)
    files = ReportFile.objects.filter(report_id=report_id)

    for comment in comments:
       comment.security_level = ReportAttachment.PUBLIC
       comment.save()

    for f in files:
        f.security_level = ReportAttachment.PUBLIC
        f.save()

    if "pro" in request.path:
            return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
            return HttpResponseRedirect(report.get_absolute_url())

def updateAttachment(request,report_id):
    report = get_object_or_404(Report,id=report_id)
    security_level = request.REQUEST.get('updateType')
    a = ReportAttachment.objects.get(pk=request.REQUEST.get('attachmentId'))
    a.security_level = int(security_level)
    a.save()

    return HttpResponseRedirect(report.get_absolute_url_pro())

def deleteAttachment(request, report_id):
    """delete a attachment (pro only)"""
    report = get_object_or_404(Report,id=report_id)
    a = ReportAttachment.objects.get(pk=request.REQUEST.get('attachmentId'))
    a.logical_deleted = True
    a.save()

    return HttpResponseRedirect(report.get_absolute_url_pro())

def updatePriority(request, report_id):
    report=get_object_or_404(Report, id=report_id)
    report.gravity = request.GET["gravity"]
    report.probability = request.GET["probability"]
    report.save()

    if "pro" in request.path:
            return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
            return HttpResponseRedirect(report.get_absolute_url())

def merge(request,report_id):
    #Get the reports that need to be merged
    report = get_object_or_404(Report, id=report_id)
    report_2 = get_object_or_404(Report,id=request.GET["mergeId"])

    #Determine which report needs to be kept
    if report.accepted_at:
        if report_2.accepted_at:
            if report.accepted_at < report_2.accepted_at:
                final_report = report
                report_to_delete = report_2
            else:
                final_report = report_2
                report_to_delete = report
        else:
            final_report = report
            report_to_delete = report_2
    else:
        if report_2.accepted_at:
            final_report = report_2
            report_to_delete = report
        else:
            if report.created < report_2.created:
                final_report = report
                report_to_delete = report_2
            else:
                final_report = report_2
                report_to_delete = report

    #Move attachments to new report
    for attachment in report_to_delete.attachments.all():
        attachment.report_id = final_report.id
        attachment.save()

    #If one of the reports is public, the new report should be public
    if not report_to_delete.private:
        final_report.private = False
        final_report.save()

    #Delete the 2nd report
    report_to_delete.delete();

    #Send message of confirmation
    messages.add_message(request, messages.SUCCESS, _("Your report has been merged."))
    if "pro" in request.path:
            return HttpResponseRedirect(final_report.get_absolute_url_pro()+"?page=1")
    else:
            return HttpResponseRedirect(final_report.get_absolute_url())

