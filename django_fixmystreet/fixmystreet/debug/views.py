from django.http import HttpResponse

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
        output += "Report %s" % report.merged_with.id
        output += "<br/>"

        # Rank merged
        rank_merged = Report.objects.filter(id=report.id).rank(report.merged_with.point, report.merged_with.secondary_category, report.merged_with.created)[0].rank
        output += "merged with %s rank %s" %(report.id, rank_merged)

        output += "<ol>"
        reports_ranked = Report.objects.all().exclude(id=report.merged_with.id).rank(report.merged_with.point, report.merged_with.secondary_category, report.merged_with.created)
        for ranked in reports_ranked[:10]:
            output += "<li>"
            if ranked.id == report.id:
                output += "<strong>"
            output += "potential duplicate %s rank %s" % (ranked.id, ranked.rank)

            if ranked.id == report.id:
                output += "</strong>"
            output += "</li>"

        output += "</ol>"
        output += "Total: %s <br/>" % len(reports_ranked)
        output += "<br/><br/>"

    return HttpResponse(output)
