import logging
import json

from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.db import IntegrityError
from django.core.exceptions import PermissionDenied
from django.forms.models import inlineformset_factory

from apps.backoffice.forms import GroupForm, GroupMailConfigForm
from apps.fixmystreet.models import OrganisationEntity, UserOrganisationMembership, FMSUser, GroupMailConfig

logger = logging.getLogger("fixmystreet")


def list_groups(request):
    current_user = request.fmsuser

    group_types = [t[0] for t in OrganisationEntity.ENTITY_TYPE_GROUP]
    groups = OrganisationEntity.objects.filter(type__in=group_types)

    if current_user.organisation:
        groups = groups.filter(dependency=request.fmsuser.organisation)
    elif not request.user.is_superuser:
        raise PermissionDenied()

    return render_to_response("pro/auth/groups_list.html", {
        'groups': groups,
        'can_create': current_user.leader
    }, context_instance=RequestContext(request))


def create_group(request,):
    can_edit = request.fmsuser.leader

    if request.method == "POST" and can_edit:
        group_form = GroupForm(request.POST)

        if group_form.is_valid():
            group = group_form.save(commit=False)
            group.dependency = request.fmsuser.organisation
            group.save()
            config = GroupMailConfig(group=group)
            config.save()

            messages.add_message(request, messages.SUCCESS, _("Group has been created successfully"))
            return HttpResponseRedirect(reverse('list_groups'))

    else:
        group_form = GroupForm()


    return render_to_response("pro/auth/group_create.html", {
        "group_form": group_form,
        "can_edit":  can_edit,
    }, context_instance=RequestContext(request))


def edit_group(request, group_id):
    can_edit = request.fmsuser.leader
    instance = OrganisationEntity.objects.get(id=group_id)

    # Init formset object for mail config
    GroupMailFormSet = inlineformset_factory(OrganisationEntity, GroupMailConfig, form=GroupMailConfigForm, can_delete=False)

    if request.method == "POST" and can_edit:
        group_form                = GroupForm(request.POST, instance=instance)
        group_mail_config_formset = GroupMailFormSet(request.POST, instance=instance)

        if group_form.is_valid() and group_mail_config_formset.is_valid():
            group_form.save()
            group_mail_config_formset.save()

            messages.add_message(request, messages.SUCCESS, _("Group has been updated successfully"))
            return HttpResponseRedirect(reverse('list_groups'))

    else:
        group_form                = GroupForm(instance=instance)
        group_mail_config_formset = GroupMailFormSet(instance=instance)

    return render_to_response("pro/auth/group_create.html", {
        "group": instance,
        "group_form": group_form,
        "group_mail_config_formset": group_mail_config_formset,
        "memberships": UserOrganisationMembership.objects.filter(organisation=instance),
        "can_edit": can_edit
    }, context_instance=RequestContext(request))


def delete_group(request, group_id):
    can_edit = request.fmsuser.leader

    instance = OrganisationEntity.objects.get(id=group_id)
    if (instance.dispatch_categories.count() or
            instance.reports_in_department.count() or
            instance.assigned_reports.count()):
        messages.add_message(request, messages.ERROR, _("Group has some reports or categories associated, remove them first and then try again"))
        return HttpResponseRedirect(reverse('edit_group', args=(instance.id,)))

    if request.method == "GET" and can_edit:
        # Delete group and memberships (in pre_delete)
        instance.delete()

        messages.add_message(request, messages.SUCCESS, _("Group has been deleted successfully"))

    return HttpResponseRedirect(reverse('list_groups'))


def add_membership(request, group_id, user_id):
    can_edit = request.fmsuser.leader
    response_data = {}
    if can_edit:
        organisation = OrganisationEntity.objects.get(id=group_id)
        user = FMSUser.objects.get(id=user_id)

        contact = not organisation.memberships.exists()
        user_organisation_membership = organisation.memberships.create(user=user, contact_user=contact)
        # user_organisation_membership = UserOrganisationMembership(user=user, organisation=organisation)

        try:
            user_organisation_membership.save()
            response_data['status'] = 'OK'
        except IntegrityError:
            response_data['status'] = 'IntegrityError'

        response_data['membership_id'] = user_organisation_membership.id
    else:
        response_data['status'] = 'Permission Denied'

    return HttpResponse(json.dumps(response_data), content_type="application/json")


def remove_membership(request, membership_id):
    can_edit = request.fmsuser.leader

    if not can_edit:
        return HttpResponse('Permission Denied')

    user_organisation_membership = UserOrganisationMembership.objects.get(id=membership_id)

    if user_organisation_membership.contact_user:
        return HttpResponse('Can not remove the contact user')

    user_organisation_membership.delete()

    return HttpResponse('OK')


def contact_membership(request, membership_id):
    can_edit = request.fmsuser.leader

    if not can_edit:
        return HttpResponse('Permission Denied')

    user_organisation_membership = UserOrganisationMembership.objects.get(id=membership_id)
    user_organisation_membership.organisation.memberships.all().update(contact_user=False)
    user_organisation_membership.contact_user = True
    user_organisation_membership.save()

    return HttpResponse('OK')
