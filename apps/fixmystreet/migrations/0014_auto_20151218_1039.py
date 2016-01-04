# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixmystreet', '0013_auto_20151117_1026'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalreport',
            name='quality',
        ),
        migrations.RemoveField(
            model_name='report',
            name='quality',
        ),
        migrations.AlterField(
            model_name='fmsuser',
            name='organisation',
            field=models.ForeignKey(related_name='users', verbose_name='Entity', blank=True, to='fixmystreet.OrganisationEntity', null=True),
        ),
        migrations.AlterField(
            model_name='reporteventlog',
            name='event_type',
            field=models.IntegerField(choices=[(1, 'Refused'), (2, 'Closed'), (3, 'Marked as Done'), (4, 'Manager assigned'), (6, 'Valid'), (7, 'Organisation assigned'), (9, 'Contractor assigned'), (10, 'Contractor changed'), (11, 'Applicant assigned'), (12, 'Applicant changed'), (14, 'Created'), (15, 'Updated'), (16, 'Update published'), (17, 'Planned'), (18, 'Merged'), (19, 'Reopen'), (20, 'Reopen request'), (21, 'Became private'), (22, 'Became public'), (23, 'PDF was sent by email'), (24, 'A comment was deleted'), (25, 'A picture or document was deleted'), (26, "The value of the 'third party responsibility' flag was changed"), (27, "The value of the 'private property flag' was changed")]),
        ),
    ]
