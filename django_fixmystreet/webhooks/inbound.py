# -*- coding: utf-8 -*-
"""
Inbound webhook handlers.
"""
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from ..fixmystreet.models import Report, ReportAttachment, ReportComment, ReportEventLog


class NotLinkedWithThirdPartyError(Exception): pass  # pylint: disable=C0321
class ThirdPartyNotAuthorizedError(Exception): pass  # pylint: disable=C0321
#class NotWaitingForThirdPartyError(Exception): pass  # pylint: disable=C0321
class BadRequestError(Exception): pass  # pylint: disable=C0321


class AbstractBaseInWebhook(object):
    """
    Abstract inbound webhook handler. Every inbound webhook must derive from this class.

    Class naming convention: ``<Resource><Hook><Action>InWebhook``.
    """

    def __init__(self, meta, data, user=None):
        self._meta = meta
        self._data = data
        self._user = user

    def run(self):
        raise NotImplementedError()


class AbstractReportInWebhook(AbstractBaseInWebhook):
    """Abstract inbound webhook handler for resource ``report``."""

    def __init__(self, meta, data, user=None):
        super(AbstractReportInWebhook, self).__init__(meta, data, user=user)
        self._report = Report.objects.get(pk=meta["id"])
        self._third_party = self._report.get_webhook_third_party()  # @TODO: Create `report.get_webhook_third_party()`.

    def _add_comment(self, context):
        context["action_msg"] = context["action_msg"].format(third_party=self._third_party.name)
        formatted_comment = render_to_string("webhooks/report_comment.txt", context)
        comment = ReportComment(report=self._report, text=formatted_comment, type=ReportAttachment.DOCUMENTATION)  # pylint: disable=E1123
        comment.save()


class AbstractReportAssignmentInWebhook(AbstractReportInWebhook):

    def _validate(self):
        if self._third_party is None:
            raise NotLinkedWithThirdPartyError("Report not linked with a third-party.")

        if self._third_party != self._user:  # @TODO: Create `Auth.User` for third-parties and link it to `_third_party.fmsproxy`.
            raise ThirdPartyNotAuthorizedError("No authorization for this report.")

        # @TODO: Really needed? If assigned
        #if not self._report.waiting_for_organisation_entity():
        #    raise NotWaitingForThirdPartyError("Report not waiting for a third-party.")

        if not self._meta.get("id"):
            raise BadRequestError(u"'meta.id' is required.")


class ReportAssignmentAcceptInWebhook(AbstractReportAssignmentInWebhook):

    def run(self):
        super(ReportAssignmentAcceptInWebhook, self).run()
        self._validate()

        context = {
            "action_msg": _("Incident was accepted by {third_party}."),
            "reference_id": self._data["reference_id"],
            "comment": self._data["comment"],
        }
        self._add_comment(context)

    def _validate(self):
        super(ReportAssignmentAcceptInWebhook, self)._validate()

        if not self._data.get("reference_id"):
            raise BadRequestError(u"'data.referenceId' is required.")


class ReportAssignmentRejectInWebhook(AbstractReportAssignmentInWebhook):

    def run(self):
        super(ReportAssignmentRejectInWebhook, self).run()
        self._validate()

        context = {
            "action_msg": _("Incident was rejected by {third_party}."),
            "comment": self._data["comment"],
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

    def _validate(self):
        super(ReportAssignmentRejectInWebhook, self)._validate()

        if not self._data.get("comment"):
            raise BadRequestError(u"'data.comment' is required.")


class ReportAssignmentCloseInWebhook(AbstractReportAssignmentInWebhook):

    def run(self):
        super(ReportAssignmentCloseInWebhook, self).run()
        self._validate()

        context = {
            "action_msg": _("Incident was closed by {third_party}."),
            "reference_id": self._data["reference_id"],
            "comment": self._data["comment"],
        }
        self._add_comment(context)

        if not self._report.contractor:
            self._report.close()

    def _validate(self):
        super(ReportAssignmentCloseInWebhook, self)._validate()

        if not self._data.get("reference_id"):
            raise BadRequestError(u"'data.referenceId' is required.")
