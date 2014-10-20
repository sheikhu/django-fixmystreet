# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.utils.text import slugify


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'FMSProxy', fields ['name']
        db.delete_unique(u'fmsproxy_fmsproxy', ['name'])

        # Adding field 'FMSProxy.slug'
        db.add_column(u'fmsproxy_fmsproxy', 'slug',
                      self.gf('django.db.models.fields.SlugField')(default='', max_length=20, unique=False),
                      keep_default=False)
        for row in orm['fmsproxy.fmsproxy'].objects.all():
            row.slug = slugify(row.name)
            row.save()
        db.create_unique(u'fmsproxy_fmsproxy', ['slug'])


    def backwards(self, orm):
        # Deleting field 'FMSProxy.slug'
        db.delete_column(u'fmsproxy_fmsproxy', 'slug')

        # Adding unique constraint on 'FMSProxy', fields ['name']
        db.create_unique(u'fmsproxy_fmsproxy', ['name'])


    models = {
        u'fmsproxy.fmsproxy': {
            'Meta': {'object_name': 'FMSProxy'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['fmsproxy']