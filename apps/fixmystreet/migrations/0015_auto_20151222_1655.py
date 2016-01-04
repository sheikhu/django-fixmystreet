# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixmystreet', '0014_auto_20151218_1039'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalorganisationentity',
            name='feature_id',
        ),
        migrations.RemoveField(
            model_name='organisationentity',
            name='feature_id',
        ),
    ]
