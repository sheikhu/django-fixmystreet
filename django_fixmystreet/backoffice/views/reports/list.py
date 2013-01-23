from django.shortcuts import render_to_response
from django_fixmystreet.fixmystreet.models import dictToPoint, Report, ZipCode
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils.translation import get_language
import math

@login_required(login_url='/pro/accounts/login/')
def list(request, status):
    if request.GET.get("page"):
        page_number = int(request.GET.get("page"))
    else:
        page_number=1

    default_position = {
        'x': '148954.431',
        'y': '170458.371'
    }

    if 'x' in request.REQUEST and 'y' in request.REQUEST:
        pnt = dictToPoint(request.REQUEST)
    else:
        pnt = dictToPoint(default_position)

    connectedUser = request.fmsuser
    user_organisation = connectedUser.organisation

    #if the user is an executeur de travaux then user the dependent organisation id
    if (connectedUser.contractor == True):
        user_organisation = user_organisation.dependency

    #reports = Report.objects.distance(pnt).order_by('distance')[0:10]

    if status == 'created':
    	reports = Report.objects.filter(responsible_entity=user_organisation).filter(status=Report.CREATED)
    elif status == 'in_progress':
    	reports = Report.objects.filter(responsible_entity=user_organisation).filter(status__in=Report.REPORT_STATUS_IN_PROGRESS)
    elif status == 'in_progress_and_assigned':
    	reports = Report.objects.filter(responsible_entity=user_organisation).filter(status__in=Report.REPORT_STATUS_ASSIGNED)
    elif status == 'closed':
    	reports = Report.objects.filter(responsible_entity=user_organisation).filter(status__in=Report.REPORT_STATUS_CLOSED)
    else: # all
        reports = Report.objects.filter(responsible_entity=user_organisation).all()

    #if the user is an executeur de travaux then display only report where He is responsible
    if (connectedUser.contractor == True):
        reports = reports.filter(contractor = connectedUser.organisation)

    #reports = reports.distance(pnt).order_by('distance')
    #reports = reports.distance(pnt).order_by('address', 'address_number')
    reports = reports.distance(pnt).order_by('-created')
    pages_list = range(1,int(math.ceil(len(reports)/settings.MAX_ITEMS_PAGE))+1+int(len(reports)%settings.MAX_ITEMS_PAGE != 0))
    zipcodes = ZipCode.objects.filter(hide=False).select_related('commune').order_by('name_' + get_language())

    return render_to_response("pro/reports/list.html",
            {
                "pnt":pnt,
                "zipcodes": zipcodes,
                "reports":reports[int((page_number-1)*settings.MAX_ITEMS_PAGE):int(page_number*settings.MAX_ITEMS_PAGE)],
                "status":status,
                "pages_list":pages_list,
            },
            context_instance=RequestContext(request))


@login_required(login_url='/pro/accounts/login/')
def listfilter(request):
    #default set on page 1 
    page_number=1
    #Get location
    pnt = dictToPoint(request.REQUEST)
    #Get street
    value_street = request.GET.get("street")
    value_street_number = request.GET.get("streetNumber")
    #Get the rayon
    value_rayon = request.GET.get("rayon")
    #Get the current user
    connectedUser = request.fmsuser
    user_organisation = connectedUser.organisation
    #if the user is an executeur de travaux then user the dependent organisation id
    if (connectedUser.contractor == True):
        user_organisation = user_organisation.dependency

    #reports = Report.objects.distance(pnt).order_by('distance')[0:10]
    reports = Report.objects.filter(responsible_entity=user_organisation)
   
    #If a rayon is given the apply it on the research
    if (not value_rayon == None):
        if (not value_street_number == ""):
            #update point to use with rayon
            unique_report_result = reports.filter(address__contains=value_street).filter(address_number=value_street_number)
            if unique_report_result.__len__() == 0:
                #no result then use the given point
                the_unique_report_with_number_point = pnt 
            else:
                the_unique_report_with_number_point = unique_report_result[0].point
            reports = reports.distance(the_unique_report_with_number_point).filter(point__distance_lte=(the_unique_report_with_number_point,int(value_rayon)))
        else:
            #Use the default position as the street number has not been given
            reports = reports.distance(pnt).filter(point__distance_lte=(pnt,int(value_rayon))) 
    #if the numer is given then filter on it
    else:
        reports = reports.filter(address__contains=value_street)
        if (not value_street_number == ""):
            reports = reports.filter(address_number=value_street_number)

    #if the user is an executeur de travaux then display only report where He is responsible
    if (connectedUser.contractor == True):
        reports = reports.filter(contractor = connectedUser.organisation)

    #Order by address number as an int
    reports = reports.extra(
    select={'address_number_as_int': 'CAST(address_number AS INTEGER)'}
).distance(pnt).order_by('address', 'address_number_as_int')
   
 
    pages_list = range(1,int(math.ceil(len(reports)/settings.MAX_ITEMS_PAGE))+1+int(len(reports)%settings.MAX_ITEMS_PAGE != 0))
    zipcodes = ZipCode.objects.filter(hide=False).select_related('commune').order_by('name_' + get_language())

    return render_to_response("pro/reports/list.html",
            {
                "pnt":pnt,
                "zipcodes": zipcodes,
                "reports":reports[int((page_number-1)*settings.MAX_ITEMS_PAGE):int(page_number*settings.MAX_ITEMS_PAGE)],
                "status": "all",
                "pages_list":pages_list,
            },
            context_instance=RequestContext(request))
