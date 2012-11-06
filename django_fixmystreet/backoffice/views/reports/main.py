from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django_fixmystreet.fixmystreet.models import dictToPoint, Report, ReportSubscription
from django_fixmystreet.fixmystreet.forms import ReportForm, ReportUpdateForm, ReportFileForm,ReportCommentForm
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

@login_required(login_url='/pro/accounts/login/')
def new(request):
    pnt = dictToPoint(request.REQUEST)
    if request.method == "POST":
        report_form = ReportForm(request.POST, request.FILES)
        # this checks update is_valid too
        if report_form.is_valid():
            # this saves the update as part of the report.
            report = report_form.save(request.user)
            if report:
            	if "pro" in request.path:
                	return HttpResponseRedirect(report.get_absolute_url_pro())
                else:
                	return HttpResponseRedirect(report.get_absolute_url())
    else:
        report_form = ReportForm(initial={
            'x': request.REQUEST.get('x'),
            'y': request.REQUEST.get('y')
        })
    
    reports = Report.objects.filter(is_fixed = False).distance(pnt).order_by('distance')[0:10]
    statusQ = request.REQUEST.get('status')
    if statusQ == "0":
    	reports = Report.objects.filter(is_fixed = False).filter(status=1).distance(pnt).order_by('distance')[0:10]
    if statusQ == "1":
    	reports = Report.objects.filter(is_fixed = False).filter(status=2).distance(pnt).order_by('distance')[0:10]
    if statusQ == "2":
    	reports = Report.objects.filter(is_fixed = False).filter(status=3).distance(pnt).order_by('distance')[0:10]
    	
    return render_to_response("reports/new_pro.html",
            {
                "report_form": report_form,
                "pnt":pnt,
                "reports":reports
            },
            context_instance=RequestContext(request))

@login_required(login_url='/pro/accounts/login/')
def show(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    return render_to_response("reports/show_pro.html",
            {
                "report": report,
                "subscribed": request.user.is_authenticated() and ReportSubscription.objects.filter(report=report, subscriber=request.user).exists(),
                "update_form": ReportUpdateForm(),
                "comment_form": ReportCommentForm(),
                "file_form":ReportFileForm()
            },
            context_instance=RequestContext(request))