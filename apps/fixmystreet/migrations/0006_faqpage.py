# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('fixmystreet', '0005_auto_20150916_1210'),
    ]

    operations = [
        migrations.CreateModel(
            name='FAQPage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title_fr', models.TextField(verbose_name=b'Title')),
                ('title_nl', models.TextField(null=True, verbose_name=b'Title', blank=True)),
                ('content_fr', ckeditor.fields.RichTextField(verbose_name=b'Content')),
                ('content_nl', ckeditor.fields.RichTextField(null=True, verbose_name=b'Content', blank=True)),
                ('visible', models.BooleanField(default=False)),
                ('ranking', models.PositiveIntegerField(blank=True)),
            ],
        ),
    ]
