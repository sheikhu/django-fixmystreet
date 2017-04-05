# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

from ..management.commands.new_category_consts import *
from apps.fixmystreet.models import ReportCategory

import logging, csv
logger = logging.getLogger("fixmystreet")


class Migration(migrations.Migration):

    def copy_dispatching_to_new_categories(apps, schema_editor):
        logger.info('Copy dispatching from old to new categories')

        # Create new dispatching
        with open("apps/fixmystreet/migrations/categories_mapping.csv", 'rb') as mapping_file:
            mapping_reader = csv.reader(mapping_file, delimiter=','.encode('utf-8'), quotechar='"'.encode('utf-8'))

            for row in mapping_reader:
                old_category = ReportCategory.objects.get(id=row[LVL_3_ID_IDX])
                new_category = ReportCategory.objects.get(id=row[NEW_LVL_3_ID_IDX])

                departments  = []
                if old_category.assigned_to_department.all().exists():
                    departments = old_category.assigned_to_department.all()
                else:
                    arbitrary_category = ReportCategory.objects.get(id=29)
                    departments = arbitrary_category.assigned_to_department.all()

                for department in departments:
                    if not new_category.assigned_to_department.filter(dependency=department.dependency).exists():
                        department.dispatch_categories.add(new_category)

        logger.info('Remove old dispatching')

        # Remove old dispatching
        categories = ReportCategory.objects.filter(id__lt=3000)

        for category in categories:
            departments = category.assigned_to_department.all()

            for department in departments:
                department.dispatch_categories.remove(old_category)


    def yo(apps, schema_editor):
        pass

    dependencies = [
        ('fixmystreet', '0021_auto_20170404_1505'),
    ]

    operations = [
        migrations.RunPython(copy_dispatching_to_new_categories, reverse_code=yo),
    ]
