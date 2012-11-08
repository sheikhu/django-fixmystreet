from operator import attrgetter
import datetime

from django.shortcuts import render_to_response, get_object_or_404
from django.template import Context, RequestContext
from django.db import connection
from django.utils.translation import ugettext_lazy, ugettext as _
from django.db.models import  Count

from django_fixmystreet.fixmystreet.models import Ward, Report
from django_fixmystreet.fixmystreet.models import Report, CityTotals, CityWardsTotals, AllCityTotals

def show_by_number( request, city_id, ward_no ):
    city= get_object_or_404(City, id=city_id)
    wards = Ward.objects.filter( city=city, number=ward_no)
    return render_to_response("wards/show.html",
                {
                    "ward": wards[0],
                    "reports": []
                },
                context_instance=RequestContext(request))

def show( request, ward_id ):
    ward = get_object_or_404(Ward, id=ward_id)

    reports = list(Report.objects.filter(ward = ward).extra( select = { 'status' : """
        CASE 
        WHEN age( clock_timestamp(), created_at ) < interval '1 month' AND is_fixed = false THEN 'New Problems'
        WHEN age( clock_timestamp(), created_at ) >= interval '1 month' AND is_fixed = false THEN 'Older Unresolved Problems'
        WHEN age( clock_timestamp(), fixed_at ) < interval '1 month' AND is_fixed = true THEN 'Recently Fixed'
        WHEN age( clock_timestamp(), fixed_at ) >= interval '1 month' AND is_fixed = true THEN 'Old Fixed'
        ELSE 'Unknown Status'
        END """,
        'status_int' : """
        CASE 
        WHEN age( clock_timestamp(), created_at ) < interval '1 month' AND is_fixed = false THEN 0
        WHEN age( clock_timestamp(), created_at ) >= interval '1 month' AND is_fixed = false THEN 1
        WHEN age( clock_timestamp(), fixed_at ) < interval '1 month' AND is_fixed = true THEN 2
        WHEN age( clock_timestamp(), fixed_at ) >= interval '1 month' AND is_fixed = true THEN 3
        ELSE 4
        END """ }, order_by = ['-created_at'] ))#[:40]
    reports.sort(key=attrgetter('status_int'))
    
    # translated for po file
    _('New Problems')
    _('Older Unresolved Problems')
    _('Recently Fixed')
    _('Older Fixed Problems')
    return render_to_response("wards/show.html",
                {"ward": ward,
                 "reports": reports,
 #                "status_display" : [ _('New Problems'), _('Older Unresolved Problems'),  _('Recently Fixed'), _('Older Fixed Problems') ] 
                },
                context_instance=RequestContext(request))
