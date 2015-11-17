# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixmystreet', '0012_auto_20151109_1034'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalreport',
            name='contractor_reference_id',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='report',
            name='contractor_reference_id',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
    ]
