from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils.translation import ugettext_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django_fixmystreet.fixmystreet.utils import FixStdImageField
from django_fixmystreet.fixmystreet.forms import AgentCreationForm
from django_fixmystreet.backoffice.forms import UserEditForm
from django_fixmystreet.fixmystreet.models import OrganisationEntity, FMSUser, ReportMainCategoryClass, ReportSecondaryCategoryClass, ReportCategory, ReportNotification
from django_fixmystreet.fixmystreet.stats import TypesWithUsersOfOrganisation, UsersAssignedToCategories


def show(request):
    user = request.fmsuser
    userType = request.REQUEST.get("userType")
    currentOrganisationId = user.organisation.id
    users = []
    if userType == 'users':
        #Get organisations dependants from the current organisation id
        dependantOrganisations = OrganisationEntity.objects.filter(dependency_id = currentOrganisationId)
        allOrganisation = list(dependantOrganisations)
        allOrganisation.append(currentOrganisationId)
        users = FMSUser.objects.filter(organisation_id__in=allOrganisation)
    if userType == 'agent':
        users = FMSUser.objects.filter(organisation_id=currentOrganisationId)
        users = users.filter(agent = True)
    if userType == 'contractor':
        dependantOrganisations = OrganisationEntity.objects.filter(dependency_id = currentOrganisationId)
        allOrganisation = list(dependantOrganisations)
        users = FMSUser.objects.filter(organisation_id__in=allOrganisation)
        users = users.filter(contractor=True)
    if userType == 'impetrant':
        users = FMSUser.objects.filter(organisation_id=currentOrganisationId)
        users = users.filter(impetrant=True)
    if userType == 'manager':
        users = FMSUser.objects.filter(organisation_id=currentOrganisationId)
        users = users.filter(manager=True)
    
    users = users.filter(logical_deleted = False)
    
    return render_to_response("pro/users_overview.html",{
        "users":users,
    },context_instance=RequestContext(request))


def edit(request):
    userType = request.REQUEST.get("userType")
    #Get user connected
    user = request.fmsuser
    
    currentOrganisationId = user.organisation.id
    users = []
    if userType == 'users':
        #Get organisations dependants from the current organisation id
        dependantOrganisations = OrganisationEntity.objects.filter(dependency_id = currentOrganisationId)
        allOrganisation = list(dependantOrganisations)
        allOrganisation.append(currentOrganisationId)
        users = FMSUser.objects.filter(organisation_id__in=allOrganisation)
    if userType == 'agent':
        users = FMSUser.objects.filter(organisation_id=currentOrganisationId)
        users = users.filter(agent = True)
    if userType == 'contractor':
        dependantOrganisations = OrganisationEntity.objects.filter(dependency_id = currentOrganisationId)
        allOrganisation = list(dependantOrganisations)
        users = FMSUser.objects.filter(organisation_id__in=allOrganisation)
        users = users.filter(contractor=True)
    if userType == 'impetrant':
        users = FMSUser.objects.filter(organisation_id=currentOrganisationId)
        users = users.filter(impetrant=True)
    if userType == 'manager':
        users = FMSUser.objects.filter(organisation_id=currentOrganisationId)
        users = users.filter(manager=True)
    #Filter deleted users
    users = users.filter(logical_deleted = False)
    #Get used to edit
    user_to_edit = FMSUser.objects.get(pk=int(request.REQUEST.get('userId')))

    connectedUser = request.fmsuser
    canEditGivenUser = (((user_to_edit.manager or user_to_edit.agent) and connectedUser.leader) or ((user_to_edit.agent) and connectedUser.manager))
    return render_to_response("pro/users_overview.html",{
                        "users":users,
                        "canEditGivenUser":canEditGivenUser,
                        "editForm":UserEditForm(instance=user_to_edit)
                        },context_instance=RequestContext(request))


def saveChanges(request):
    userEditForm = UserEditForm(request.POST)
    print "Going to edit user id= "
    print request.REQUEST.get('userId')
    userEditForm.save(request.REQUEST.get('userId'))
    return HttpResponseRedirect('/pro/users/overview?userType='+request.REQUEST.get('userType'))


def deleteUser(request):
    # todo set active = false
    print 'Deleting user with id='
    print request.REQUEST.get('userId')
    user_to_delete = FMSUser.objects.get(id=request.REQUEST.get('userId'))
    user_to_delete.logical_deleted = True
    user_to_delete.save()
    #FMSUser.objects.get(id=request.REQUEST.get('userId')).delete()
    return HttpResponseRedirect('/pro/users/overview?userType='+request.REQUEST.get('userType'))

def createUser(request, userType):
    connectedUser = request.fmsuser

    isManager = connectedUser.manager    
    #a boolean value to tell the ui if the user can edit the given form content
    if request.method == "POST":
        user_type = int(request.POST.get("user_type"))
        createform = AgentCreationForm(request.POST)
        if createform.is_valid():
            createdOrganisationEntity = -1;    
            #Also create the organisation too            
            if (user_type == FMSUser.CONTRACTOR):
                createdOrganisationEntity = OrganisationEntity()
                createdOrganisationEntity.name_nl = request.POST.get('first_name')+"/"+request.POST.get('last_name')
                createdOrganisationEntity.name_fr = request.POST.get('first_name')+"/"+request.POST.get('last_name')
                createdOrganisationEntity.name_en = request.POST.get('first_name')+"/"+request.POST.get('last_name')
                createdOrganisationEntity.region = False
                createdOrganisationEntity.commune = False
                createdOrganisationEntity.subcontractor = True
                createdOrganisationEntity.applicant = False
                createdOrganisationEntity.dependency_id = connectedUser.organisation.id
                createdOrganisationEntity.save()
            
            createdUser = createform.save(connectedUser, createdOrganisationEntity, user_type)

            if createdUser:
                notifiation = ReportNotification(
                    content_template='send_created_to_user',
                    recipient=createdUser,
                    related=createdUser,
                )
                notifiation.save(data={
                        "password":request.POST.get('password1')
                    })
                return HttpResponseRedirect('/pro/')
    else:
        createform = AgentCreationForm()
    
    return render_to_response("pro/user_create.html",
            {
                "createform":createform,
                "isManager":isManager
            },
            context_instance=RequestContext(request))

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

