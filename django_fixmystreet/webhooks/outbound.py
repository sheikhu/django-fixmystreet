# -*- coding: utf-8 -*-
"""
Outbound webhook handlers.
"""
import json
import requests
from datetime import datetime

from .models import WebhookConfig
from ..api.utils.conversion import dict_walk_python_to_json, dict_walk_json_to_python
from django_fixmystreet.fixmystreet.models import OrganisationEntity
from django_fixmystreet.fixmystreet.utils import sign_message


class AbstractBaseOutWebhook(object):
    """
    Abstract outbound webhook handler. Every outbound webhook must derive from this class.

    Class naming convention: ``<Resource><Hook><Action>OutWebhook``.
    """

    resource_slug = None
    hook_slug = None
    action_slug = None
    third_party = None  # ``OrganisationEntity`` object.

    def fire(self):
        """Sends the request to all registered endpoints."""
        payload = self.get_payload()

        # Send the request to all registered endpoints.
        for endpoint in self.get_endpoints():
            try:
                response = self._send_request(endpoint, payload)
                if response.status_code != 200:
                    message = u"Invalid status code ({}).".format(response.status_code)
                    response_data = response.json()
                    if response_data.get("message"):
                        message = u"{} Message: {}".format(message, response_data["message"])
                    self._handle_error(message, response, endpoint)
            except ValueError, e:
                message = "Exception: {}".format(e)
                self._handle_error(message, response, endpoint)

    def get_endpoints(self):
        """Retrieves the configuration for each endpoints registered for the current ``resource.hook.action``."""
        filters = {
            "resource": self.resource_slug,
            "hook": self.hook_slug,
            "action": self.action_slug,
        }

        if self.third_party:
            filters["third_party"] = self.third_party

        # Always return a list.
        return WebhookConfig.objects.filter(**filters).values("url", "data")

    def get_payload(self):
        """
        Generates the payload that must be sent.

        It must return a dictionary using Python conventions (snake_case, Python objects...).
        The `serialize` method takes care of formating the data before sending them.
        """
        return {
            "meta": {
                "now": datetime.now(),
                "resource": self.resource_slug,
                "hook": self.hook_slug,
                "action": self.action_slug,
            },
            "data": {},
        }

    def _handle_error(self, message, response, endpoint):
        """Handles errors during requests to endpoints."""
        pass  # @TODO: What to do? Just logging? Send a mail? Endpoint admin email in config? Try again later?

    def _send_request(self, endpoint, payload, headers=None):
        """
        Sends the HTTP request to the given endpoint.

        Args:
            - endpoint: A dictionary {url, data}.
            - payload: The payload (as Python object).
        """
        headers = headers or {}
        headers["Content-Type"] = "application/json; charset=utf-8"
        serialized_payload = self.serialize(payload)

        if endpoint.get("data"):
            # If the endpoint config contains a signature key, sign the request with it.
            if endpoint["data"].get("signature_key"):
                headers["X-FMS-Signature"] = sign_message(endpoint["data"]["signature_key"], serialized_payload)

        return requests.post(endpoint["url"], data=serialized_payload, headers=headers)

    @staticmethod
    def serialize(data):
        """Converts a Python object into a JSON string."""
        return json.dumps(dict_walk_python_to_json(data))

    @staticmethod
    def unserialize(string):
        """Converts a JSON string into a Python object."""
        return dict_walk_json_to_python(json.loads(string))


class AbstractReportOutWebhook(AbstractBaseOutWebhook):
    """Abstract outbound webhook handler for resource ``report``."""

    resource_slug = "report"

    def __init__(self, report, third_party=None):
        if third_party is not None and not isinstance(third_party, OrganisationEntity):
            raise TypeError("'third_party' must be a 'auth.User' object.")

        super(AbstractReportOutWebhook, self).__init__()
        self.report = report
        self.third_party = third_party

    def get_payload(self):
        payload = super(AbstractReportOutWebhook, self).get_payload()
        creator = self.report.get_creator()

        payload["meta"]["now"] = self.report.modified
        payload["data"]["report"] = {
            "id": self.report.id,
            "created_at": self.report.created,
            "modified_at": self.report.modified,
            "category": self.report.display_category(),
            "pdf_url": self.report.get_pdf_url_pro_with_auth_token(),
            "address": {
                "street": self.report.address,
                "number": self.report.address_number,
                "postal_code": self.report.postalcode,
                "municipality": self.report.get_address_commune_name(),
            },
            "creator": {
                "type": "pro" if self.report.is_pro() else "citizen",
                "first_name": creator.first_name,
                "last_name": creator.last_name,
                "phone": creator.telephone,
                "email": creator.email,
            },
            "comments": [],
        },

        comments = self.report.comments()
        for comment in comments:
            payload["data"]["report"]["comments"].append({
                "created_at": comment.created,
                "name": comment.created_by.get_display_name() if comment.created_by else "",
                "text": comment.self.reportcomment.text,
            })

        return payload


class AbstractReportAssignmentOutWebhook(AbstractReportOutWebhook):
    hook_slug = "assignment"

    def __init__(self, report, third_party):
        super(AbstractReportAssignmentOutWebhook, self).__init__(report, third_party=third_party)


class ReportAssignmentRequestOutWebhook(AbstractReportAssignmentOutWebhook):
    action_slug = "request"


class AbstractReportTransferOutWebhook(AbstractReportOutWebhook):
    hook_slug = "transfer"

    def __init__(self, report, third_party):
        super(AbstractReportTransferOutWebhook, self).__init__(report, third_party=third_party)


class ReportTransferRequestOutWebhook(AbstractReportTransferOutWebhook):
    action_slug = "request"
