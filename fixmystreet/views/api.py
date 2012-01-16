import httplib
import json
from django.http import HttpResponse
from fixmystreet.models import dictToPoint, Report
from django.contrib.gis.measure import D
from fixmystreet.templatetags.tags import report_to_array
import settings



def search(request): 
    conn = httplib.HTTPConnection(settings.LOCAL_API)
    #conn.request("POST", "/WSGeoloc/Rest/Localize/getstreet", request.raw_post_data.decode('utf-8').encode('iso-8859-15'))
    conn.request("POST", "/urbis/Rest/Localize/getstreet", request.raw_post_data.decode('utf-8'))
    response = conn.getresponse()
    data = response.read()

    conn.close()
    #try:
        #return HttpResponse(data.decode('iso-8859-15'))
    #except UnicodeError:
    return HttpResponse(data,mimetype="text/json")


def locate(request): 
    conn = httplib.HTTPConnection(settings.LOCAL_API)

    #conn.request("POST", "/WSGeoloc/Rest/Localize/getaddressfromcoord", request.raw_post_data)
    conn.request("POST", "/urbis/Rest/Localize/getaddressfromcoord", request.raw_post_data)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    #try:
        #return HttpResponse(data.decode('iso-8859-15'))
    #except UnicodeError:
    return HttpResponse(data,mimetype="text/json")


def reports(request):
    pnt = dictToPoint(request.REQUEST)
    reports = Report.objects.filter(is_fixed = False).distance(pnt).order_by('distance')[:20]
    
    result = []
    for i,report in enumerate(reports):
        result.append(report_to_array(report))

    return HttpResponse(json.dumps({
        'status':'success',
        'results':result
    }),mimetype="text/json")
