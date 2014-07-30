from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404

from django_fixmystreet.fixmystreet.models import Report, ReportSubscription

def create(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    if not report.subscriptions.filter(subscriber=request.user.fmsuser).exists():
        subscriber = ReportSubscription(subscriber=request.user.fmsuser, report=report)
        subscriber.save()

    return HttpResponseRedirect(report.get_absolute_url_pro())

def unsubscribe(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    try:
        subscriber = ReportSubscription.objects.get(report__id=report_id, subscriber=request.user)
        subscriber.delete()

        messages.add_message(request, messages.SUCCESS, _("You have unsubscribed successfully"))
    except ReportSubscription.DoesNotExist:
        messages.add_message(request, messages.SUCCESS, _("You were not subscribed."))

    return HttpResponseRedirect(report.get_absolute_url_pro())


