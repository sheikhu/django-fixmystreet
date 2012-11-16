from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django_fixmystreet.fixmystreet.forms import AgentCreationForm
from django_fixmystreet.fixmystreet.models import getLoggedInUserId, FMSUser, ReportCategory

@login_required(login_url='/pro/accounts/login/')
def createUser(request):
    userid = getLoggedInUserId(request.COOKIES.get("sessionid"))
    connectedUser = FMSUser.objects.get(user_ptr_id=userid)

    isManager = connectedUser.manager

    #a boolean value to tell the ui if the user can edit the given form content
    if request.method == "POST":
        createform = AgentCreationForm(request.POST)
        if createform.is_valid():
        	#createdUser = createform.save(userid,request.POST.get("userType"))
        	createdUser = createform.save(userid,request.POST.get("agentRadio"),request.POST.get("managerRadio"),request.POST.get("impetrantRadio"),request.POST.get("contractorRadio"))
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
