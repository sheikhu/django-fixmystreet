# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from apps.fixmystreet.models import Report, ReportComment, ReportEventLog
from django.utils import translation
import os
from datetime import timedelta

class Command(BaseCommand):
    help = 'Fix abp'

    ABP_USER = 10673
    ABP_ENTITY = 23

    REPORTS_CREATED = []

    def handle(self, *args, **options):
        abp_reports = Report.objects.filter(responsible_entity=self.ABP_ENTITY, status=Report.CREATED)

        for report in abp_reports:
            print report.id

            # Extract date and reference_id from comments
            created, contractor_reference_id = self.extract_created_reference_id(report)

            if not created or not contractor_reference_id:
                self.REPORTS_CREATED.append(report.id)
                continue

            # Fill contractor_reference_id if missing by parsing comments
            if not report.contractor_reference_id:
                report.contractor_reference_id = contractor_reference_id

            # Change report status
            report.status = Report.MANAGER_ASSIGNED

            # Set accepted date with first abp comment
            report.accepted_at = created

            print '    %s %s %s' % (report.status, report.accepted_at, report.contractor_reference_id)
            report.bypassStatusChanged = True
            report.save()

        print "Reports CREATED", self.REPORTS_CREATED

    def extract_created_reference_id(self, report):
        comments = ReportComment.objects.filter(report=report.id, created_by=self.ABP_USER).order_by('created')

        for comment in comments:
            if u'Référence externe' in comment.text:
                splitted_values = comment.text.split(u'Référence externe:')
                return comment.created, splitted_values[1].strip()

        return None, None
