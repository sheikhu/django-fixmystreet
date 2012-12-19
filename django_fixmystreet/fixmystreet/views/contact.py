from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect

from django_fixmystreet.fixmystreet.forms import ContactForm

def thanks(request): 
     return render_to_response("contact/thanks.html", {},
                context_instance=RequestContext(request))

def new(request):
    if request.method == 'POST':
        form = ContactForm(data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/contact/thanks")
    else:
        form = ContactForm()

    return render_to_response("contact/new.html",
                              { 'contact_form': form },
                              context_instance=RequestContext(request))
