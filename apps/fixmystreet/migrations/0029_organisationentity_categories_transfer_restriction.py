# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixmystreet', '0028_auto_20170418_1119'),
    ]

    operations = [
        migrations.AddField(
            model_name='organisationentity',
            name='categories_transfer_restriction',
            field=models.ManyToManyField(related_name='transferred_by', to='fixmystreet.ReportCategory', blank=True),
        ),
    ]
