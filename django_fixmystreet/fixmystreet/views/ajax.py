
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import Context, RequestContext
from django_fixmystreet.fixmystreet.models import ReportCategory, ReportMainCategoryClass, ReportSecondaryCategoryClass
from django_fixmystreet.fixmystreet.session_manager import SessionManager
from django.utils.translation import ugettext as _
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
	return True
	
def create_file(request):
	session_manager = SessionManager()
	session_manager.createFile(request.POST.get('title'),request.POST.get('file'),request.session.session_key)
	return True

def uploadFile(request):
	print request.FILES
	print request.FILES.getlist('form_file')
	for upfile in request.FILES.getlist('form_file'):
		filename = upfile.name
		# instead of "filename" specify the full path and filename of your choice here
		fd = open(filename, 'w')
		fd.write(upfile['content'])
		fd.close()
