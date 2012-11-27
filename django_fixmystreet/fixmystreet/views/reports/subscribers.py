from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.template import Context, RequestContext
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.core.urlresolvers import reverse
from django_fixmystreet.fixmystreet.models import FMSUser
from django.db import IntegrityError

from django_fixmystreet.fixmystreet.models import Report, ReportSubscription


def create(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    #CREATE USER CITIZEN IF NECESSARY 
    try:
        user = FMSUser.objects.get(username=request.REQUEST.get('citizen_email'));
    except FMSUser.DoesNotExist:
        #Add information about the citizen connected if it does not exist
        user = FMSUser.objects.create(username=request.REQUEST.get('citizen_email'), email=request.REQUEST.get('citizen_email'), first_name='ANONYMOUS', last_name='ANONYMOUS')

    #VERIFY THAT A SUBSCRIPTION DOES NOT ALREADY EXIST
    try:
        subscriber = ReportSubscription(subscriber=user,report=report)
        subscriber.save()
        messages.add_message(request, messages.SUCCESS, _("You have subscribed from updates successfully"))
    except IntegrityError, e:   
        #Do nothing. A subscription for this user already exists...
        messages.add_message(request, messages.SUCCESS, _("You have subscribed from updates successfully"))
    
    return HttpResponseRedirect(report.get_absolute_url())
