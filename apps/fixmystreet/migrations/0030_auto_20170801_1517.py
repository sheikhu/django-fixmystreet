# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings

from mobileserverstatus.models import Message
import os


class Migration(migrations.Migration):

    def fix_mobileserver_status(apps, schema_editor):
        if os.environ.get('SKIP_MIGRATIONS', False) or settings.ENVIRONMENT == "jenkins":
            return

        message = Message.objects.all()[0]
        message.status = 1
        message.save()


    dependencies = [
        ('fixmystreet', '0029_organisationentity_categories_transfer_restriction'),
    ]

    operations = [
        migrations.RunPython(fix_mobileserver_status),
    ]
