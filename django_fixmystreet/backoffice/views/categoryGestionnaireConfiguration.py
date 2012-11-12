from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django_fixmystreet.backoffice.forms import ManagersListForm
from django_fixmystreet.fixmystreet.models import TypesWithUsersOfOrganisation,FMSUser, UsersAssignedToCategories, getLoggedInUserId, ReportMainCategoryClass, ReportSecondaryCategoryClass, ReportCategory
from django.contrib.sessions.models import Session

@login_required(login_url='/pro/accounts/login/')
def show(request):
    maincategories = ReportMainCategoryClass.objects.all()
    secondcategories = ReportSecondaryCategoryClass.objects.all()
    #This list will be filled with the names of the current selected managers over the whole matrix
    currentSelectedList = [["" for _ in range(len(secondcategories))] for _ in range(len(maincategories))]
    
    currentUserOrganisationId = FMSUser.objects.get(pk=getLoggedInUserId(Session.objects.all()[0].session_key)).organisation.id
    for main in maincategories:
        for second in secondcategories:
            #This query will get all the users that are assigned to the types that are linked with the given main and secondary category. 
            #These users must also be in the same organisation as the current logged in user.
            users = UsersAssignedToCategories(main.id,second.id,currentUserOrganisationId)
            userString = ""
            for u in users.get_results():
                userString+= u[0]+" "+u[1]+"/"
            currentSelectedList[main.id-1][second.id-1]= currentSelectedList[main.id-1][second.id-1]+userString
    # Return the main categories list, secondary categories list for displaying the matrix column- and rowheaders.
    # Return an empty categories list (types) because we are showing the page (not doing the selection via popup)
    # Return the current selected list so that the buttons in the matrix have as label all names of selected managers
    return render_to_response("category_gestionnaire_configuration.html",
            {
                "maincategories" : maincategories,
                "secondcategories": secondcategories,
                "categories": [],
                "currentSelectedList":currentSelectedList
            },
            context_instance=RequestContext(request))

@login_required(login_url='/pro/accounts/login/')
def update(request):
    maincategories = ReportMainCategoryClass.objects.all()
    secondcategories = ReportSecondaryCategoryClass.objects.all()
    #Set the categories for the selected main and secondary category.
    categories = ReportCategory.objects.filter(category_class_id=request.REQUEST.get('main'))
    categories = categories.filter(secondary_category_class_id=request.REQUEST.get('second'))
    #This list will be filled with the names of the current selected managers over the whole matrix
    currentSelectedList = [["" for _ in range(len(secondcategories))] for _ in range(len(maincategories))]
    currentUserOrganisationId = FMSUser.objects.get(pk=getLoggedInUserId(Session.objects.all()[0].session_key)).organisation.id
    for main in maincategories:
        for second in secondcategories:
            #This query will get all the users that are assigned to the types that are linked with the given main and secondary category.
            #These users must also be in the same organisation as the current logged in user.
            users = UsersAssignedToCategories(main.id,second.id,currentUserOrganisationId)
            userString = ""
            for u in users.get_results():
                userString+= u[0]+" "+u[1]+"/"
            currentSelectedList[main.id-1][second.id-1]= currentSelectedList[main.id-1][second.id-1]+userString
    #This list will be filled with the names of the selected managers for the given types in "categories"
    categoryUserMapping = [0]*len(ReportCategory.objects.all())
    #This query will return for each type the currently selected manager
    res = TypesWithUsersOfOrganisation(currentUserOrganisationId).get_results()
    for item in res:
        categoryUserMapping[item[0]-1]=item[1]
    #Return main and secondary categories lists for displaying the maxtrix colmun- and rowheaders
    #Return the categories linked with the selected main and secondary category
    #Return the current selected list so that the buttons in the matrix have as label all names of selected managers
    #Return the dropdown form to select managers from
    #Return the category user mapping so that the shown selection boxes contain the current selected managers
    return render_to_response("category_gestionnaire_configuration.html",
            {
                "maincategories" : maincategories,
                "secondcategories": secondcategories,
                "categories":categories,
                "currentSelectedList":currentSelectedList,
                "managerDropDown":ManagersListForm(),
                "categoryUserMapping":categoryUserMapping
            },
            context_instance=RequestContext(request))