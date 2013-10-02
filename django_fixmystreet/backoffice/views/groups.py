import logging
import json

from smtplib import SMTPException

from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth import login, logout
from django.utils import translation
from django.contrib.auth.forms import PasswordChangeForm
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError

from django_fixmystreet.backoffice.forms import FmsUserForm, GroupForm
from django_fixmystreet.fixmystreet.models import OrganisationEntity, UserOrganisationMembership, FMSUser

logger = logging.getLogger(__name__)


def list_groups(request):
    current_user = request.fmsuser

    groups = OrganisationEntity.objects.filter(type__in=['D', 'S'])
    if current_user.organisation:
        groups = groups.filter(dependency=current_user.organisation)
    elif not request.user.is_superuser:
        raise PermissionDenied()

    return render_to_response("pro/auth/groups_overview.html", {
        'groups': groups,
        'can_create' : request.fmsuser.leader
    }, context_instance=RequestContext(request))

def create_group(request,):
    isManager = request.fmsuser.manager
    #a boolean value to tell the ui if the user can edit the given form content
    if request.method == "POST":
        group_form = GroupForm(request.POST)

        if group_form.is_valid():
            group = group_form.save(commit=False)
            group.dependency = request.fmsuser.organisation
            group.save()

            messages.add_message(request, messages.SUCCESS, _("Group has been created successfully"))
            return HttpResponseRedirect(reverse('list_groups'))

    else:
        group_form = GroupForm()

    return render_to_response("pro/auth/group_create.html",
            {
                "group_form": group_form,
                "isManager":  isManager,
            },
            context_instance=RequestContext(request))

def edit_group(request, group_id):
    isManager = request.fmsuser.manager
    #a boolean value to tell the ui if the user can edit the given form content

    instance = OrganisationEntity.objects.get(id=group_id)
    if request.method == "POST":
        group_form = GroupForm(request.POST, instance=instance)

        if group_form.is_valid():
            group = group_form.save()

            messages.add_message(request, messages.SUCCESS, _("Group has been updated successfully"))
            return HttpResponseRedirect(reverse('list_groups'))

    else:
        group_form = GroupForm(edit=True, instance=instance)

    return render_to_response("pro/auth/group_create.html",
            {
                "group_id"   : instance.id,
                "group_form" : group_form,
                "memberships"  : UserOrganisationMembership.objects.filter(organisation=instance),
            },
            context_instance=RequestContext(request))

def add_membership(request, group_id, user_id):
    can_add = request.fmsuser.leader

    if can_add:
        response_data = {}
        organisation  = OrganisationEntity.objects.get(id=group_id)
        user          = FMSUser.objects.get(id=user_id)

        user_organisation_membership = UserOrganisationMembership(user=user, organisation=organisation)

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
    can_remove = request.fmsuser.leader

    if not can_remove:
        return HttpResponse('Permission Denied');

    isManager = request.fmsuser.manager

    user_organisation_membership = UserOrganisationMembership.objects.get(id=membership_id)
    user_organisation_membership.delete()

    return HttpResponse('OK');
