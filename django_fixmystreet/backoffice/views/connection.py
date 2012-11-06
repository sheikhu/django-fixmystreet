from django.shortcuts import render_to_response
from django.template import Context, RequestContext

def show( request):
	return render_to_response("connection.html",{},context_instance=RequestContext(request))