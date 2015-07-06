# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields.json


class Migration(migrations.Migration):

    dependencies = [
        ('fixmystreet', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebhookConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('resource', models.SlugField(max_length=30, verbose_name='resource')),
                ('hook', models.SlugField(max_length=30, verbose_name='hook')),
                ('action', models.SlugField(max_length=30, verbose_name='action')),
                ('url', models.URLField(verbose_name='URL')),
                ('data', django_extensions.db.fields.json.JSONField(help_text='Extra parameters related to the hook or the endpoint.', verbose_name='data', blank=True)),
                ('third_party', models.ForeignKey(verbose_name='third-party', blank=True, to='fixmystreet.OrganisationEntity')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='webhookconfig',
            unique_together=set([('resource', 'hook', 'action', 'third_party')]),
        ),
        migrations.AlterIndexTogether(
            name='webhookconfig',
            index_together=set([('resource', 'hook', 'action')]),
        ),
    ]
