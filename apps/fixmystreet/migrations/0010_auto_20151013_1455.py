# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixmystreet', '0009_auto_20151009_1522'),
    ]

    operations = [
        migrations.AddField(
            model_name='reporteventlog',
            name='text',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='reporteventlog',
            name='event_type',
            field=models.IntegerField(choices=[(1, 'Refused'), (2, 'Closed'), (3, 'Marked as Done'), (4, 'Manager assigned'), (6, 'Valid'), (7, 'Organisation assigned'), (9, 'Contractor assigned'), (10, 'Contractor changed'), (11, 'Applicant assigned'), (12, 'Applicant changed'), (14, 'Created'), (15, 'Updated'), (16, 'Update published'), (17, 'Planned'), (18, 'Merged'), (19, 'Reopen'), (20, 'Reopen request'), (21, 'Became private'), (22, 'Became public'), (23, 'PDF was sent by email')]),
        ),
    ]
