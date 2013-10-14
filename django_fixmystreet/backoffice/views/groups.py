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

<<<<<<< HEAD
    #~ if current_user.organisation:
        #~ groups = groups.filter(dependency=current_user.organisation)
    #~ elif not request.user.is_superuser:
        #~ raise PermissionDenied()
=======
    if current_user.organisation:
        groups = groups.filter(dependency=current_user.organisation)
    elif not request.user.is_superuser:
        raise PermissionDenied()
>>>>>>> fc2f0799166888a383d1a361c0d3c27b89a429bd

    return render_to_response("pro/auth/groups_list.html", {
        'groups': groups,
        'can_create' : current_user.leader
    }, context_instance=RequestContext(request))

def create_group(request,):
    can_edit = request.fmsuser.leader

    if request.method == "POST" and can_edit:
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
                "can_edit":  can_edit,
            },
            context_instance=RequestContext(request))

def edit_group(request, group_id):
    can_edit = request.fmsuser.leader

    instance = OrganisationEntity.objects.get(id=group_id)
    if request.method == "POST" and can_edit:
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
                "can_edit" : can_edit
            },
            context_instance=RequestContext(request))

def delete_group(request, group_id):
    can_edit = request.fmsuser.leader

    instance = OrganisationEntity.objects.get(id=group_id)
    if request.method == "GET" and can_edit:
            # Delete group and memberships (in pre_delete)
            instance.delete()

            messages.add_message(request, messages.SUCCESS, _("Group has been deleted successfully"))

    return HttpResponseRedirect(reverse('list_groups'))

def add_membership(request, group_id, user_id):
    can_edit = request.fmsuser.leader
    response_data = {}
<<<<<<< HEAD
    if can_edit:        
=======
    if can_edit:
>>>>>>> fc2f0799166888a383d1a361c0d3c27b89a429bd
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
    can_edit = request.fmsuser.leader

    if not can_edit:
        return HttpResponse('Permission Denied');

    isManager = request.fmsuser.manager

    user_organisation_membership = UserOrganisationMembership.objects.get(id=membership_id)
    user_organisation_membership.delete()

    return HttpResponse('OK');
