import logging
from smtplib import SMTPException

from django.db.models import Q
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth import login, logout
from django.utils import translation
from django.contrib.auth.forms import PasswordChangeForm
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from django_fixmystreet.backoffice.forms import FmsUserForm, AgentForm, ContractorForm, ContractorUserForm
from django_fixmystreet.fixmystreet.forms import LoginForm
from django_fixmystreet.fixmystreet.models import OrganisationEntity, FMSUser

logger = logging.getLogger(__name__)



def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.user
            login(request, user)
            messages.add_message(request, messages.SUCCESS, _("You are logged in successfully"))
            logger.info('login user {1} ({0})'.format(user.id, user.username))
            if 'next' in request.REQUEST and request.REQUEST['next'] and request.REQUEST['next'] != reverse('login'):
                return HttpResponseRedirect(request.REQUEST['next'])
            else:
                translation.activate(user.fmsuser.last_used_language)
                return HttpResponseRedirect(reverse('home_pro'))
    else:
        form = LoginForm()
    return render_to_response("pro/login.html", {
        "form": form
    }, context_instance=RequestContext(request))


def logout_view(request):
    logger.info('logout user {1} ({0})'.format(request.user.id, request.user.username))
    logout(request)
    return HttpResponseRedirect(reverse('home'))


def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.fmsuser, request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('')
    else:
        form = PasswordChangeForm(request.fmsuser)
    return render_to_response('pro/change_password.html', {'form': form}, context_instance=RequestContext(request))


def list_users(request, user_id=None, user_type='users'):
    params = dict()
    params['user_type'] = user_type
    currentOrganisation = request.fmsuser.organisation
    users = FMSUser.objects.filter(organisation=currentOrganisation)
    if user_id:
        user_to_edit = FMSUser.objects.get(id=user_id)
        params['can_edit'] = (((user_to_edit.manager or user_to_edit.agent) and request.fmsuser.leader) or ((user_to_edit.agent) and request.fmsuser.manager))

        if request.method == "POST" and params['can_edit']:
            user_form = FmsUserForm(request.POST, instance=user_to_edit)
            if user_form.is_valid():
                user_form.save()
                messages.add_message(request, messages.SUCCESS, _("User has been saved successfully"))
                return HttpResponseRedirect('')
        else:
            user_form = FmsUserForm(instance=user_to_edit)

        params['user_form'] = user_form


    if user_type == 'agents':
        users = users.filter(agent=True, manager=False)
    elif user_type == 'managers':
        users = users.filter(manager=True)
    else:
        users = users.filter(Q(agent=True) | Q(manager=True) | Q(leader=True))

    users = users.filter(logical_deleted = False)

    params['users'] = users

    return render_to_response("pro/users_overview.html", params, context_instance=RequestContext(request))


def create_user(request, user_type='users'):
    isManager = request.fmsuser.manager
    #a boolean value to tell the ui if the user can edit the given form content
    if request.method == "POST":
        user_form = AgentForm(request.POST)
        if user_form.is_valid():
            try:
                user = user_form.save(commit=False)
                user.organisation = request.fmsuser.organisation
                user.save()
                if not user_form.instance_retrived:
                    user_form.notify_user(user)
                if user:
                    messages.add_message(request, messages.SUCCESS, _("User has been created successfully"))
                    return HttpResponseRedirect('')
            except SMTPException as e:
                logger.error("email not sent successfully: {0}".format(e))
                messages.add_message(request, messages.ERROR, _("An error occurd during the email sending"))

    else:
        user_form = AgentForm(initial={'user_type': 'manager' if user_type=='managers' else 'agent'})

    return render_to_response("pro/user_create.html",
            {
                "user_form":user_form,
                "isManager":isManager
            },
            context_instance=RequestContext(request))


