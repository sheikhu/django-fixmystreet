
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import Context, RequestContext
from django.utils.translation import ugettext as _
from django.conf import settings

from django_fixmystreet.fixmystreet.models import ReportCategory, ReportMainCategoryClass, ReportSecondaryCategoryClass, FMSUser
from django_fixmystreet.fixmystreet.session_manager import SessionManager
from django_fixmystreet.fixmystreet.forms import FileUploadForm


def report_category_note(request, id):
    cat = ReportMainCategoryClass.objects.get(id=id)
    if not cat.hint:
        return HttpResponse("")
    return HttpResponse("<div class='note'><strong>{0}</strong><p>{1}</p></div>".format(
        _("Please Note"),
        cat.hint.label
    ))

def create_comment(request):
	SessionManager.createComment(request.POST.get('title'), request.POST.get('text'), request.session)
	hh = HttpResponse(content='True', mimetype='text/html')
	return hh 

def create_file(request):
    SessionManager.createFile(request.POST.get('title'), request.POST.get('file'), request.session)
    hh = HttpResponse(content='True', mimetype='text/html')
    return hh 

def uploadFile(request):
    for file_code in request.FILES:
        upfile = request.FILES[file_code]
        with open('media/files/'+upfile.name, 'wb+') as destination:
            for chunk in upfile.chunks():
                destination.write(chunk)
    hh = HttpResponse(content='True',mimetype='text/html')
    return hh

