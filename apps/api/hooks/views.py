# -*- coding: utf-8 -*-
# pylint: disable=C0103,W0613,W0622
from apps.webhooks.inbound import BadRequestError, ThirdPartyNotAuthorizedError, \
    NotLinkedWithThirdPartyError, InvalidReportStatusError
from ..views import PrivateApiView
from ..utils.conversion import to_upper_camel_case
from ...webhooks import inbound as inbound_webhooks

import logging
logger = logging.getLogger("fixmystreet")


class UnknownWebhookError(LookupError): pass  # pylint: disable=C0321


class HooksView(PrivateApiView):

    def post(self, request, format=None):
        try:
            meta = request.DATA["meta"]
            data = request.DATA["data"]
        except KeyError:
            return self._get_response_400(u"Payload must contain 'meta' and 'data'.")

        try:
            # Build handler class name.
            class_name = "{}{}{}InWebhook".format(
                to_upper_camel_case(meta["resource"]),
                to_upper_camel_case(meta["hook"]),
                to_upper_camel_case(meta["action"])
            )
        except KeyError:
            return self._get_response_400(u"'meta' must contain 'resource', 'hook' and 'action'.")

        try:  # ``AttributeError`` means there's no handler for that ``resource.hook.action``.
            handler_class = getattr(inbound_webhooks, class_name)
        except AttributeError:
            return self._get_response_400(u"Unknown inbound webhook for '{resource}.{hook}.{action}'.".format(**meta))

        # Run the handler.
        handler = handler_class(meta, data, user=request.user)
        try:
            handler.run()
        except BadRequestError, e:
            return self._get_response_400(e.message)
        except (ThirdPartyNotAuthorizedError, NotLinkedWithThirdPartyError, InvalidReportStatusError), e:
            logger.error(e.message)
            return self._get_response_403()
        except Exception, e:
            logger.exception(e)
            return self._get_response_500()

        return self._get_response_200()
