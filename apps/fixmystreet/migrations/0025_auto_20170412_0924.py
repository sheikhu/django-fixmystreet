# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    def increment_mobile_version(apps, schema_editor):
        MobileServerStatus = apps.get_model("mobileserverstatus", "Message")
        message = MobileServerStatus.objects.all()[0]
        message.version = 2
        message.save()

    dependencies = [
        ('fixmystreet', '0024_auto_20170404_1313'),
    ]

    operations = [
        migrations.RunPython(increment_mobile_version),
    ]
