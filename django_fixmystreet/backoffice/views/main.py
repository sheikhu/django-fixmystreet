from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.utils.translation import activate
from django.core.urlresolvers import reverse


def home(request, location = None, error_msg =None):
    if not request.LANGUAGE_CODE == request.fmsuser.last_used_language.lower():
        activate(request.user.fmsuser.last_used_language.lower())
        return HttpResponseRedirect(reverse("home_pro"))

    #Redirect to pro section: list of reports if the user has the role manager
    if (request.fmsuser.manager):
        fromUrl = reverse('report_list_pro', args=['all'])
        return HttpResponseRedirect(fromUrl)
    else:
        fromUrl = reverse('report_prepare_pro')
        return HttpResponseRedirect(fromUrl)

