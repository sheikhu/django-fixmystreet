# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings

import os

class Migration(migrations.Migration):

    def fix_map_language(apps, schema_editor):
        if os.environ.get('SKIP_MIGRATIONS', False) or settings.ENVIRONMENT == "jenkins":
            return

        FMSUser = apps.get_model('fixmystreet', 'FMSUser')

        for user in FMSUser.objects.all():
            user.map_language = user.last_used_language
            user.save()


    dependencies = [
        ('fixmystreet', '0032_auto_20170905_1416'),
    ]

    operations = [
        migrations.RunPython(fix_map_language),
    ]
