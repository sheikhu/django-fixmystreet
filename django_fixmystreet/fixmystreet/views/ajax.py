from django.http import HttpResponse

from django_fixmystreet.fixmystreet.models import ReportMainCategoryClass
from django.utils.translation import ugettext as _

def report_category_note(request, id):
    cat = ReportMainCategoryClass.objects.get(id=id)
    if not cat.hint:
        return HttpResponse("")
    return HttpResponse("<div class='note'><strong>{0}</strong><p>{1}</p></div>".format(
        _("Please Note"),
        cat.hint.label
    ))
