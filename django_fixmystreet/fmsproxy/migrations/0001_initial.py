# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FMSProxy'
        db.create_table(u'fmsproxy_fmsproxy', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=20)),
        ))
        db.send_create_signal(u'fmsproxy', ['FMSProxy'])


    def backwards(self, orm):
        # Deleting model 'FMSProxy'
        db.delete_table(u'fmsproxy_fmsproxy')


    models = {
        u'fmsproxy.fmsproxy': {
            'Meta': {'object_name': 'FMSProxy'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'})
        }
    }

    complete_apps = ['fmsproxy']