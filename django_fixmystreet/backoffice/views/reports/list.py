from django.shortcuts import render_to_response
from django_fixmystreet.fixmystreet.models import dictToPoint, Report
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.conf import settings
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
    return render_to_response("pro/reports/list.html",
            {
                "pnt":pnt,
                "reports":reports[int((page_number-1)*settings.MAX_ITEMS_PAGE):int(page_number*settings.MAX_ITEMS_PAGE)],
                "status":status,
                "pages_list":pages_list,
            },
            context_instance=RequestContext(request))
