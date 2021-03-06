from apps.fixmystreet.utils import sign_message
from django.conf import settings

# this is based on description "Validation d'une requete" found at confluence.cirb.lan/display/DJA/FMS-Proxy
def fms_proxy_signature_is_valid(request):
    payload = request.body

    expected_signature = sign_message(settings.SECRET_KEY, payload)
    request_signature = request.META["HTTP_X_FMS_PROXY_SIGNATURE"]

    return request_signature == expected_signature