def delete_user(request, user_id, user_type='users'):
    # todo set active = false

    user_to_delete = FMSUser.objects.get(id=user_id, organisation=request.fmsuser.organisation)

    can_edit = (((user_to_delete.manager or user_to_delete.agent) and request.fmsuser.leader) or ((user_to_delete.agent) and request.fmsuser.manager))
    if not can_edit:
        messages.add_message(request, messages.ERROR, _("You can not delete this user"))
        return HttpResponseRedirect(reverse('list_users', kwargs={'user_type': user_type}))

    user_to_delete.logical_deleted = True
    user_to_delete.is_active = False
    user_to_delete.agent = False
    user_to_delete.manager = False
    user_to_delete.save()
    messages.add_message(request, messages.SUCCESS, _("User deleted successfully"))

    #FMSUser.objects.get(id=request.REQUEST.get('userId')).delete()
    return HttpResponseRedirect(reverse('list_users', kwargs={'user_type': user_type}))


def list_contractors(request, contractor_id=None):
    currentOrganisation = request.fmsuser.organisation
    params = dict()
    contractors = OrganisationEntity.objects.filter(dependency=currentOrganisation, subcontractor=True)

    if contractor_id:
        contractor_to_edit = OrganisationEntity.objects.get(id=contractor_id, subcontractor=True)
        user_to_edit = contractor_to_edit.workers.all()[0]
        params['can_edit'] = request.fmsuser.leader or request.fmsuser.manager

        if request.method == "POST" and params['can_edit']:
            contractor_form = ContractorForm(request.POST, instance=contractor_to_edit)
            user_form = FmsUserForm(request.POST, instance=user_to_edit)
            if contractor_form.is_valid() and user_form.is_valid():
                contractor = contractor_form.save(request.fmsuser.organisation)
                user = user_form.save()
                user.work_for.add(contractor)

                messages.add_message(request, messages.SUCCESS, _("Contractor has been saved successfully"))
                return HttpResponseRedirect('')
        else:
            contractor_form = ContractorForm(instance=contractor_to_edit)
            user_form = FmsUserForm(instance=user_to_edit)

        params['contractor_form'] = contractor_form
        params['user_form'] = user_form

    params["contractors"] = contractors
    return render_to_response("pro/contractors_overview.html", params, context_instance=RequestContext(request))


def create_contractor(request):
    isManager = request.fmsuser.manager
    # a boolean value to tell the ui if the user can edit the given form content
    if request.method == "POST":
        contractor_form = ContractorForm(request.POST, prefix="entity")
        user_form = ContractorUserForm(request.POST, prefix="user")
        if contractor_form.is_valid() and user_form.is_valid():

            try:
                contractor = contractor_form.save(request.fmsuser.organisation)
                user = user_form.save()
                user.work_for.add(contractor)

                if user_form.instance_retrived:
                    messages.add_message(request, messages.SUCCESS, _("Contractor has been linked with existing user {0}").format(user.get_full_name()))
                    return HttpResponseRedirect('')
                elif user:
                    messages.add_message(request, messages.SUCCESS, _("User has been created successfully"))
                    return HttpResponseRedirect('')
            except SMTPException as e:
                logger.error("email not sent successfully: {0}".format(e))
                messages.add_message(request, messages.ERROR, _("An error occurd during the email sending"))

    else:
        contractor_form = ContractorForm(prefix="entity")
        user_form = ContractorUserForm(prefix="user")

    return render_to_response("pro/contractor_create.html",
            {
                "contractor_form": contractor_form,
                "user_form": user_form,
                "isManager": isManager
            },
            context_instance=RequestContext(request))

def delete_contractor(request, contractor_id):
    # todo set active = false
    contractor = OrganisationEntity.objects.get(id=contractor_id, dependency=request.fmsuser.organisation, subcontractor=True)

    can_edit = request.fmsuser.leader or request.fmsuser.manager
    if not can_edit:
        messages.add_message(request, messages.ERROR, _("You can not delete this contractor"))
        return HttpResponseRedirect(reverse('list_contractors'))

    for user in contractor.team.all():
        user.work_for.remove(contractor)
        if user.work_for.count() == 0:
            user.contractor = False
            if not user.agent and not user.manager:
                user.logical_deleted = True
                user.is_active = False
        user.save()

    contractor.delete()
    messages.add_message(request, messages.SUCCESS, _("Contractor deleted successfully"))

    #FMSUser.objects.get(id=request.REQUEST.get('userId')).delete()
    return HttpResponseRedirect(reverse('list_contractors'))
