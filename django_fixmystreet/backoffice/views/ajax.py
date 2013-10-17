
import json
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from django_fixmystreet.fixmystreet.models import FMSUser, ReportCategory, Report,ReportMainCategoryClass
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

def get_report_popup_details(request):
    report_id = request.REQUEST.get("report_id")
    report = Report.objects.get(id=report_id)
    return HttpResponse(json.dumps(report.full_marker_detail_pro_JSON()), mimetype="application/json")

def updatePriority(request, report_id):
    report=get_object_or_404(Report, id=report_id)
    report.gravity = int(request.GET["gravity"])
    report.probability = int(request.GET["probability"])
    report.save()
    return HttpResponse(json.dumps({"priority":report.get_priority()}), mimetype="application/json")

def filter_map(request):
    mFilter = request.GET["filter"]
    result = []
    if "created" in mFilter:
        result += Report.objects.all().filter(status=Report.CREATED)
    if "in_progress" in mFilter:
        result += Report.objects.all().filter(status__in=Report.REPORT_STATUS_IN_PROGRESS)
    if "closed" in mFilter:
        result+= Report.objects.all().filter(status__in= Report.REPORT_STATUS_CLOSED)
    if mFilter == "":
        result += Report.objects.all()

    jsonList =[]
    jsonString= "["
    for report in result:
        jsonString+= json.dumps(report.marker_detail_short())+","

    jsonString = jsonString[:-1]
    jsonString+= "]"

    return HttpResponse(jsonString,mimetype="application/json")

def report_false_address(request, report_id):
    if request.method == "POST":
        report = get_object_or_404(Report, id=report_id)

        false_address = request.POST.get('false_address');
        report.false_address = false_address;
        report.save();

        return HttpResponse(report.false_address);

def secondary_category_for_main_category(request):
    main_category_id = int(request.GET["main_category"])
    secondary_categories = ReportCategory.objects.filter(category_class=main_category_id)
    jsonstring= ReportCategory.listToJSON(secondary_categories)
    return HttpResponse(jsonstring,mimetype="application/json")

def update_category_for_report(request,report_id):
    main_category_id = int(request.POST["main_category"])
    secondary_category_id = int(request.POST["secondary_category"])
    report = get_object_or_404(Report,id=report_id)
    report.category = ReportMainCategoryClass.objects.get(id=main_category_id)
    report.secondary_category = ReportCategory.objects.get(id=secondary_category_id)
    report.save()
    return HttpResponse(json.dumps({"returntype":"ok"}),mimetype="application/json")
