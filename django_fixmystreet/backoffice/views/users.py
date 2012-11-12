from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django_fixmystreet.backoffice.forms import UserEditForm
from django_fixmystreet.fixmystreet.models import TypesWithUsersOfOrganisation,FMSUser, UsersAssignedToCategories, getLoggedInUserId, ReportMainCategoryClass, ReportSecondaryCategoryClass, ReportCategory
from django.contrib.sessions.models import Session
from django.utils.translation import ugettext_lazy

@login_required(login_url='/pro/accounts/login/')
def show(request):

	userType = request.REQUEST.get("userType")
	currentOrganisationId = 1
	users = FMSUser.objects.filter(organisation_id=currentOrganisationId)
	if userType == 'agent':
		users = users.filter(agent = True)
	if userType == 'contractor':
		users = users.filter(contractor=True)
	if userType == 'impetrant':
		users = users.filter(impetrant=True)
	if userType == 'manager':
		users = users.filter(manager=True)
	return render_to_response("users_overview.html",{
		"users":users,
	},context_instance=RequestContext(request))

@login_required(login_url='/pro/accounts/login/')
def edit(request):
	userType = request.REQUEST.get("userType")
	currentOrganisationId = 1
	users = FMSUser.objects.filter(organisation_id=currentOrganisationId)
	if userType == 'agent':
		users = users.filter(agent = True)
	if userType == 'contractor':
		users = users.filter(contractor=True)
	if userType == 'impetrant':
		users = users.filter(impetrant=True)
	if userType == 'manager':
		users = users.filter(manager=True)
	user = FMSUser.objects.get(pk=int(request.REQUEST.get('userId')))
	return render_to_response("users_overview.html",{
						"users":users,
						"editForm":UserEditForm(instance=user)
						},context_instance=RequestContext(request))

@login_required(login_url='/pro/accounts/login/')
def saveChanges(request):
	print 'Before'
	userEditForm = UserEditForm(request.POST)
	print 'After'
	userEditForm.save(request.REQUEST.get('userId'))
	return HttpResponseRedirect('/pro/users/overview?userType='+request.REQUEST.get('userType'))