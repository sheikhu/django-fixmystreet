# pylint: disable=E1120
import logging

from django.db import models
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string



logger = logging.getLogger(__name__)


class NotWaitingForThirdPartyError(Exception): pass  # pylint: disable=C0321
class NotAssignedToThirdPartyError(Exception): pass  # pylint: disable=C0321
class NotAuthorizedToThirdPartyError(Exception): pass  # pylint: disable=C0321


class FMSProxy(models.Model):

    name = models.CharField(max_length=20)
    slug = models.SlugField(max_length=20)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(FMSProxy, self).save(*args, **kwargs)


class AssignmentHandler(object):

    def __init__(self, report_id, user):
        from ..fixmystreet.models import Report

        self._report = Report.objects.get(pk=report_id)
        self._user = user

        if not self._report.waiting_for_organisation_entity():
            raise NotWaitingForThirdPartyError("Report not waiting for a third-party.")

        self._org_entity = self._report.get_organisation_entity_with_fms_proxy()
        if self._org_entity is None:
            raise NotAssignedToThirdPartyError("Report not assigned to a third-party.")
        #if user != self._org_entity.fmsproxy:  # @TODO: Create `Auth.User` for third-parties and link it to `_org_entity.fmsproxy`.
        #    raise NotAuthorizedToThirdPartyError("No authorization for this report.")

    def accept(self, data):
        context = {
            "action_msg": _("Incident was accepted by {contractor}."),
            "reference_id": data["reference_id"],
            "comment": data["comment"],
        }
        self._add_comment(context)

    def reject(self, data):
        from ..fixmystreet.models import Report, ReportEventLog

        context = {
            "action_msg": _("Incident was rejected by {contractor}."),
            "comment": data["comment"],
        }
        self._add_comment(context)

        if not self._report.contractor:
            self._report.responsible_department = ReportEventLog.objects.filter(
                report=self._report,
                organisation=self._report.responsible_entity,
                event_type=ReportEventLog.MANAGER_ASSIGNED
            ).latest("event_at").related_old
            self._report.responsible_entity = self._report.responsible_department.dependency
            self._report.status = Report.MANAGER_ASSIGNED
            self._report.save()

    def close(self, data):
        context = {
            "action_msg": _("Incident was closed by {contractor}."),
            "reference_id": data["reference_id"],
            "comment": data["comment"],
        }
        self._add_comment(context)

        if not self._report.contractor:
            self._report.close()

    def _add_comment(self, context):
        from ..fixmystreet.models import ReportAttachment

        context["action_msg"] = context["action_msg"].format(contractor=self._org_entity.name)
        formatted_comment = render_to_string("fmsproxy_comment.txt", context)
        comment = ReportComment(report=self._report, text=formatted_comment, type=ReportAttachment.DOCUMENTATION)  # pylint: disable=E1123
        comment.save()


def get_assign_payload(report):
    creator = report.get_creator()
    payload = {
        "application": report.get_organisation_entity_with_fms_proxy().fmsproxy.slug,
        "report":{
            "id": report.id,
            "created_at": report.created.isoformat(),
            "modified_at": report.modified.isoformat(),
            "category": report.display_category(),
            "pdf_url": report.get_pdf_url_pro_with_auth_token(),
            "address": report.address,
            "address_number": report.address_number,
            "postal_code": report.postalcode,
            "municipality": report.get_address_commune_name(),
            "creator": {
                "type": "pro" if report.is_pro() else "citizen",
                "first_name": creator.first_name,
                "last_name": creator.last_name,
                "phone": creator.telephone,
                "email": creator.email,
            },
            "comments": [],
        },
    }

    comments = report.comments()
    for comment in comments:
        payload["report"]["comments"].append({
            "created_at": comment.created.isoformat(),
            "name": comment.created_by.get_display_name() if comment.created_by else "",
            "text": comment.reportcomment.text,
        })

    return payload
