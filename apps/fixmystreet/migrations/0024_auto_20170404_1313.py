# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings

import logging, os
logger = logging.getLogger("fixmystreet")


class Migration(migrations.Migration):

    def delete_old_categories(apps, schema_editor):
        if os.environ.get('SKIP_MIGRATIONS', False) or settings.ENVIRONMENT == "jenkins":
            return

        logger.info('Delete old categories')

        Category_LVL_1 = apps.get_model("fixmystreet", "ReportMainCategoryClass")
        Category_LVL_2 = apps.get_model("fixmystreet", "ReportSecondaryCategoryClass")
        Category_LVL_3 = apps.get_model("fixmystreet", "ReportCategory")
        Category_LVL_4 = apps.get_model("fixmystreet", "ReportSubCategory")

        Category_LVL_1.objects.filter(id__lt=1000).delete()
        Category_LVL_2.objects.filter(id__lt=2000).delete()
        Category_LVL_3.objects.filter(id__lt=3000).delete()
        Category_LVL_4.objects.filter(id__lt=4000).delete()

    dependencies = [
        ('fixmystreet', '0023_auto_20170404_1050'),
    ]

    operations = [
        migrations.RunPython(delete_old_categories),
    ]
