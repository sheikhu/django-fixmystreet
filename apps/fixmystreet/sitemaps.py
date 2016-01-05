from django.contrib.sitemaps import Sitemap

from apps.fixmystreet.models import Report

class ReportSitemap(Sitemap):
    changefreq = "daily"

    def items(self):
        return Report.objects.filter(status__in=Report.REPORT_STATUS_IN_PROGRESS)
