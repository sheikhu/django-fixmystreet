from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect

from django_fixmystreet.fixmystreet.models import Report, ReportSubscription


def create(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    if not report.subscriptions.filter(subscriber=request.user.fmsuser).exists():
        subscriber = ReportSubscription(subscriber=request.user.fmsuser, report=report)
        subscriber.save()
    return HttpResponseRedirect(report.get_absolute_url_pro())

def unsubscribe(request, report_id):
    subscriber = get_object_or_404(ReportSubscription, report__id=report_id, subscriber=request.user)
    report = subscriber.report
    subscriber.delete()
    return HttpResponseRedirect(report.get_absolute_url_pro())


