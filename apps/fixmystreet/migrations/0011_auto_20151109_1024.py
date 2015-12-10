# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixmystreet', '0010_auto_20151013_1455'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalorganisationentity',
            name='created',
            field=models.DateTimeField(verbose_name='created', editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='historicalorganisationentity',
            name='modified',
            field=models.DateTimeField(verbose_name='modified', editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='historicalreport',
            name='created',
            field=models.DateTimeField(verbose_name='created', editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='historicalreport',
            name='modified',
            field=models.DateTimeField(verbose_name='modified', editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='organisationentity',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created'),
        ),
        migrations.AlterField(
            model_name='organisationentity',
            name='modified',
            field=models.DateTimeField(auto_now=True, verbose_name='modified'),
        ),
        migrations.AlterField(
            model_name='report',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created'),
        ),
        migrations.AlterField(
            model_name='report',
            name='modified',
            field=models.DateTimeField(auto_now=True, verbose_name='modified'),
        ),
        migrations.AlterField(
            model_name='reportattachment',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created'),
        ),
        migrations.AlterField(
            model_name='reportattachment',
            name='modified',
            field=models.DateTimeField(auto_now=True, verbose_name='modified'),
        ),
        migrations.AlterField(
            model_name='reportcategory',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created'),
        ),
        migrations.AlterField(
            model_name='reportcategory',
            name='modified',
            field=models.DateTimeField(auto_now=True, verbose_name='modified'),
        ),
        migrations.AlterField(
            model_name='reporteventlog',
            name='event_type',
            field=models.IntegerField(choices=[(1, 'Refused'), (2, 'Closed'), (3, 'Marked as Done'), (4, 'Manager assigned'), (6, 'Valid'), (7, 'Organisation assigned'), (9, 'Contractor assigned'), (10, 'Contractor changed'), (11, 'Applicant assigned'), (12, 'Applicant changed'), (14, 'Created'), (15, 'Updated'), (16, 'Update published'), (17, 'Planned'), (18, 'Merged'), (19, 'Reopen'), (20, 'Reopen request'), (21, 'Became private'), (22, 'Became public'), (23, 'PDF was sent by email'), (24, 'A comment was deleted'), (25, 'A picture or document was deleted')]),
        ),
        migrations.AlterField(
            model_name='reportmaincategoryclass',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created'),
        ),
        migrations.AlterField(
            model_name='reportmaincategoryclass',
            name='modified',
            field=models.DateTimeField(auto_now=True, verbose_name='modified'),
        ),
        migrations.AlterField(
            model_name='reportsecondarycategoryclass',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created'),
        ),
        migrations.AlterField(
            model_name='reportsecondarycategoryclass',
            name='modified',
            field=models.DateTimeField(auto_now=True, verbose_name='modified'),
        ),
        migrations.AlterField(
            model_name='userorganisationmembership',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created'),
        ),
        migrations.AlterField(
            model_name='userorganisationmembership',
            name='modified',
            field=models.DateTimeField(auto_now=True, verbose_name='modified'),
        ),
    ]
