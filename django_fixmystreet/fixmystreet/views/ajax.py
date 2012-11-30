
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import Context, RequestContext
from django_fixmystreet.fixmystreet.models import ReportCategory, ReportMainCategoryClass, ReportSecondaryCategoryClass, FMSUser
from django_fixmystreet.fixmystreet.session_manager import SessionManager
from django_fixmystreet.fixmystreet.forms import FileUploadForm
from django.utils.translation import ugettext as _
from django.utils.translation import get_language
from django.utils import translation
from django.conf import settings
def report_category_note(request, id):
    cat = ReportMainCategoryClass.objects.get(id=id)
    if not cat.hint:
        return HttpResponse("")
    return HttpResponse("<div class='note'><strong>{0}</strong><p>{1}</p></div>".format(
        _("Please Note"),
        cat.hint.label
    ))

def create_comment(request):
	session_manager = SessionManager()
	session_manager.createComment(request.POST.get('title'),request.POST.get('text'),request.session.session_key)
        hh = HttpResponse(content='True', mimetype='text/html')
	return hh 
	
def create_file(request):
    session_manager = SessionManager()
    print request.POST
    session_manager.createFile(request.POST.get('title'),request.POST.get('file'),request.session.session_key)
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

def update_last_used_language(request):
    if request.user.id:
        fmsUser = FMSUser.objects.get(pk=request.user.id)
        fmsUser.last_used_language = request.REQUEST.get('language').upper()
        fmsUser.save()
    translation.activate(request.REQUEST.get('language'))
    fromUrl = request.REQUEST.get('from')
    if 'pro' in fromUrl:
        fromUrl = '/'+request.REQUEST.get('language')+'/pro/'
    else:
        fromUrl = '/'+request.REQUEST.get('language')+'/'
    return HttpResponseRedirect(fromUrl)
