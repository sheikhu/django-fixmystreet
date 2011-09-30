import httplib
import json
from django.http import HttpResponse


def locate(request): 
    conn = httplib.HTTPConnection('gislb.irisnetlab.be')
    conn.request("POST", "/WSGeoloc/Rest/Localize/getxycoord", request.raw_post_data)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return HttpResponse(data)

# http://geoserver.gis.irisnet.be/wms?LAYERS=urbisFR&TRANSPARENT=true&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&STYLES=&EXCEPTIONS=application%2Fvnd.ogc.se_inimage&FORMAT=image%2Fpng&SRS=EPSG%3A31370&BBOX=133736.38890635,160293.01359269,167103.47196451,182838.33998333&WIDTH=222&HEIGHT=150
# http://geoserver.gis.irisnet.be/geoserver/wms?LAYERS=urbisFR&TRANSPARENT=true&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&STYLES=&EXCEPTIONS=application%2Fvnd.ogc.se_inimage&FORMAT=image%2Fpng&SRS=EPSG%3A31370&BBOX=133736.38890635,160293.01359269,167103.47196451,182838.33998333&WIDTH=222&HEIGHT=150
# http://geoserver.gis.irisnet.be/geoserver/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=urbis:MU_VIEW_FR&maxFeatures=50&outputFormat=json
def wards(request): 
    conn = httplib.HTTPConnection('geoserver.gis.irisnet.be')
    conn.request("GET", "geoserver/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=urbis:MU_VIEW_FR&maxFeatures=50&outputFormat=json")
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return HttpResponse(data)
