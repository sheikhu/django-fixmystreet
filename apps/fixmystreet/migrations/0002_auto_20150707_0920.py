# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fixmystreet', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupmailconfig',
            name='group',
            field=models.OneToOneField(to='fixmystreet.OrganisationEntity'),
        ),
        migrations.AlterField(
            model_name='historicalreport',
            name='address_number_as_int',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='report',
            name='address_number_as_int',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='report',
            name='previous_managers',
            field=models.ManyToManyField(related_name='previous_reports', to='fixmystreet.FMSUser', blank=True),
        ),
    ]
