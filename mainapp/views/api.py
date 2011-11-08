import httplib
import json
from django.http import HttpResponse
from mainapp.models import DictToPoint, Report
from django.contrib.gis.measure import D
from mainapp.templatetags.tags import report_to_array
import settings



def search(request): 
    conn = httplib.HTTPConnection(settings.LOCAL_API)
    conn.request("POST", "/WSGeoloc/Rest/Localize/getstreet", request.raw_post_data.decode('utf-8').encode('iso-8859-15'))
    response = conn.getresponse()
    data = response.read()

    #import pdb;pdb.set_trace()
    conn.close()
    try:
        return HttpResponse(data.decode('iso-8859-15'))
    except UnicodeError:
        return HttpResponse(data)


def locate(request): 
    conn = httplib.HTTPConnection(settings.LOCAL_API)

    conn.request("POST", "/WSGeoloc/Rest/Localize/getaddressfromcoord", request.raw_post_data)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    try:
        return HttpResponse(data.decode('iso-8859-15'))
    except UnicodeError:
        return HttpResponse(data)

def wards(request): 
    conn = httplib.HTTPConnection(settings.GEOSERVER)
    
    conn.request("GET", "/geoserver/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=urbis:MU_VIEW_FR&maxFeatures=50&outputFormat=json")
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return HttpResponse(data)

def reports(request): 
    d2p = DictToPoint(request.REQUEST)
    pnt = d2p.pnt()
    reports = Report.objects.filter(is_confirmed = True,is_fixed = False).distance(pnt).order_by('distance')[:20]
    
    result = []
    for i,report in enumerate(reports):
        result.append(report_to_array(report))

    return HttpResponse(json.dumps({
        'status':'success',
        'results':result
    }))
