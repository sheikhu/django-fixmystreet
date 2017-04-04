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

        with open("apps/resources/categories_mapping.csv", 'rb') as mapping_file:
            mapping_reader = csv.reader(mapping_file, delimiter=','.encode('utf-8'), quotechar='"'.encode('utf-8'))

            for row in mapping_reader:
                old_category = ReportCategory.objects.get(id=row[LVL_3_ID_IDX])
                new_category = ReportCategory.objects.get(id=row[NEW_LVL_3_ID_IDX])

                for department in old_category.assigned_to_department.all():
                    department.dispatch_categories.remove(old_category)

                    if not new_category.assigned_to_department.filter(dependency=department.dependency).exists():
                        department.dispatch_categories.add(new_category)


    dependencies = [
        ('fixmystreet', '0019_auto_20170316_0848'),
    ]

    operations = [
        migrations.RunPython(copy_dispatching_to_new_categories),
    ]
