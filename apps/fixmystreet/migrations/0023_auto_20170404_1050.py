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
        historical_reports = HistoricalReport.objects.all()

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
        for key in NEW_LVL.keys():
            new_categories = NEW_LVL[key]
            count = reports.filter(secondary_category=key).update(secondary_category=new_categories['LVL_3'], category=new_categories['LVL_1'])

            logger.info("Report - Secondary category / affected  |  %s / %s" %(key, count))

        reports = None

        # HISTORICAL REPORTS MIGRATION
        for key in NEW_LVL.keys():
            new_categories = NEW_LVL[key]
            count = historical_reports.filter(secondary_category=key).update(secondary_category=new_categories['LVL_3'], category=new_categories['LVL_1'])

            logger.info("Historical Report - Secondary category / affected  |  %s / %s" %(key, count))

        historical_reports = None

        # Check that all reports are migrated
        if Report.objects.filter(category__lt=1000).exists() or Report.objects.filter(secondary_category__lt=3000).exists():
            logger.error('Some reports are not migrated')

        # Check that all historical reports are migrated
        if HistoricalReport.objects.filter(category__lt=1000).exists() or HistoricalReport.objects.filter(secondary_category__lt=3000).exists():
            logger.error('Some historical reports are not migrated')


    dependencies = [
        ('fixmystreet', '0022_auto_20170404_1411'),
    ]

    operations = [
        migrations.RunPython(reports_migrations),
    ]
