# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

import logging, os
logger = logging.getLogger("fixmystreet")


class Migration(migrations.Migration):

    def fix_sub_categories_uniqueness(apps, schema_editor):
        ReportSubCategory = apps.get_model('fixmystreet', 'ReportSubCategory')
        Report = apps.get_model('fixmystreet', 'Report')

        sub_categories = ReportSubCategory.objects.all()

        for sub_category in sub_categories:

            if sub_category.subcategories.count() > 1:
                logger.info('SubCategory duplicated: {}'.format(sub_category.id))

                # Duplicate double subcat
                sub_category_id = sub_category.id

                duplicate_sub_category = sub_category
                duplicate_sub_category.pk = None
                duplicate_sub_category.save()

                sub_category = ReportSubCategory.objects.get(id=sub_category_id)

                # Reassign reportcat with unique sub_category
                first = True
                for category in sub_category.subcategories.all():

                    if first:
                        first = False;

                        logger.info('Category to migrate: {}'.format(category.id, sub_category.id))

                        category.sub_categories.remove(sub_category)
                        category.sub_categories.add(duplicate_sub_category)
                        category.save()
                        # Migrate report according to new subcat.
                        for report in Report.objects.filter(secondary_category=category, sub_category=sub_category):
                            logger.info('Report to migrate: {}'.format(report.id))

                            report.sub_category = duplicate_sub_category
                            report.save()


    dependencies = [
        ('fixmystreet', '0030_auto_20170801_1517'),
    ]

    operations = [
        migrations.RunPython(fix_sub_categories_uniqueness),
    ]
