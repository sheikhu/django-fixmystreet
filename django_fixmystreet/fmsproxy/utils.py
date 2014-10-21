from django_fixmystreet.fixmystreet.utils import sign_message
from django_fixmystreet.settings import SECRET_KEY

# this is based on description "Validation d'une requete" found at confluence.cirb.lan/display/DJA/FMS-Proxy
def fms_proxy_signature_is_valid(request):
    payload = request.body

    expected_signature = sign_message(SECRET_KEY, payload)
    request_signature = request.META["HTTP_X_FMS_PROXY_SIGNATURE"]

    return request_signature == expected_signature
