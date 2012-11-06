from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django_fixmystreet.fixmystreet.forms import AgentCreationForm

@login_required(login_url='/pro/accounts/login/')
def createAgent(request):
    if request.method == "POST":
        createform = AgentCreationForm(request.POST)
        if createform.is_valid():
        	user = createform.save()
        	if user:
        		return HttpResponseRedirect('/pro/')
    else:
        createform = AgentCreationForm()
    
    return render_to_response("createuser.html",
            {
                "createform":createform
            },
            context_instance=RequestContext(request))
            
@login_required(login_url='/pro/accounts/login/')
def createEntity(request):
    if request.method == "POST":
        createform = UserCreationForm(request.POST)
        if createform.is_valid():
        	user = createform.save()
        	if user:
        		return HttpResponseRedirect('/pro/')
    else:
        createform = UserCreationForm()
    
    return render_to_response("createuser.html",
            {
                "createform":createform
            },
            context_instance=RequestContext(request))
            
@login_required(login_url='/pro/accounts/login/')
def createExecuteur(request):
    if request.method == "POST":
        createform = UserCreationForm(request.POST)
        if createform.is_valid():
        	user = createform.save()
        	if user:
        		return HttpResponseRedirect('/pro/')
    else:
        createform = UserCreationForm()
    
    return render_to_response("createuser.html",
            {
                "createform":createform
            },
            context_instance=RequestContext(request))
            
@login_required(login_url='/pro/accounts/login/')
def createGestionnaire(request):
    if request.method == "POST":
        createform = UserCreationForm(request.POST)
        if createform.is_valid():
        	user = createform.save()
        	if user:
        		return HttpResponseRedirect('/pro/')
    else:
        createform = UserCreationForm()
    
    return render_to_response("createuser.html",
            {
                "createform":createform
            },
            context_instance=RequestContext(request))
            
@login_required(login_url='/pro/accounts/login/')
def createImpetrant(request):
    if request.method == "POST":
        createform = UserCreationForm(request.POST)
        if createform.is_valid():
        	user = createform.save()
        	if user:
        		return HttpResponseRedirect('/pro/')
    else:
        createform = UserCreationForm()
    
    return render_to_response("createuser.html",
            {
                "createform":createform
            },
            context_instance=RequestContext(request))