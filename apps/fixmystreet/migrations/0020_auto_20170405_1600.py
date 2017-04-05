# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.core.management import call_command

import logging
logger = logging.getLogger("fixmystreet")


class Migration(migrations.Migration):

    def import_abp_categories(apps, schema_editor):
        logger.info('Import abp categories')
        call_command('loaddata', 'apps/fixmystreet/migrations/abp_categories.json')

    dependencies = [
        ('fixmystreet', '0019_auto_20170316_0848'),
    ]

    operations = [
        migrations.RunPython(import_abp_categories),
    ]
