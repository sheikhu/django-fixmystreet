# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('fixmystreet', '0019_auto_20170316_0848'),
    ]

    operations = [
        migrations.AddField(
            model_name='faqpage',
            name='content_en',
            field=ckeditor.fields.RichTextField(null=True, verbose_name=b'Content', blank=True),
        ),
        migrations.AddField(
            model_name='faqpage',
            name='title_en',
            field=models.TextField(null=True, verbose_name=b'Title', blank=True),
        ),
        migrations.AddField(
            model_name='historicalorganisationentity',
            name='name_en',
            field=models.CharField(max_length=100, null=True, verbose_name='Name', blank=True),
        ),
        migrations.AddField(
            model_name='historicalorganisationentity',
            name='slug_en',
            field=models.SlugField(max_length=100, null=True, verbose_name='Slug', blank=True),
        ),
        migrations.AddField(
            model_name='historicalpage',
            name='content_en',
            field=ckeditor.fields.RichTextField(null=True, verbose_name=b'Content', blank=True),
        ),
        migrations.AddField(
            model_name='historicalpage',
            name='slug_en',
            field=models.CharField(max_length=100, null=True, verbose_name=b'Slug', blank=True),
        ),
        migrations.AddField(
            model_name='historicalpage',
            name='title_en',
            field=models.CharField(max_length=100, null=True, verbose_name=b'Title', blank=True),
        ),
        migrations.AddField(
            model_name='historicalreport',
            name='address_en',
            field=models.CharField(max_length=255, null=True, verbose_name='Location', blank=True),
        ),
        migrations.AddField(
            model_name='listitem',
            name='label_en',
            field=models.CharField(max_length=100, null=True, verbose_name='Label', blank=True),
        ),
        migrations.AddField(
            model_name='organisationentity',
            name='name_en',
            field=models.CharField(max_length=100, null=True, verbose_name='Name', blank=True),
        ),
        migrations.AddField(
            model_name='organisationentity',
            name='slug_en',
            field=models.SlugField(max_length=100, null=True, verbose_name='Slug', blank=True),
        ),
        migrations.AddField(
            model_name='page',
            name='content_en',
            field=ckeditor.fields.RichTextField(null=True, verbose_name=b'Content', blank=True),
        ),
        migrations.AddField(
            model_name='page',
            name='slug_en',
            field=models.CharField(max_length=100, null=True, verbose_name=b'Slug', blank=True),
        ),
        migrations.AddField(
            model_name='page',
            name='title_en',
            field=models.CharField(max_length=100, null=True, verbose_name=b'Title', blank=True),
        ),
        migrations.AddField(
            model_name='report',
            name='address_en',
            field=models.CharField(max_length=255, null=True, verbose_name='Location', blank=True),
        ),
        migrations.AddField(
            model_name='reportcategory',
            name='name_en',
            field=models.CharField(max_length=100, null=True, verbose_name='Name', blank=True),
        ),
        migrations.AddField(
            model_name='reportcategory',
            name='slug_en',
            field=models.SlugField(max_length=100, null=True, verbose_name='Slug', blank=True),
        ),
        migrations.AddField(
            model_name='reportcategoryhint',
            name='label_en',
            field=models.TextField(null=True, verbose_name='Label', blank=True),
        ),
        migrations.AddField(
            model_name='reportmaincategoryclass',
            name='name_en',
            field=models.CharField(max_length=100, null=True, verbose_name='Name', blank=True),
        ),
        migrations.AddField(
            model_name='reportmaincategoryclass',
            name='slug_en',
            field=models.SlugField(max_length=100, null=True, verbose_name='Slug', blank=True),
        ),
        migrations.AddField(
            model_name='reportsecondarycategoryclass',
            name='name_en',
            field=models.CharField(max_length=100, null=True, verbose_name='Name', blank=True),
        ),
        migrations.AddField(
            model_name='reportsecondarycategoryclass',
            name='slug_en',
            field=models.SlugField(max_length=100, null=True, verbose_name='Slug', blank=True),
        ),
        migrations.AddField(
            model_name='reportsubcategory',
            name='name_en',
            field=models.CharField(max_length=100, null=True, verbose_name='Name', blank=True),
        ),
        migrations.AddField(
            model_name='reportsubcategory',
            name='slug_en',
            field=models.SlugField(max_length=100, null=True, verbose_name='Slug', blank=True),
        ),
        migrations.AddField(
            model_name='zipcode',
            name='name_en',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]
