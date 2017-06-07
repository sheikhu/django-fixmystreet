# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings

import os


class Migration(migrations.Migration):

    def increment_mobile_version(apps, schema_editor):
        if os.environ.get('SKIP_MIGRATIONS', False) or settings.ENVIRONMENT == "jenkins":
            return

        MobileServerStatus = apps.get_model("mobileserverstatus", "Message")
        message = MobileServerStatus.objects.all()[0]
        message.version = 2
        message.save()

    dependencies = [
        ('fixmystreet', '0025_auto_20170404_1313'),
    ]

    operations = [
        migrations.RunPython(increment_mobile_version),
    ]
