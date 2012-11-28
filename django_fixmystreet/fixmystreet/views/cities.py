from django.shortcuts import render_to_response, get_object_or_404
from django.template import Context, RequestContext
from django.db.models import  Count

from django_fixmystreet.fixmystreet.models import Report, CityTotals, CityWardsTotals, AllCityTotals

def index(request):    
    return render_to_response("cities/index.html",
                {"report_counts": AllCityTotals() },
                context_instance=RequestContext(request))


def show( request, city_id ):
    #city = get_object_or_404(City, id=city_id)
    
    #top_problems = Report.objects.filter(ward__city=city,is_fixed=False) \
    #        .annotate(subscriber_count=Count('reportsubscription')) \
    #        .filter(subscriber_count__gt=1) \
    #        .order_by('-subscriber_count')[:10]
        
    return render_to_response("cities/show.html",
                {#"city":city,
                 #'top_problems': top_problems,
                 #'city_totals' : CityTotals( '10 years',city),
                 #"report_counts": CityWardsTotals(city) },
},
                 context_instance=RequestContext(request))

def home( request, city, error_msg, disambiguate ):
    top_problems = Report.objects.filter(ward__city=city,is_fixed=False) \
            .annotate(subscriber_count=Count('reportsubscription')) \
            .filter(subscriber_count__gt=1) \
            .order_by('-subscriber_count')[:10]
    reports_with_photos = Report.objects.filter(is_confirmed=True, ward__city=city).exclude(photo='').order_by("-created")[:3]
    recent_reports = Report.objects.filter(is_confirmed=True, ward__city=city).order_by("-created")[:5]
        
    return render_to_response("cities/home.html",
                {"report_counts": CityTotals('1 year', city),
                # "cities": City.objects.all(),
                 'city':city,
                 'top_problems': top_problems,
                 "reports_with_photos": reports_with_photos,
                 "recent_reports": recent_reports , 
                 'error_msg': error_msg,
                 'disambiguate':disambiguate },
                context_instance=RequestContext(request))    
    
