from django.shortcuts import render_to_response
from django.template import RequestContext

from apps.fixmystreet.models import OrganisationEntity, ReportMainCategoryClass, ReportSecondaryCategoryClass, ReportCategory


# Build the table of groups dispatching.
def getTable(organisation):
    table = []

    # Line: Build each lines concerning one SecondaryCategory.
    for secCat in ReportSecondaryCategoryClass.objects.all():
        mainCategories = []

        # Column: For one SecondaryCategory, build each columns concerning MainCategoryClass
        for mainCat in ReportMainCategoryClass.objects.all():
            groups = []
            categories = ReportCategory.objects.filter(category_class_id=mainCat.id, secondary_category_class_id=secCat.id)

            # Cell: Inside each cell, list all groups
            for cat in categories:
                groups.append(cat.assigned_to_department.filter(dependency=organisation))

            mainCategories.append({'id': mainCat.id, 'groups': groups})

        table.append({'secondCategory': secCat, 'mainCategories': mainCategories})

    return table


def show(request):
    # Return the current selected list so that the buttons in the matrix have as label all names of selected managers
    return render_to_response("pro/manager_category_configuration.html",
        {
            "maincategories": ReportMainCategoryClass.objects.all(),
            "table": getTable(request.fmsuser.organisation)
        },
        context_instance=RequestContext(request))


def update(request):
    organisation = request.fmsuser.organisation
    maincategories = ReportMainCategoryClass.objects.all()

    #Set the categories for the selected main and secondary category.
    categories = ReportCategory.objects.filter(category_class_id=request.REQUEST.get('main'))
    categories = categories.filter(secondary_category_class_id=request.REQUEST.get('second'))

    mainCategory = ReportMainCategoryClass.objects.get(id=request.REQUEST.get('main'))
    secondCategory = ReportSecondaryCategoryClass.objects.get(id=request.REQUEST.get('second'))
    return render_to_response("pro/manager_category_configuration.html", {
        "maincategories": maincategories,
        "table": getTable(organisation),
        "categories": categories,
        "groupDropDown": OrganisationEntity.objects.filter(type=OrganisationEntity.DEPARTMENT, dependency=organisation),
        "firstCateg": mainCategory,
        "secondCateg": secondCategory
    }, context_instance=RequestContext(request))
