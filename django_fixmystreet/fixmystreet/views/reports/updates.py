from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.template import Context, RequestContext
from django.contrib import messages
from django.utils.translation import ugettext as _

from django_fixmystreet.fixmystreet.models import Report, ReportUpdate, Ward, ReportCategory
from django_fixmystreet.fixmystreet.forms import ReportForm, ReportUpdateForm

def new( request, report_id ):
    report = get_object_or_404(Report, id=report_id)
    if request.method == 'POST':
        update_form = ReportUpdateForm(request.POST)
        if update_form.is_valid():
            update = update_form.save(request.user,report,commit=False)
            update.is_fixed = request.POST.has_key('is_fixed')
            update.save()
            messages.add_message(request, messages.SUCCESS, _('The report has been sucessfully updated.'))

        return HttpResponseRedirect(report.get_absolute_url())
    raise Http404()
