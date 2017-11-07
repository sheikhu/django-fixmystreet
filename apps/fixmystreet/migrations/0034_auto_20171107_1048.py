# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

from apps.fixmystreet.models import Report as ModelReport


class Migration(migrations.Migration):

    def fix_abp_async_reports(apps, schema_editor):
        Report = apps.get_model('fixmystreet', 'Report')
        ReportComment = apps.get_model('fixmystreet', 'ReportComment')

        ABP_USER = 10673
        ABP_ENTITY = 23
        REPORTS_CREATED = []

        abp_reports = Report.objects.filter(responsible_entity=ABP_ENTITY, status=ModelReport.CREATED)

        for report in abp_reports:
            print report.id

            created = None
            contractor_reference_id = None

            # Extract date and reference_id from comments
            comments = ReportComment.objects.filter(report=report.id, created_by=ABP_USER).order_by('created')

            for comment in comments:
                if u'Référence externe' in comment.text:
                    splitted_values = comment.text.split(u'Référence externe:')
                    created = comment.created
                    contractor_reference_id = splitted_values[1].strip()

            if not created or not contractor_reference_id:
                REPORTS_CREATED.append(report.id)
                continue

            # Fill contractor_reference_id if missing by parsing comments
            if not report.contractor_reference_id:
                report.contractor_reference_id = contractor_reference_id

            # Change report status
            report.status = ModelReport.MANAGER_ASSIGNED

            # Set accepted date with first abp comment
            report.accepted_at = created

            print '    %s %s %s' % (report.status, report.accepted_at, report.contractor_reference_id)
            report.save()

        print "Reports CREATED", REPORTS_CREATED

    dependencies = [
        ('fixmystreet', '0033_auto_20170905_1421'),
    ]

    operations = [
        migrations.RunPython(fix_abp_async_reports),
    ]
