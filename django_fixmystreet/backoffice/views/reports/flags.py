from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.template import Context, RequestContext
from django.template.loader import render_to_string
from django.core.mail import send_mail

from django_fixmystreet.fixmystreet.models import Report
from django.conf import settings

def new( request, report_id ):
    report = get_object_or_404(Report, id=report_id)
    if request.method == 'GET':
        return render_to_response("reports/flags/new.html",
                { "report": report },
                context_instance=RequestContext(request))
    else:
        report.flagComment = request.POST['comment']
        report.flagAsOffensive()
        return HttpResponseRedirect(report.get_absolute_url() + '/flags/thanks')

def thanks( request, report_id ):
    return render_to_response("reports/flags/thanks.html", {},
                context_instance=RequestContext(request))
