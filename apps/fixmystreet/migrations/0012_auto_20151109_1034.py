# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixmystreet', '0011_auto_20151109_1024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalorganisationentity',
            name='created',
            field=models.DateTimeField(verbose_name='created', null=True, editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='historicalorganisationentity',
            name='modified',
            field=models.DateTimeField(verbose_name='modified', null=True, editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='historicalreport',
            name='created',
            field=models.DateTimeField(verbose_name='created', null=True, editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='historicalreport',
            name='modified',
            field=models.DateTimeField(verbose_name='modified', null=True, editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='organisationentity',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created', null=True),
        ),
        migrations.AlterField(
            model_name='organisationentity',
            name='modified',
            field=models.DateTimeField(auto_now=True, verbose_name='modified', null=True),
        ),
        migrations.AlterField(
            model_name='report',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created', null=True),
        ),
        migrations.AlterField(
            model_name='report',
            name='modified',
            field=models.DateTimeField(auto_now=True, verbose_name='modified', null=True),
        ),
        migrations.AlterField(
            model_name='reportattachment',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created', null=True),
        ),
        migrations.AlterField(
            model_name='reportattachment',
            name='modified',
            field=models.DateTimeField(auto_now=True, verbose_name='modified', null=True),
        ),
        migrations.AlterField(
            model_name='reportcategory',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created', null=True),
        ),
        migrations.AlterField(
            model_name='reportcategory',
            name='modified',
            field=models.DateTimeField(auto_now=True, verbose_name='modified', null=True),
        ),
        migrations.AlterField(
            model_name='reportmaincategoryclass',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created', null=True),
        ),
        migrations.AlterField(
            model_name='reportmaincategoryclass',
            name='modified',
            field=models.DateTimeField(auto_now=True, verbose_name='modified', null=True),
        ),
        migrations.AlterField(
            model_name='reportsecondarycategoryclass',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created', null=True),
        ),
        migrations.AlterField(
            model_name='reportsecondarycategoryclass',
            name='modified',
            field=models.DateTimeField(auto_now=True, verbose_name='modified', null=True),
        ),
        migrations.AlterField(
            model_name='userorganisationmembership',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created', null=True),
        ),
        migrations.AlterField(
            model_name='userorganisationmembership',
            name='modified',
            field=models.DateTimeField(auto_now=True, verbose_name='modified', null=True),
        ),
    ]
