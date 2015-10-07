# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixmystreet', '0007_auto_20150928_1017'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='reportsecondarycategoryclass',
            options={'verbose_name': 'secondary category group', 'verbose_name_plural': 'secondary category groups'},
        ),
    ]
