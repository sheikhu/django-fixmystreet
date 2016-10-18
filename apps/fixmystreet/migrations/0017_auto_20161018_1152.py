# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fixmystreet', '0016_auto_20161018_1025'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalreport',
            name='sub_category',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='fixmystreet.ReportSubCategory', null=True),
        ),
        migrations.AddField(
            model_name='report',
            name='sub_category',
            field=models.ForeignKey(verbose_name='SubCategory', blank=True, to='fixmystreet.ReportSubCategory', null=True),
        ),
    ]
