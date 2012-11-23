import re
import json
from django.conf import settings

from django import template
from django.conf import settings
from django.core.urlresolvers import resolve
from django_fixmystreet.fixmystreet.models import FMSUser, Report, ReportSubscription, OrganisationEntity

register = template.Library()

MENU_DEFS = [ 
    ('submit', ['home','report_new']),
    ('view', ['report_index', 'report_show', 'report_update', 'subscribe', 'unsubscribe', 'flag_success', 'flag_report']),
    ('about',  ['about', 'terms_of_use']),
    ('contact', ['contact'])
]

@register.simple_tag(takes_context=True)
def get_active_menu(context):
    page = resolve(context['request'].path)
    for menu,defs in MENU_DEFS:
        if page.url_name in defs:
            context['menu'] = menu
            return ''
    return ''

@register.simple_tag
def map_scripts():
    return '''
    <script src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/jquery-ui.min.js"></script>
    <script src="{STATIC_URL}OpenLayers-2.11/OpenLayers.js"></script>
    <script src="{STATIC_URL}js/fixmystreetmap.js"></script>
    <script src="{STATIC_URL}js/proj4js/engine/proj4js-compressed.js"></script>
    <script src="{STATIC_URL}js/proj4js/defs/EPSG31370.js"></script>
    '''.format(STATIC_URL=settings.STATIC_URL)

@register.simple_tag
def addthis_scripts():
    return '<script src="http://s7.addthis.com/js/250/addthis_widget.js?pub=' + settings.ADD_THIS_KEY + '"></script>'

@register.simple_tag
def report_to_json(report):
    return json.dumps(report.to_object())

@register.filter
def getElementFromList(list,index):
    #Defined to get an element from a list
    return list[index]

@register.filter
def isLeader(userId):
    return FMSUser.objects.get(user_ptr_id=userId).leader

@register.filter
def getUserType(userId):
    result = ""
    user = FMSUser.objects.get(user_ptr_id=userId)
    if user.leader:
        return "leader"
    if user.manager:
        return "manager"
    if user.agent:
        return "agent"
    if user.impetrant:
        return "impetrant"
    if user.contractor:
        return "contractor"
@register.filter
def isManager(userId):
    return FMSUser.objects.get(user_ptr_id=userId).manager

@register.filter
def isAgent(userId):
    return FMSUser.objects.get(user_ptr_id=userId).agent

@register.filter
def numberOfCreatedReports(userId):
    userConnected = FMSUser.objects.get(user_ptr_id=userId)
    userConnectedOrganisation = userConnected.organisation
    reports = Report.objects.filter(responsible_entity=userConnectedOrganisation).filter(status=Report.CREATED)
    return reports.count()

@register.filter
def numberOfInProgressReports(userId):
    userConnected = FMSUser.objects.get(user_ptr_id=userId)
    userConnectedOrganisation = userConnected.organisation
    reports = Report.objects.filter(responsible_entity=userConnectedOrganisation).filter(status__in=Report.REPORT_STATUS_IN_PROGRESS)
    return reports.count()

@register.filter
def numberOfClosedReports(userId):
    userConnected = FMSUser.objects.get(user_ptr_id=userId)
    userConnectedOrganisation = userConnected.organisation
    reports = Report.objects.filter(responsible_entity=userConnectedOrganisation).filter(status__in=Report.REPORT_STATUS_CLOSED)
    return reports.count()

@register.filter
def numberOfReports(userId):
    userConnected = FMSUser.objects.get(user_ptr_id=userId)
    userConnectedOrganisation = userConnected.organisation
    reports = Report.objects.filter(responsible_entity=userConnectedOrganisation).all()
    #Activate something similar to this to filter per entity !!!
    #reports = Report.objects.filter(status_id=1).filter(responsible_manager__organisation=userConnectedOrganisation)
    return reports.count()

@register.filter
def numberOfUsers(userId):
    organisationId = FMSUser.objects.get(user_ptr_id=userId).organisation.id
    users = FMSUser.objects.filter(organisation_id = organisationId)
    return users.count()

@register.filter
def numberOfAgents(userId):
    organisationId = FMSUser.objects.get(user_ptr_id=userId).organisation.id
    agents = FMSUser.objects.filter(organisation_id = organisationId)
    agents = agents.filter(agent = True)
    return agents.count()

@register.filter
def numberOfContractors(userId):
    organisationId = FMSUser.objects.get(user_ptr_id=userId).organisation.id
    #Get organisations dependants from the current organisation id
    dependantOrganisations = OrganisationEntity.objects.filter(dependency_id = organisationId)
    allOrganisation = list(dependantOrganisations)
    allOrganisation.append(organisationId)
    contractors = FMSUser.objects.filter(organisation_id__in=allOrganisation)
    contractors = contractors.filter(contractor = True)
    return contractors.count()

@register.filter
def numberOfImpetrants(userId):
    organisationId = FMSUser.objects.get(user_ptr_id=userId).organisation.id
    impetrants = FMSUser.objects.filter(organisation_id = organisationId)
    impetrants = impetrants.filter(impetrant = True)
    return impetrants.count()

@register.filter
def numberOfSubscriptions(userId):
    subscriptions = ReportSubscription.objects.filter(subscriber_id=userId)
    return subscriptions.count()

@register.filter
def numberOfManagers(userId):
    organisationId = FMSUser.objects.get(user_ptr_id=userId).organisation.id
    managers = FMSUser.objects.filter(organisation_id = organisationId)
    managers = managers.filter(manager = True)
    return managers.count()

@register.filter
def hasAtLeastAManager(userId):
    organisationId = FMSUser.objects.get(user_ptr_id=userId).organisation.id
     
    return FMSUser.objects.filter(organisation_id=organisationId).filter(manager=True).exists()
