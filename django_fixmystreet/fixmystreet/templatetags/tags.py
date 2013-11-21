import json
from django.conf import settings

from django import template
from django.core.urlresolvers import resolve
from django_fixmystreet.fixmystreet.models import FMSUser
from django_fixmystreet.fixmystreet import models


register = template.Library()

MENU_DEFS = {
    'submit':                    ['home', 'report_new', 'report_new_pro', 'home_pro',
                                  'report_prepare_pro', 'report_verify'
                                  ],
    'view':                      ['report_index', 'report_show', 'report_update', 'subscribe',
                                  'unsubscribe', 'flag_success', 'flag_report', 'report_show_pro',
                                  'report_list_pro', 'report_table_pro'
                                  ],
    'auth':                      ['list_users', 'edit_user', 'create_user', 'list_groups',
                                  'create_group', 'edit_group',
                                  'category_gestionnaire_configuration',
                                  'password_change'
                                  ],
    'users':                     ['list_users', 'edit_user', 'create_user'],
    'groups':                    ['list_groups', 'create_group', 'edit_group'],
    'users_manager_dispatching': ['category_gestionnaire_configuration'],
    'users_change_password':     ['password_change'],
    'about':                     ['about', 'terms_of_use'],
    'contact':                   ['contact']
}


@register.simple_tag(takes_context=True)
def is_active_menu(context, menu):
    page = resolve(context['request'].path)
    if page.url_name in MENU_DEFS[menu]:
        return 'active'
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


# TODO move it to model and fix it
@register.filter
def hasAtLeastAManager(userId):
    connectedUser = FMSUser.objects.get(id=userId)
    organisation = connectedUser.organisation
    if not organisation:
        return False
    #if the user is an executeur de travaux then user the dependent organisation id
    if connectedUser.contractor and organisation.dependency:
        organisation = organisation.dependency

    return organisation.team.filter(manager=True).exists()


@register.filter
def classname(obj):
    return obj.__class__.__name__


@register.simple_tag
def input_placeholder(field):
    field.field.widget.attrs["placeholder"] = field.label
    return field


@register.simple_tag
def input_class(field, css_class):

    if "class" in field.field.widget.attrs:
        field.field.widget.attrs["class"] += " "
        field.field.widget.attrs["class"] += css_class
    else:
        field.field.widget.attrs["class"] = css_class

    return field


@register.inclusion_tag('ga.html')
def ga_script():
    return {
        'code': settings.GA_CODE
    }


@register.filter
def model_field_choices(model_name, field):
    choices = []
    model = getattr(models, model_name)
    for value in model._meta.get_field_by_name(field)[0].choices:
        if isinstance(value[1], tuple):
            [choices.append(unicode(v[1])) for v in value[1]]
        else:
            unicode(choices.append(value[1]))

    return choices
