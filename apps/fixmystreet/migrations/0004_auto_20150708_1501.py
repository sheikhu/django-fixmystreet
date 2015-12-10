# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fixmystreet', '0003_auto_20150708_1409'),
    ]

    operations = [
        migrations.DeleteModel(
            name='MailNotificationTemplate',
        ),
    ]
