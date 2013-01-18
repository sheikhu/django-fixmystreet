import json
from django.conf import settings

from django import template
from django.core.urlresolvers import resolve
from django_fixmystreet.fixmystreet.models import FMSUser


register = template.Library()

MENU_DEFS = [
    ('submit', ['home','report_new','report_new_pro','home_pro']),
    ('view', ['report_index', 'report_show', 'report_update', 'subscribe', 'unsubscribe', 'flag_success', 'flag_report','report_show_pro','report_list_pro']),
    ('users',['usersOverview']),
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
def addthis_scripts():
    return '<script src="http://s7.addthis.com/js/250/addthis_widget.js?pub=' + settings.ADD_THIS_KEY + '"></script>'

@register.filter
def dict_to_json(values):
    return json.dumps(values)

@register.filter
def get_element_from_list(list, index):
    """
    Defined to get an element from a list
    """
    return list[index]

@register.filter
def hasAtLeastAManager(userId):
    connectedUser  = FMSUser.objects.get(user_ptr_id=userId)
    connectedOrganisation = connectedUser.organisation
    organisationId = connectedOrganisation.id
    #if the user is an executeur de travaux then user the dependent organisation id
    if (connectedUser.contractor == True):
        organisationId = connectedOrganisation.dependency.id

    return FMSUser.objects.filter(organisation_id=organisationId).filter(manager=True).exists()

@register.filter
def classname(obj):
    return obj.__class__.__name__

@register.simple_tag
def input_placeholder(field):
    field.field.widget.attrs["placeholder"] = field.label
    return field
