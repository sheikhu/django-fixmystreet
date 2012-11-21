from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django_fixmystreet.fixmystreet.models import FMSUser, ReportCategory
from django_fixmystreet.fixmystreet.stats import UserTypeForOrganisation

def saveCategoryConfiguration(request):
	# Save the chosen categories from the different forms
	# The request url has this form:
	# base_url/?cat0=A&man0=B&cat1=C&man1=D&...   with A,C the id's of the first and second type and with B,D the id's of the selected managers for these types
	i = 0
	cat= "cat"
	man = "man"
	while request.REQUEST.get(cat+str(i)):
		#Get the manager from the given id
		manager = FMSUser.objects.get(user_ptr_id=request.REQUEST.get(man+str(i)))
		# Query to get the id of the user that are chosen to be reponsible of the given category id in the given organisation
		resul = UserTypeForOrganisation(int(request.REQUEST.get(cat+str(i))),manager.organisation.id)
		# If such a user exists remove the category from this user because another user is now assigned to be responsible for this category
		if resul.get_results():
			FMSUser.objects.get(user_ptr_id=resul.get_results()[0][0]).categories.remove(ReportCategory.objects.get(pk=resul.get_results()[0][1]))
		# Set for the user given in the request that he is responsible for this category
		manager.categories.add(ReportCategory.objects.get(pk=request.REQUEST.get(cat+str(i))))
		i = i+1
	return HttpResponseRedirect(reverse("category_gestionnaire_configuration"))
