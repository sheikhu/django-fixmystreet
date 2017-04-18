# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.core.management import call_command
from django.conf import settings

import logging, os
logger = logging.getLogger("fixmystreet")


class Migration(migrations.Migration):

    def import_new_categories(apps, schema_editor):
        if os.environ.get('SKIP_MIGRATIONS', False) or settings.ENVIRONMENT == "jenkins":
            return

        logger.info('Generate new categories from mapping')
        call_command('append_new_categories_tree')

        logger.info('Append new categories')
        call_command('loaddata', 'new_categories_append.json')


    dependencies = [
        ('fixmystreet', '0025_auto_20170412_0924'),
    ]

    operations = [
        migrations.RunPython(import_new_categories),
    ]
