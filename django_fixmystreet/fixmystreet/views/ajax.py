from django.shortcuts import render_to_response, get_object_or_404
from django.template import Context, RequestContext
from django_fixmystreet.fixmystreet.models import ReportCategory, ReportMainCategoryClass, ReportSecondaryCategoryClass
from django_fixmystreet.fixmystreet.session_manager import SessionManager
def category_desc(request,id):    
   return render_to_response("ajax/category_description.html",
                {"category": ReportCategory.objects.get(id=id),
                  },
                context_instance=RequestContext(request))

def maincategory_desc(request,id):    
   return render_to_response("ajax/maincategory_description.html",
                {"category": ReportMainCategoryClass.objects.get(id=id),
                  },
                context_instance=RequestContext(request))

def create_comment(request):
	session_manager = SessionManager()
	session_manager.createComment(request.POST.get('title'),request.POST.get('text'),request.session.session_key)
	return True
	
def create_file(request):
	session_manager = SessionManager()
	session_manager.createFile(request.POST.get('title'),request.POST.get('file'),request.session.session_key)
	return True