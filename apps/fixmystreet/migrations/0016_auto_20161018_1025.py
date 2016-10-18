# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixmystreet', '0015_auto_20151222_1655'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportSubCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created', null=True)),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='modified', null=True)),
                ('name_fr', models.CharField(max_length=100, verbose_name='Name')),
                ('name_nl', models.CharField(max_length=100, null=True, verbose_name='Name', blank=True)),
                ('slug_fr', models.SlugField(max_length=100, verbose_name='Slug')),
                ('slug_nl', models.SlugField(max_length=100, null=True, verbose_name='Slug', blank=True)),
                ('created_by', models.ForeignKey(related_name='reportsubcategory_created', editable=False, to='fixmystreet.FMSUser', null=True)),
                ('modified_by', models.ForeignKey(related_name='reportsubcategory_modified', editable=False, to='fixmystreet.FMSUser', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='reportcategory',
            name='sub_categories',
            field=models.ManyToManyField(related_name='subcategories', to='fixmystreet.ReportSubCategory'),
        ),
    ]
