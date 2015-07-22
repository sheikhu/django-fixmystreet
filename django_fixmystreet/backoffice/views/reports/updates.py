from datetime import datetime
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.db import transaction
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import Http404

from django_fixmystreet.fixmystreet.models import Report, OrganisationEntity, ReportComment, ReportFile, ReportAttachment
from django_fixmystreet.fixmystreet.forms import ReportCommentForm
from django_fixmystreet.fixmystreet.utils import responsible_permission
from django_fixmystreet.backoffice.forms import TransferForm

import logging
logger = logging.getLogger(__name__)


@responsible_permission
def accept(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    # Test if the report is created...
    if report.status == Report.CREATED:
        # Update the status and persist to the database
        report.status = Report.MANAGER_ASSIGNED
        report.accepted_at = datetime.now()

        # When validating a report created by a citizen set all attachments to public per default.
        if (report.citizen):
            validateAll(request, report.id)
        report.save()

    return HttpResponseRedirect(report.get_absolute_url_pro())

@responsible_permission
def refuse(request, report_id):
    report       = get_object_or_404(Report, id=report_id)
    comment_form = ReportCommentForm(request.POST)

    # TOFIX: Validate form
    if comment_form.is_valid() and request.POST.get('text'):
        comment = comment_form.save(commit=False)

        # Save refusal motivation
        comment.report = report

        # If the report is public, make the refusal motivation public too
        if not report.private:
            comment.security_level = ReportComment.PUBLIC

        comment.type = ReportAttachment.REFUSED
        comment.save()

        #Update the status of report
        report.status = Report.REFUSED
        report.save()

    #Redirect to the report show page
    if "pro" in request.path:
        return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
        return HttpResponseRedirect(report.get_absolute_url())

# Every one should be capable to mark as done
# @responsible_permission
def fixed(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    comment_form = ReportCommentForm(request.POST)

    # TOFIX: Validate form
    if report.is_markable_as_solved() and comment_form.is_valid() and request.POST.get('text'):
        comment = comment_form.save(commit=False)

        # Save refusal motivation
        comment.report = report
        comment.type = ReportAttachment.MARK_AS_DONE
        comment.save()

        #Update the status of report
        report.status               = Report.SOLVED
        report.fixed_at             = datetime.now()
        report.save()

    return HttpResponseRedirect(report.get_absolute_url_pro())

@responsible_permission
def close(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    report.close()

    #Redirect to the report show page
    if "pro" in request.path:
        return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
        return HttpResponseRedirect(report.get_absolute_url())

@responsible_permission
def reopen(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    if report.is_closed() or report.is_refused():

        # If the report was rejected, no accepted_at date exists. Need to init it.
        if report.is_refused() and not report.accepted_at:
            report.accepted_at = datetime.now()

            # When validating a report created by a citizen set all attachments to public per default.
            if (report.citizen):
                validateAll(request, report.id)

        report.status = Report.MANAGER_ASSIGNED
        report.save()

    return HttpResponseRedirect(report.get_absolute_url_pro())

@responsible_permission
def planned(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    #Update the status and set the planned
    date_planned = request.GET.get("date_planned", False)
    if date_planned:
        report.date_planned = datetime.strptime(date_planned, "%m/%Y")
        report.save()

    # Redirect to the report show page
    return HttpResponseRedirect(report.get_absolute_url_pro())

@responsible_permission
def pending(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    report.pending = True
    report.save()

    #Redirect to the report show page
    if "pro" in request.path:
        return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
        return HttpResponseRedirect(report.get_absolute_url())

@responsible_permission
def notpending(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    report.pending = False
    report.save()

    #Redirect to the report show page
    if "pro" in request.path:
        return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
        return HttpResponseRedirect(report.get_absolute_url())

@responsible_permission
def switchPrivacy(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    privacy = request.REQUEST.get("privacy")

    if privacy == 'true':
        # Is private
        report.private = True
    else:
        # Is public
        if report.secondary_category.public:
            report.private = False
        else:
            messages.add_message(request, messages.ERROR, _("Cannot turn incident public. The category of this incident may not be shown to the citizens."))

    report.save()

    return HttpResponseRedirect(report.get_absolute_url_pro())

@responsible_permission
def switchThirdPartyResponsibility(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    third_party_responsibility = request.REQUEST.get("thirdPartyResponsibility")

    if third_party_responsibility == 'true':
        #source of incident is due to a third party
        report.third_party_responsibility = True
    else:
        #source of incident is not a third party
        report.third_party_responsibility = False

    report.save()

    if "pro" in request.path:
            return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
            return HttpResponseRedirect(report.get_absolute_url())

@responsible_permission
def changeManager(request, report_id):
    report = Report.objects.get(pk=report_id)

    transfer_form = TransferForm(request.POST)

    if transfer_form.is_valid():
        try:
            transfer_form.save(report, request.user)
        except Exception, e:
            messages.add_message(request, messages.ERROR, _("organisation entity TRANSFER : Generic error"))
            logger.exception(e)

    return HttpResponseRedirect(report.get_absolute_url_pro())

@responsible_permission
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

        if organisation.type == OrganisationEntity.SUBCONTRACTOR:
            report.status = Report.CONTRACTOR_ASSIGNED
        else:
            report.status = Report.APPLICANT_RESPONSIBLE

    try:
        report.save()
    except Exception, e:
        messages.add_message(request, messages.ERROR, _("organisation entity ASSIGN : Generic error"))
        logger.exception(e)


    if "pro" in request.path:
            return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
            return HttpResponseRedirect(report.get_absolute_url())

@responsible_permission
def updatePriority(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    report.gravity = int(request.GET["gravity"])
    report.probability = int(request.GET["probability"])
    report.save()

    if "pro" in request.path:
            return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
            return HttpResponseRedirect(report.get_absolute_url())

@responsible_permission
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

    return HttpResponseRedirect(report.get_absolute_url_pro())

@responsible_permission
def validateAll(request, report_id):
    '''Set all annexes to public'''
    switchPrivacy(request, report_id)

    report = get_object_or_404(Report, id=report_id)

    if not report.private:
        attachments = report.attachments.all()

        # Loop to trigger signals using .save()
        for attachment in attachments:
            attachment.security_level = ReportAttachment.PUBLIC
            attachment.is_new_report  = True
            attachment.save()

    return HttpResponseRedirect(report.get_absolute_url_pro())

@responsible_permission
def updateAttachment(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    security_level            = request.REQUEST.get('updateType')
    attachment                = report.attachments.get(pk=request.REQUEST.get('attachmentId'))
    attachment.security_level = int(security_level)
    attachment.save()

    # update modified_by
    report.save()

    return render_to_response("reports/_visibility_control.html", {
        "attachment": attachment
    }, context_instance=RequestContext(request))

@responsible_permission
def deleteAttachment(request, report_id):
    """delete a attachment (pro only)"""
    report = get_object_or_404(Report, id=report_id)
    a = ReportAttachment.objects.get(pk=request.REQUEST.get('attachmentId'))
    a.logical_deleted = True
    a.save()

    return HttpResponseRedirect(report.get_absolute_url_pro())

@responsible_permission
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
            return HttpResponseRedirect(final_report.get_absolute_url_pro())
    else:
            return HttpResponseRedirect(final_report.get_absolute_url())


def report_false_address(request, report_id):
    if request.method == "POST":
        report = get_object_or_404(Report, id=report_id)

        false_address = request.POST.get('false_address')

        if (false_address):
            false_address = false_address.strip()
            if (false_address == ''):
                false_address = None

        report.false_address = false_address
        report.save()

        return HttpResponseRedirect(report.get_absolute_url_pro())
    else:
        raise Http404
