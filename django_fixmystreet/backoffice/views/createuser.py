from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django_fixmystreet.fixmystreet.forms import AgentCreationForm
from django_fixmystreet.fixmystreet.models import FMSUser, ReportCategory, OrganisationEntity
from django.views.generic.edit import FormView

@login_required(login_url='/pro/accounts/login/')
def createUser(request):
    user = request.user
    connectedUser = FMSUser.objects.get(user_ptr_id=user.id)

    isManager = connectedUser.manager

    #a boolean value to tell the ui if the user can edit the given form content
    if request.method == "POST":
        createform = AgentCreationForm(request.POST)
        if createform.is_valid():
	
		createdOrganisationEntity = -1;	
		#Also create the organisation too
		if (request.POST.get("contractorRadio") == "1"):
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
		#createdUser = createform.save(userid,request.POST.get("userType"))
        	createdUser = createform.save(user, createdOrganisationEntity, request.POST.get("agentRadio"), request.POST.get("managerRadio"),request.POST.get("contractorRadio"))
        	
		#If this is the first user created and of type gestionnaire then assign all reportcategories to him
		if (createdUser.manager == True & connectedUser.leader == True):
			#if we have just created the first one, then apply all type to him
			#import pdb
			#pdb.set_trace()
			if len(FMSUser.objects.filter(organisation_id=connectedUser.organisation.id).filter(manager=True)) == 1:
				for type in ReportCategory.objects.all():
					createdUser.categories.add(type)

		if createdUser:
        		return HttpResponseRedirect('/pro/')
    else:
        createform = AgentCreationForm()
    
    return render_to_response("createuser.html",
            {
                "createform":createform,
                "isManager":isManager
            },
            context_instance=RequestContext(request))
