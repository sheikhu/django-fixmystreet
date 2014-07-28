from django.http import HttpResponse
from django.template.loader import render_to_string

from django_fixmystreet.fixmystreet.models import Report

def rank(request):
    page = 0
    reports_merge = Report.objects.filter(merged_with__isnull=False).select_related('merged_with')

    # Filter by id
    if request.GET.get('id'):
        param_id = request.GET.get('id')
        reports_merge = reports_merge.filter(merged_with__id=param_id)
    # Filter by paging
    elif request.GET.get('page'):
        param_page = request.GET.get('page')
        page = 10 * int(param_page)

    if not reports_merge:
        return HttpResponse("No merged report")

    # Prepare results
    output = ""
    for report in reports_merge[page:page+10]:
        # Generate the rank for the related merged report
        rank_merged = Report.objects.filter(id=report.id).rank(report.merged_with, debug=True)[0].rank

        # Potential duplicates
        reports_ranked = Report.objects.all().rank(report.merged_with, debug=True)

        # Rendering
        output += render_to_string("debug/rank.html", {
            'report': report,
            'rank_merged': rank_merged,
            'reports_ranked': reports_ranked[:10],
            'total': len(reports_ranked)
        })

    return HttpResponse(output)

