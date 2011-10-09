import httplib
import json
from django.http import HttpResponse
from mainapp.models import DictToPoint, Report
from django.contrib.gis.measure import D
from fixmystreet.mainapp.templatetags.tags import report_to_array



def search(request): 
#    conn = httplib.HTTPConnection('gislb.irisnetlab.be')
    conn = httplib.HTTPConnection('192.168.13.42')

    conn.request("POST", "/WSGeoloc/Rest/Localize/getstreet", request.raw_post_data.decode('utf-8').encode('iso-8859-15'))
    response = conn.getresponse()
    data = response.read()
    conn.close()
    #f = open('/tmp/fms.txt', 'w')
    #for i, header in enumerate(response.getheaders()):
        #f.write(':'.join(header) + '\n')
    #f.write('\n')
    #f.write(data)
    #f.close()
    try:
        return HttpResponse(data.decode('iso-8859-15'))
    except UnicodeError:
        return HttpResponse(data)


def locate(request): 
#    conn = httplib.HTTPConnection('gislb.irisnetlab.be')
    conn = httplib.HTTPConnection('192.168.13.42')

    conn.request("POST", "/WSGeoloc/Rest/Localize/getaddressfromcoord", request.raw_post_data)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    try:
        return HttpResponse(data.decode('iso-8859-15'))
    except UnicodeError:
        return HttpResponse(data)

# http://geoserver.gis.irisnet.be/wms?LAYERS=urbisFR&TRANSPARENT=true&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&STYLES=&EXCEPTIONS=application%2Fvnd.ogc.se_inimage&FORMAT=image%2Fpng&SRS=EPSG%3A31370&BBOX=133736.38890635,160293.01359269,167103.47196451,182838.33998333&WIDTH=222&HEIGHT=150
# http://geoserver.gis.irisnet.be/geoserver/wms?LAYERS=urbisFR&TRANSPARENT=true&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&STYLES=&EXCEPTIONS=application%2Fvnd.ogc.se_inimage&FORMAT=image%2Fpng&SRS=EPSG%3A31370&BBOX=133736.38890635,160293.01359269,167103.47196451,182838.33998333&WIDTH=222&HEIGHT=150
# http://geoserver.gis.irisnet.be/geoserver/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=urbis:MU_VIEW_FR&maxFeatures=50&outputFormat=json
def wards(request): 
    conn = httplib.HTTPConnection('geoserver.gis.irisnet.be')
    conn.request("GET", "/geoserver/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=urbis:MU_VIEW_FR&maxFeatures=50&outputFormat=json")
    #conn.request("GET", "geoserver/ows",{
        #"service":"WFS",
        #"version":"1.0.0",
        #"request":"GetFeature",
        #"typeName":"urbis:MU_VIEW_FR",
        #"maxFeatures:":"50",
        #"outputFormat":"json"
    #})
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return HttpResponse(data)

def reports(request): 
    d2p = DictToPoint( request.REQUEST )
    pnt = d2p.pnt()
    reports = Report.objects.filter(is_confirmed = True,is_fixed = False,point__distance_lte=(pnt,D(km=2))).distance(pnt).order_by('-created_at')
    
    result = []
    for i,report in enumerate(reports):

        result.append(report_to_array(report))
        #{
            #'id':report.id,
            #'title':report.title,
            #'point':{
                #'x':report.point.x,
                #'y':report.point.y
            #},
            #'is_fixed':report.is_fixed,
            ##'photo':report.photo,
            #'distance':report.distance.km
        #});
    return HttpResponse(json.dumps({
        'status':'success',
        'results':result
    }))
