from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils.translation import ugettext_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django_fixmystreet.backoffice.forms import UserEditForm
from django_fixmystreet.fixmystreet.models import FMSUser, ReportMainCategoryClass, ReportSecondaryCategoryClass, ReportCategory
from django_fixmystreet.fixmystreet.stats import TypesWithUsersOfOrganisation, UsersAssignedToCategories


def show(request):
	user = FMSUser.objects.get(user_ptr_id=request.user.id)
	userType = request.REQUEST.get("userType")
	currentOrganisationId = user.organisation.id
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
	#Get user connected
	user = FMSUser.objects.get(user_ptr_id=request.user.id)
	
	currentOrganisationId = user.organisation.id
	users = FMSUser.objects.filter(organisation_id=currentOrganisationId)
	if userType == 'agent':
		users = users.filter(agent = True)
	if userType == 'contractor':
		users = users.filter(contractor=True)
	if userType == 'impetrant':
		users = users.filter(impetrant=True)
	if userType == 'manager':
		users = users.filter(manager=True)
	#Get used to edit
        user = FMSUser.objects.get(pk=int(request.REQUEST.get('userId')))

    	connectedUser = FMSUser.objects.get(user_ptr_id=request.user.id)
	

	canEditGivenUser = (((user.manager or user.agent) and connectedUser.leader) or ((user.agent) and connectedUser.manager))
	return render_to_response("users_overview.html",{
						"users":users,
						"canEditGivenUser":canEditGivenUser,
						"editForm":UserEditForm(instance=user)
						},context_instance=RequestContext(request))


def saveChanges(request):
	userEditForm = UserEditForm(request.POST)
	print "Going to edit user id= "
	print request.REQUEST.get('userId')
	userEditForm.save(request.REQUEST.get('userId'))
	return HttpResponseRedirect('/pro/users/overview?userType='+request.REQUEST.get('userType'))


def deleteUser(request):
	print 'Deleting user with id='
	print request.REQUEST.get('userId')
	FMSUser.objects.get(user_ptr_id=request.REQUEST.get('userId')).delete()
	return HttpResponseRedirect('/pro/users/overview?userType='+request.REQUEST.get('userType'))

# 
# class CreateUser(CreateView):
    # template_name = 'createuser.html'
    # form_class = UserForm
# 
# class UpdateUser(UpdateView):
    # template_name = 'users_overview.html'
    # form_class = UserForm
# 
# 
# class DeleteUser(UpdateView):
    # template_name = 'users_overview.html'
    # form_class = UserForm
    # success_url = '/pro/'

