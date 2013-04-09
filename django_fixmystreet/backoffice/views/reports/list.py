from django.shortcuts import render_to_response
from django_fixmystreet.fixmystreet.models import dictToPoint, Report, ZipCode
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils.translation import get_language
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

@login_required(login_url='/pro/accounts/login/')
def list(request, status):
    ownership = request.GET.get("ownership", "entity")

    #Get street
    value_street = request.GET.get("street", "")
    value_street_number = request.GET.get("streetNumber", "")
    #Get the rayon
    value_rayon = request.GET.get("rayon", "")

    default_position = {
        'x': '148954.431',
        'y': '170458.371'
    }

    if 'x' in request.REQUEST and 'y' in request.REQUEST:
        pnt = dictToPoint(request.REQUEST)
    else:
        pnt = dictToPoint(default_position)

    connectedUser = request.fmsuser

    reports = Report.objects.all()
    #if the user is an contractor then user the dependent organisation id
    if (connectedUser.contractor == True or connectedUser.applicant == True):
        #if the user is an contractor then display only report where He is responsible
        reports = reports.filter(contractor__in = connectedUser.work_for.all())
    else:
        #If the manager is connected then filter on manager
        if ownership == "responsible":
            reports = reports.responsible(connectedUser)
        elif ownership == "subscribed":
            reports = reports.subscribed(connectedUser)
        elif connectedUser.organisation: # ownership == entity
            reports = reports.entity_responsible(connectedUser.organisation)


    #reports = Report.objects.distance(pnt).order_by('distance')[0:10]

    if status == 'created':
        reports = reports.pending()
    elif status == 'in_progress':
        reports = reports.in_progress()
    elif status == 'in_progress_and_assigned':
        reports = reports.in_progress().assigned()
    elif status == 'closed':
        reports = reports.closed()
    # else: # all

    # Address & rayon
    #If a rayon is given the apply it on the research
    if (value_rayon):
        if (not value_street_number == ""):
            #update point to use with rayon
            if request.LANGUAGE_CODE == 'nl':
                unique_report_result = reports.filter(address_nl__contains=value_street).filter(address_number=value_street_number)
            else:
                unique_report_result = reports.filter(address_fr__contains=value_street).filter(address_number=value_street_number)

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
        if request.LANGUAGE_CODE == 'nl':
            reports = reports.filter(address_nl__contains=value_street)
        else:
            reports = reports.filter(address_fr__contains=value_street)

        if (not value_street_number == ""):
            reports = reports.filter(address_number=value_street_number)

    #reports = reports.distance(pnt).order_by('distance')
    #reports = reports.distance(pnt).order_by('address', 'address_number')
    reports = reports.distance(pnt).order_by('-created')
    #pages_list = range(1,int(math.ceil(len(reports)/settings.MAX_ITEMS_PAGE))+1+int(len(reports)%settings.MAX_ITEMS_PAGE != 0))
    zipcodes = ZipCode.objects.filter(hide=False).select_related('commune').order_by('name_' + get_language())

    page_number = int(request.GET.get("page", 1))
    paginator = Paginator(reports, settings.MAX_ITEMS_PAGE)
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    return render_to_response("pro/reports/list.html",
            {
                "pnt":pnt,
                "zipcodes": zipcodes,
                "reports": page,
                "status": status,
                "ownership": ownership,
                "page_number": page_number,
                "status": status
            },
            context_instance=RequestContext(request))
