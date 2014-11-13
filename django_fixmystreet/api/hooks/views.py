# -*- coding: utf-8 -*-
# pylint: disable=C0103,W0613,W0622
from ..views import PrivateApiView
from ..utils import dict_walk_json_to_python, to_upper_camel_case
from ...webhooks import inbound as inbound_webhooks


class UnknownWebhookError(LookupError): pass  # pylint: disable=C0321


class HooksView(PrivateApiView):

    def post(self, request, format=None):
        request_data = dict_walk_json_to_python(request.DATA)  # @TODO: Do that earlier in DRF process (cf. parsers).
        meta = request_data["meta"]
        data = request_data["data"]

        # Build handler class name.
        class_name = "{}{}{}InWebhook".format(
            to_upper_camel_case(meta["resource"]),
            to_upper_camel_case(meta["hook"]),
            to_upper_camel_case(meta["action"])
        )
        try:  # ``AttributeError`` means there's no handler for that ``resource.hook.action``.
            cls = getattr(inbound_webhooks, class_name)
        except AttributeError:
            raise UnknownWebhookError(u"Unknown inbound wehook for '{resource}.{hook}.{action}'.".format(**meta))

        # Run the handler.
        handler = cls(meta, data, user=request.user)
        handler.run()
