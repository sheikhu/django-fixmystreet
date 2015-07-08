# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fixmystreet', '0002_auto_20150707_0920'),
    ]

    # Hack to force null=True
    operations = [
        migrations.AlterField(
            model_name='historicalfmsuser',
            name='last_login',
            field=models.DateTimeField(null=False, blank=False),
        ),
        migrations.AlterField(
            model_name='historicalfmsuser',
            name='last_login',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
