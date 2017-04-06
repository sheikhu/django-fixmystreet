# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.core.management import call_command

import logging, csv, os
logger = logging.getLogger("fixmystreet")


class Migration(migrations.Migration):

    def import_new_categories(apps, schema_editor):
        if os.environ.get('SKIP_MIGRATIONS', False):
            return

        logger.info('Generate new categories from mapping')
        call_command('generate_new_categories_tree')

        logger.info('Import new categories')
        call_command('loaddata', 'apps/fixmystreet/migrations/new_categories.json')

    dependencies = [
        ('fixmystreet', '0020_auto_20170405_1600'),
    ]

    operations = [
        migrations.RunPython(import_new_categories),
    ]
