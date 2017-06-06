# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixmystreet', '0018_auto_20170206_1056'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalreport',
            name='several_occurences',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='report',
            name='several_occurences',
            field=models.BooleanField(default=False),
        ),
    ]
