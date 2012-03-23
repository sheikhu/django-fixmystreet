from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.template import Context, RequestContext
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.core.urlresolvers import reverse

from fixmystreet.models import Report, ReportSubscription


def create(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    subscriber = ReportSubscription(subscriber=request.user,report=report)
    subscriber.save()
    messages.add_message(request, messages.SUCCESS, _("You have subscribed from updates successfully"))
    return HttpResponseRedirect(report.get_absolute_url())

def unsubscribe(request, report_id):
    subscriber = get_object_or_404(ReportSubscription, report__id=report_id, subscriber=request.user)
    report = subscriber.report
    subscriber.delete()
    messages.add_message(request, messages.SUCCESS, _("You have unsubscribed from updates successfully"))
    return HttpResponseRedirect(report.get_absolute_url())

    
