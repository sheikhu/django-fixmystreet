import httplib
from urllib2 import HTTPError

from django.contrib.gis.measure import D
from django.http import HttpResponse
from django.utils import simplejson


from fixmystreet.models import Report, ReportCategory, Ward, dictToPoint
from fixmystreet.utils import ssl_required, oauthtoken_to_user, JsonHttpResponse
from fixmystreet.templatetags.tags import report_to_array
import settings


# deprecated ! service.gis.irisnet.be support jsonp
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

    return JsonHttpResponse({
        'status':'success',
        'results':result
    })

@ssl_required
def create_report(request):
    user = None
    if request.user.is_authenticated():
        user = request.user
    try:
        user = user or oauthtoken_to_user(request.REQUEST.get('backend'),request.REQUEST.get('access_token'),request)
    except HTTPError, e:
        return JsonHttpResponse('error', {
            'code': e.code,
            'errortype':'trasaction_error',
            'message': simplejson.loads(e.read())['error']['message']
        })
    
    if not user:
        return JsonHttpResponse('error', {
            'errortype':'connection_error',
            'message': 'Enable to authenticate user'
        })

    data = request.POST
    report = Report()
    report.author = user

    try:
        # Category
        report.category = ReportCategory.objects.get(id=data['category'])
        # Address
        report.point = dictToPoint(data)
        report.postalcode = data['postalcode']
        report.ward = Ward.objects.get(zipcode__code=data['postalcode'])
        report.address = data['address']
        # Photo
        report.photo = request.FILES.get('photo')
        # Description
        report.desc = data.get('description')
    except Exception, e:
        return JsonHttpResponse('error', {
            'errortype':'validation_error',
            'message': 'Some data are invalid {}'.format(e)
        })

    report.save()
    
    
    return JsonHttpResponse({
        'user': user.get_full_name(),
        'report': {
            'id':report.id
        }
    })
