from datetime import datetime
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.db import transaction
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response
from django.template import RequestContext

from django_fixmystreet.fixmystreet.models import Report, OrganisationEntity, ReportComment, ReportFile, ReportAttachment
from django_fixmystreet.fixmystreet.forms import MarkAsDoneForm
from django_fixmystreet.backoffice.forms import RefuseForm

import logging
logger = logging.getLogger(__name__)


# TODO move to backoffice/views/reports/main.py
@transaction.commit_on_success
def accept(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    #Test if the report is created...
    if report.status == Report.CREATED:
        #Update the status and persist to the database
        report.status = Report.MANAGER_ASSIGNED
        report.accepted_at = datetime.now()
        #When validating a report created by a citizen set all attachments to public per default.
        if (report.citizen):
            validateAll(request, report.id)
        report.save()

    if "pro" in request.path:
        return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
        return HttpResponseRedirect(report.get_absolute_url())


def refuse(request, report_id):
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


def fixed(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    if 'is_fixed' in request.REQUEST:
        form = MarkAsDoneForm(request.POST, instance=report)
        # Save the mark as done motivation in the database
        form.save()  # Redirect to the report show page

    if "pro" in request.path:
        return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
        return HttpResponseRedirect(report.get_absolute_url())


def close(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    #Update the status and set the close date
    report.status = Report.PROCESSED
    report.close_date = datetime.now()
    if not report.fixed_at:
        report.fixed_at = report.close_date
    report.save()

    #Redirect to the report show page
    if "pro" in request.path:
        return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
        return HttpResponseRedirect(report.get_absolute_url())


def planned(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    #Update the status and set the planned
    date_planned = request.GET.get("date_planned", False)
    if (date_planned):
        date_planned = datetime.strptime(date_planned, "%m/%Y")

        report.planned = True
        report.date_planned = date_planned
        report.save()

    #Redirect to the report show page
    if "pro" in request.path:
        return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
        return HttpResponseRedirect(report.get_absolute_url())


def pending(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    report.pending = True
    report.save()

    #Redirect to the report show page
    if "pro" in request.path:
        return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
        return HttpResponseRedirect(report.get_absolute_url())


def notpending(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    report.pending = False
    report.save()

    #Redirect to the report show page
    if "pro" in request.path:
        return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
        return HttpResponseRedirect(report.get_absolute_url())


def switchPrivacy(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    privacy = request.REQUEST.get("privacy")
    if privacy != 'true':
        if report.secondary_category.public:
            report.private = ('true' == privacy)
        else:
            messages.add_message(request, messages.ERROR, _("Cannot turn incident public. The category of this incident may not be shown to the citizens."))
    else:
        report.private = ('true' == privacy)

    report.save()

    if "pro" in request.path:
            return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
            return HttpResponseRedirect(report.get_absolute_url())


def changeManager(request, report_id):
    report = Report.objects.get(pk=report_id)
    report.status = Report.MANAGER_ASSIGNED

    # old_resp_man = report.responsible_manager
    # report.previous_managers.add(old_resp_man)
    manId = request.REQUEST.get("manId")

    if manId.split("_")[0] == "department":
        newRespMan = OrganisationEntity.objects.get(pk=int(manId.split("_")[1]))
        report.responsible_department = newRespMan
    elif manId.split("_")[0] == "entity":
        orgId = int(manId.split("_")[1])
        report.responsible_entity = OrganisationEntity.objects.get(id=orgId)
        report.responsible_department = None
    else:
        raise Exception('missing department or entity paramettre')

    report.save()

    if "pro" in request.path:
            return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
            return HttpResponseRedirect(report.get_absolute_url())


def changeContractor(request, report_id):
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
    accept(request, report_id)

    # Publish
    report = get_object_or_404(Report, id=report_id)
    report.status = Report.MANAGER_ASSIGNED
    report.private = False
    report.save()

    comments = ReportComment.objects.filter(report_id=report_id)
    for comment in comments:
        comment.security_level = ReportAttachment.PUBLIC
        comment.save(publish_report=True)

    files = ReportFile.objects.filter(report_id=report_id)
    for f in files:
        f.security_level = ReportAttachment.PUBLIC
        f.save(publish_report=True)

    if "pro" in request.path:
        return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
        return HttpResponseRedirect(report.get_absolute_url())


def validateAll(request, report_id):
    '''Set all annexes to public'''
    report = get_object_or_404(Report, id=report_id)

    attachments = report.attachments.all()
    attachments.update(security_level=ReportAttachment.PUBLIC)
    # for comment in comments:
    #     comment.security_level = ReportAttachment.PUBLIC
    #     comment.save()

    # for f in files:
    #     f.security_level = ReportAttachment.PUBLIC
    #     f.save()

    if "pro" in request.path:
            return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
            return HttpResponseRedirect(report.get_absolute_url())


def updateAttachment(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    security_level = request.REQUEST.get('updateType')
    a = report.attachments.get(pk=request.REQUEST.get('attachmentId'))
    a.security_level = int(security_level)
    a.save()

    return render_to_response("reports/_visibility_control.html", {
        "attachment": a
    }, context_instance=RequestContext(request))


def deleteAttachment(request, report_id):
    """delete a attachment (pro only)"""
    report = get_object_or_404(Report, id=report_id)
    a = ReportAttachment.objects.get(pk=request.REQUEST.get('attachmentId'))
    a.logical_deleted = True
    a.save()

    return HttpResponseRedirect(report.get_absolute_url_pro())


def do_merge(request, report_id):
    #Get the reports that need to be merged
    report = get_object_or_404(Report, id=report_id)
    report_2 = get_object_or_404(Report, id=request.POST["mergeId"])

    # Constraints for categories match and visibility match when merging
    # #Check that category + subcategory of two reports are equal:
    # if report.category != report_2.category or report.secondary_category != report_2.secondary_category:
    #     messages.add_message(request, messages.ERROR, _("Cannot merge reports that have different categories."))
    #     return HttpResponseRedirect(report.get_absolute_url_pro()+"?page=1")

    # #Check that visibility of two reports are equal:
    # if report.private != report_2.private:
    #     messages.add_message(request, messages.ERROR, _("Cannot merge reports that have different visibility."))
    #     return HttpResponseRedirect(report.get_absolute_url_pro()+"?page=1")

    #Determine which report needs to be kept [TO BE REVIEWED SPRINT 2]
    #NEW ALGO: 2014/01/12
    if report.created < report_2.created:
        final_report = report
        report_to_delete = report_2
    else:
        final_report = report_2
        report_to_delete = report
    #Now the oldest report must remain
    #if report.accepted_at:
    #    if report_2.accepted_at:
    #        if report.accepted_at < report_2.accepted_at:
    #            final_report = report
    #            report_to_delete = report_2
    #        else:
    #            final_report = report_2
    #            report_to_delete = report
    #    else:
    #        final_report = report
    #        report_to_delete = report_2
    #else:
    #    if report_2.accepted_at:
    #        final_report = report_2
    #        report_to_delete = report
    #    else:
    #        if report.created < report_2.created:
    #            final_report = report
    #            report_to_delete = report_2
    #        else:
    #            final_report = report_2
    #            report_to_delete = report

    #Move attachments to new report
    for attachment in report_to_delete.attachments.all():
        attachment.report_id = final_report.id
        attachment.save()

    #If one of the reports is public, the new report should be public
    if not report_to_delete.private:
        final_report.private = False
        final_report.save()
    #Send mail to report_to_delete subscribers, resp man and creator if
    #Delete the 2nd report
    report_to_delete.merged_with = final_report
    report_to_delete.save()
    # report_to_delete.delete();

    #Send message of confirmation
    # messages.add_message(request, messages.SUCCESS, _("Your report has been merged."))
    if "pro" in request.path:
            return HttpResponseRedirect(final_report.get_absolute_url_pro()+"?page=1")
    else:
            return HttpResponseRedirect(final_report.get_absolute_url())

