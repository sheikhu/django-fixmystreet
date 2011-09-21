import httplib
import json
from django.http import HttpResponse

def locate(request): 
    conn = httplib.HTTPConnection('gislb.irisnetlab.be')
    #resp.language = getDictArray(
    conn.request("GET", "/WSGeoloc/Rest/Localize/getxycoord", request.raw_post_data)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return HttpResponse(data)
