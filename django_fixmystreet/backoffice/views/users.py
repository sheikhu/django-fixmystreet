import logging
from smtplib import SMTPException

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth import login, logout
from django.utils import translation
from django.contrib.auth.forms import PasswordChangeForm
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.core.exceptions import PermissionDenied

from django_fixmystreet.backoffice.forms import FmsUserForm, FmsUserCreateForm
from django_fixmystreet.fixmystreet.forms import LoginForm
from django_fixmystreet.fixmystreet.models import FMSUser

logger = logging.getLogger(__name__)


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.user
            login(request, user)
            # messages.add_message(request, messages.SUCCESS, _("You are logged in successfully"))
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


def list_users(request):
    current_user = request.fmsuser
    users = FMSUser.objects.filter(logical_deleted=False).is_pro()
    if current_user.organisation:
        users = users.filter(organisation=current_user.organisation)
    elif not request.user.is_superuser:
        raise PermissionDenied()

    return render_to_response("pro/auth/users_list.html", {
        'users': users,
        'can_create': current_user.leader
    }, context_instance=RequestContext(request))

def edit_user(request, user_id):
    current_user = request.fmsuser
    users = FMSUser.objects.all()
    if current_user.organisation:
        users = users.filter(organisation=current_user.organisation)
    elif not request.user.is_superuser:
        raise PermissionDenied()

    users = users.filter(logical_deleted=False)

    user_to_edit = users.get(id=user_id)
    can_edit = current_user.leader and not user_to_edit.leader

    if request.method == "POST" and can_edit:
        user_form = FmsUserForm(request.POST, instance=user_to_edit)
        if user_form.is_valid():
            user_form.save()
            return HttpResponseRedirect('')
    else:
        user_form = FmsUserForm(instance=user_to_edit)

    return render_to_response("pro/auth/user_edit.html", {
        'can_edit': can_edit,
        'user_form': user_form
    }, context_instance=RequestContext(request))


def create_user(request):
    can_edit = request.fmsuser.leader
    if request.method == "POST" and can_edit:
        user_form = FmsUserCreateForm(request.POST)
        if user_form.is_valid():
            try:
                user = user_form.save(commit=False)
                user.organisation = request.fmsuser.organisation
                user.save()
                user_form.notify_user()
                if user:
                    messages.add_message(request, messages.SUCCESS, _("User has been created successfully"))
                    return HttpResponseRedirect(user.get_absolute_url())
            except SMTPException as e:
                logger.error("email not sent successfully: {0}".format(e))
                messages.add_message(request, messages.ERROR, _("An error occurd during the email sending"))

    else:
        user_form = FmsUserCreateForm()

    return render_to_response("pro/auth/user_edit.html", {
                "user_form":user_form,
                "can_edit": can_edit
            }, context_instance=RequestContext(request))


def delete_user(request, user_id, user_type='users'):
    # todo set active = false

    user_to_delete = FMSUser.objects.get(id=user_id, organisation=request.fmsuser.organisation)

    can_edit = request.fmsuser.leader
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

