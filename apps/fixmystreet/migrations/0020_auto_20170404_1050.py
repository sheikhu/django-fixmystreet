# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

import logging, csv

from ..management.commands.new_category_consts import *

logger = logging.getLogger("fixmystreet")

class Migration(migrations.Migration):

    def reports_migrations(apps, schema_editor):
        Report = apps.get_model("fixmystreet", "Report")
        Category_LVL_1 = apps.get_model("fixmystreet", "ReportMainCategoryClass")
        Category_LVL_2 = apps.get_model("fixmystreet", "ReportSecondaryCategoryClass")
        Category_LVL_3 = apps.get_model("fixmystreet", "ReportCategory")

        reports = Report.objects.all()

        # CATEGORIES MAPPING
        NEW_LVL = {}
        with open("apps/resources/categories_mapping.csv", 'rb') as mapping_file:
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

            logger.info("%.2f%%  -  %s  %s  %s" % (progression, report.id, report.category.id, report.secondary_category.id))

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

        logger.info('\nLVL3 ERRORS')
        logger.info('===========')
        logger.info(LVL_3_ERRORS)


    dependencies = [
        ('fixmystreet', '0019_auto_20170316_0848'),
    ]

    operations = [
        migrations.RunPython(reports_migrations),
    ]
