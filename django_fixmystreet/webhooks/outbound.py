# -*- coding: utf-8 -*-
"""
Outbound webhook handlers.
"""
import json
from datetime import datetime

import requests

from ..api.utils.conversion import dict_walk_python_to_json, dict_walk_json_to_python
from ..fixmystreet.models import OrganisationEntity
from ..fixmystreet.utils import sign_message
from .models import WebhookConfig

import logging
logger = logging.getLogger(__name__)


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
        endpoints = self.get_endpoints()
        if not endpoints:
            return

        payload = self.get_payload()

        # Send the request to all registered endpoints.
        for endpoint in endpoints:
            try:
                response = self._send_request(endpoint, payload)
            except Exception, e:
                message = u"Exception: Connection to endpoint {} failed. {}".format(endpoint["url"], e.message)
                e.args += (message,)  # message needs to be a tuple to be added to args
                raise
                #@FIXME: Raising the error breaks the loop so if there is more than one endpoint and the first one raise an error, the others will not be managed.

            if response.status_code != requests.codes.ok:
                message = u"Invalid status code ({}) on {}.".format(response.status_code, endpoint["url"])
                try:
                    response_data = response.json()
                    if response_data.get("detail"):
                        message += u"{} Message: {}".format(message, response_data["detail"])
                except ValueError, e:
                    pass
                raise Exception(message)


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
        # /!\ As ``data`` is a JSONField, we cannot use ``values()`` because it doesn't unserialize string to Python.
        items = WebhookConfig.objects.filter(**filters)
        endpoints = [{"url": i.url, "data": i.data} for i in items]
        return endpoints

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
            # If the endpoint config contains an authentication token, add an authorization header to the request.
            if endpoint["data"].get("auth_token"):
                headers["Authorization"] = "Token {}".format(endpoint["data"]["auth_token"])

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

    def __init__(self, report, third_party):
        if not isinstance(third_party, OrganisationEntity):
            raise TypeError("'third_party' must be an 'OrganisationEntity' object.")

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
            "category": {
                "fr": self.report.display_category("fr"),
                "nl": self.report.display_category("nl"),
            },
            "pdf_url": {
                "fr": self.report.get_pdf_url_pro_with_auth_token("fr"),
                "nl": self.report.get_pdf_url_pro_with_auth_token("nl")
            },
            "address": {
                "street": {
                    "fr": self.report.address_fr,
                    "nl": self.report.address_nl,
                },
                "number": self.report.address_number,
                "postal_code": self.report.postalcode,
                "municipality": {
                    "fr": self.report.get_address_commune_name("fr"),
                    "nl": self.report.get_address_commune_name("nl")
                },
            },
            "point": {
                "x": self.report.point.x,
                "y": self.report.point.y,
             },
            "creator": {
                "type": "pro" if self.report.is_pro() else "citizen",
                "first_name": creator.first_name,
                "last_name": creator.last_name,
                "phone": creator.telephone,
                "email": creator.email,
            },
            "comments": [],
        }

        for comment in self.report.comments():
            payload["data"]["report"]["comments"].append({
                "created_at": comment.created,
                "name": comment.created_by.get_display_name() if comment.created_by else "",
                "text": comment.reportcomment.text,
            })

        return payload


class AbstractReportAssignmentOutWebhook(AbstractReportOutWebhook):
    hook_slug = "assignment"


class ReportAssignmentRequestOutWebhook(AbstractReportAssignmentOutWebhook):
    action_slug = "request"


class AbstractReportTransferOutWebhook(AbstractReportOutWebhook):
    hook_slug = "transfer"


class ReportTransferRequestOutWebhook(AbstractReportTransferOutWebhook):
    action_slug = "request"
