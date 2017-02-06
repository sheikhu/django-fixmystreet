# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixmystreet', '0017_auto_20161018_1152'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalreport',
            name='duplicates',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='report',
            name='duplicates',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='reportcategory',
            name='sub_categories',
            field=models.ManyToManyField(related_name='subcategories', to='fixmystreet.ReportSubCategory', blank=True),
        ),
    ]
