# -*- coding: utf-8 -*-
# pylint: disable=C0321,E1120,E1123,W0223
"""
Inbound webhook handlers.
"""
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from apps.fixmystreet.models import FMSUser, Report, ReportAttachment, ReportComment, ReportEventLog
from apps.fixmystreet.utils import check_responsible_permission, check_contractor_permission


class NotLinkedWithThirdPartyError(Exception): pass
class ThirdPartyNotAuthorizedError(Exception): pass
class InvalidReportStatusError(Exception): pass
class BadRequestError(Exception): pass


class ReportAcceptInWebhookMixin(object):

    ACTION_MESSAGE = u""

    def run(self):
        self._validate()

        context = {
            "action_msg": self.ACTION_MESSAGE,
            "reference_id": self._data["reference_id"],
            "comment": self._data["comment"],
        }
        self._add_comment(context)

    def _validate(self):
        super(ReportAcceptInWebhookMixin, self)._validate()

        # Required fields.
        if not self._data.get("reference_id"):
            raise BadRequestError(u"'data.referenceId' is required.")


class ReportRejectInWebhookMixin(object):

    ACTION_MESSAGE = u""

    def run(self):
        self._validate()

        context = {
            "action_msg": self.ACTION_MESSAGE,
            "comment": self._data["comment"],
        }
        self._add_comment(context)

    def _validate(self):
        super(ReportRejectInWebhookMixin, self)._validate()

        # Required fields.
        if not self._data.get("comment"):
            raise BadRequestError(u"'data.comment' is required.")


class ReportCloseInWebhookMixin(object):

    ACTION_MESSAGE = u""

    def run(self):
        self._validate()

        context = {
            "action_msg": self.ACTION_MESSAGE,
            "reference_id": self._data["reference_id"],
            "comment": self._data["comment"],
        }
        self._add_comment(context)

    def _validate(self):
        super(ReportCloseInWebhookMixin, self)._validate()

        # Required fields.
        if not self._data.get("reference_id"):
            raise BadRequestError(u"'data.referenceId' is required.")


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
    """Abstract inbound webhook handler for ``report.*.*``."""

    def __init__(self, meta, data, user=None):
        super(AbstractReportInWebhook, self).__init__(meta, data, user=user)
        self._report = Report.objects.get(pk=meta["id"])
        self._third_party = None

    def _add_comment(self, context):
        context["action_msg"] = context["action_msg"].format(third_party=self._third_party.name)
        formatted_comment = render_to_string("webhooks/report_comment.txt", context)
        fms_user = FMSUser.objects.get(pk=self._user.id)
        comment = ReportComment(
            report=self._report, text=formatted_comment, type=ReportAttachment.DOCUMENTATION, created_by=fms_user
        )
        comment.save()

    def _user_has_permission(self):
        raise NotImplementedError()

    def _validate(self):
        if self._third_party is None:
            raise NotLinkedWithThirdPartyError(u"Report not linked with a third-party.")

        if not self._report.is_in_progress():
            raise InvalidReportStatusError(u"Report not in a valid state.")

        if not self._user_has_permission():
            raise ThirdPartyNotAuthorizedError(u"No authorization for this report.")

        # Required fields.
        if not self._meta.get("id"):
            raise BadRequestError(u"'meta.id' is required.")


class AbstractReportAssignmentInWebhook(AbstractReportInWebhook):
    """Abstract inbound webhook handler for ``report.assignment.*``."""

    def __init__(self, meta, data, user=None):
        super(AbstractReportAssignmentInWebhook, self).__init__(meta, data, user=user)
        self._third_party = self._report.contractor

    def _user_has_permission(self):
        return check_contractor_permission(self._user, self._report)


class ReportAssignmentAcceptInWebhook(ReportAcceptInWebhookMixin, AbstractReportAssignmentInWebhook):
    """Inbound webhook handler for ``report.assignment.accept``."""

    ACTION_MESSAGE = _(u"Report assignment was accepted by {third_party}.")


class ReportAssignmentRejectInWebhook(ReportRejectInWebhookMixin, AbstractReportAssignmentInWebhook):
    """Inbound webhook handler for ``report.assignment.reject``."""

    ACTION_MESSAGE = _(u"Report assignment was rejected by {third_party}.")


class ReportAssignmentCloseInWebhook(ReportCloseInWebhookMixin, AbstractReportAssignmentInWebhook):
    """Inbound webhook handler for ``report.assignment.close``."""

    ACTION_MESSAGE = _(u"Report assignment was closed by {third_party}.")


class AbstractReportTransferInWebhook(AbstractReportInWebhook):
    """Abstract inbound webhook handler for ``report.transfer.*``."""

    def __init__(self, meta, data, user=None):
        super(AbstractReportTransferInWebhook, self).__init__(meta, data, user=user)
        self._third_party = self._report.responsible_department

    def _user_has_permission(self):
        return check_responsible_permission(self._user, self._report)


class ReportTransferAcceptInWebhook(ReportAcceptInWebhookMixin, AbstractReportTransferInWebhook):
    """Inbound webhook handler for ``report.transfer.accept``."""

    ACTION_MESSAGE = _(u"Report transfer was accepted by {third_party}.")


class ReportTransferRejectInWebhook(ReportRejectInWebhookMixin, AbstractReportTransferInWebhook):
    """Inbound webhook handler for ``report.transfer.reject``."""

    ACTION_MESSAGE = _(u"Report transfer was rejected by {third_party}.")

    def run(self):
        super(ReportTransferRejectInWebhook, self).run()

        self._report.responsible_department = ReportEventLog.objects.filter(
            report=self._report,
            organisation=self._report.responsible_entity,
            event_type=ReportEventLog.MANAGER_ASSIGNED
        ).latest("event_at").related_old
        self._report.responsible_entity = self._report.responsible_department.dependency
        self._report.status = Report.MANAGER_ASSIGNED
        self._report.save()


class ReportTransferCloseInWebhook(ReportCloseInWebhookMixin, AbstractReportTransferInWebhook):
    """Inbound webhook handler for ``report.transfer.close``."""

    ACTION_MESSAGE = _(u"Report transfer was closed by {third_party}.")

    def run(self):
        super(ReportTransferCloseInWebhook, self).run()

        self._report.close()
