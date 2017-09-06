# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixmystreet', '0031_auto_20170801_0916'),
    ]

    operations = [
        migrations.AddField(
            model_name='fmsuser',
            name='map_language',
            field=models.CharField(default=b'FR', max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='historicalfmsuser',
            name='map_language',
            field=models.CharField(default=b'FR', max_length=10, null=True),
        ),
    ]
