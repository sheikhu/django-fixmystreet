# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixmystreet', '0008_auto_20151007_1159'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalreport',
            name='private_property',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='report',
            name='private_property',
            field=models.BooleanField(default=False),
        ),
    ]
