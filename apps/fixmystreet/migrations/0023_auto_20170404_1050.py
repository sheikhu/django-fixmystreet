# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings

import logging, csv, os

from ..management.commands.new_category_consts import *

logger = logging.getLogger("fixmystreet")

class Migration(migrations.Migration):

    def reports_migrations(apps, schema_editor):
        if os.environ.get('SKIP_MIGRATIONS', False) or settings.ENVIRONMENT == "jenkins":
            return

        Report = apps.get_model("fixmystreet", "Report")
        HistoricalReport = apps.get_model("fixmystreet", "HistoricalReport")
        Category_LVL_1 = apps.get_model("fixmystreet", "ReportMainCategoryClass")
        Category_LVL_2 = apps.get_model("fixmystreet", "ReportSecondaryCategoryClass")
        Category_LVL_3 = apps.get_model("fixmystreet", "ReportCategory")

        reports = Report.objects.all()

        # CATEGORIES MAPPING
        NEW_LVL = {}
        with open("apps/fixmystreet/migrations/categories_mapping.csv", 'rb') as mapping_file:
            mapping_reader = csv.reader(mapping_file, delimiter=','.encode('utf-8'), quotechar='"'.encode('utf-8'))

            for row in mapping_reader:
                NEW_LVL[int(row[LVL_3_ID_IDX])] = {
                    'LVL_1' : Category_LVL_1.objects.get(id=row[NEW_LVL_1_ID_IDX]),
                    'LVL_2' : Category_LVL_2.objects.get(id=row[NEW_LVL_2_ID_IDX]),
                    'LVL_3' : Category_LVL_3.objects.get(id=row[NEW_LVL_3_ID_IDX]),
                }

        # REPORTS MIGRATION
        max_reports = len(reports)
        LVL_3_ERRORS = []

        for idx, report in enumerate(reports):
            progression = (idx + 0.0) / max_reports * 100

            logger.info("Reports: %.2f%%  -  %s  %s  %s" % (progression, report.id, report.category.id, report.secondary_category.id))

            try:
                new_categories = NEW_LVL[report.secondary_category.id]

                # LVL 1
                report.category = new_categories['LVL_1']

                # LVL 3
                report.secondary_category = new_categories['LVL_3']

                # Save
                report.save()
            except KeyError:
                LVL_3_ERRORS.append({ 'report' : report.id,'cat': report.secondary_category.id})

        # Empty reports array
        reports = None

        # HISTORICAL REPORTS MIGRATION
        if os.environ.get('SKIP_MIGRATIONS_HISTORICALREPORT', False):
            return

        max_reports = HistoricalReport.objects.all().count()
        HISTORICAL_LVL_3_ERRORS = []

        step = 10000
        loop = 0

        while HistoricalReport.objects.filter(category_id__lt=1000).exists():

            partial_reports = HistoricalReport.objects.filter(category_id__lt=1000).order_by("id")[:step]

            for idx, report in enumerate(partial_reports):
                progression = (loop * step + idx + 0.0) / max_reports * 100

                logger.info("Historical Reports: %.2f%%  -  %s  %s  %s" % (progression, report.id, report.category.id, report.secondary_category.id))

                try:
                    new_categories = NEW_LVL[report.secondary_category.id]

                    # LVL 1
                    report.category = new_categories['LVL_1']

                    # LVL 3
                    report.secondary_category = new_categories['LVL_3']

                    # Save
                    report.save()
                except KeyError:
                    LVL_3_ERRORS.append({ 'report' : report.id,'cat': report.secondary_category.id})

            loop += 1

        logger.info('LVL3 ERRORS: %s' % LVL_3_ERRORS)
        logger.info('HISTORICAL LVL3 ERRORS: %s' % HISTORICAL_LVL_3_ERRORS)

    dependencies = [
        ('fixmystreet', '0022_auto_20170404_1411'),
    ]

    operations = [
        migrations.RunPython(reports_migrations),
    ]
