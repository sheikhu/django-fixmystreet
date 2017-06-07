# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.core.management import call_command
from django.conf import settings

import logging, os
logger = logging.getLogger("fixmystreet")


class Migration(migrations.Migration):

    def import_abp_categories(apps, schema_editor):
        if os.environ.get('SKIP_MIGRATIONS', False) or settings.ENVIRONMENT == "jenkins":
            return

        logger.info('Import abp categories')
        call_command('loaddata', 'apps/fixmystreet/migrations/abp_categories.json')

    dependencies = [
        ('fixmystreet', '0020_auto_20170607_1057'),
    ]

    operations = [
        migrations.RunPython(import_abp_categories),
    ]
