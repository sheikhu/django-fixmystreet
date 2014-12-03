# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    depends_on = (
        ("fixmystreet", "0059_fmsproxy"),
    )

    def forwards(self, orm):
        # Adding model 'WebhookConfig'
        db.create_table(u'webhooks_webhookconfig', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('resource', self.gf('django.db.models.fields.SlugField')(max_length=30)),
            ('hook', self.gf('django.db.models.fields.SlugField')(max_length=30)),
            ('action', self.gf('django.db.models.fields.SlugField')(max_length=30)),
            ('third_party', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fixmystreet.OrganisationEntity'], blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('data', self.gf('django.db.models.fields.TextField')(default='{}', blank=True)),
        ))
        db.send_create_signal(u'webhooks', ['WebhookConfig'])

        # Adding unique constraint on 'WebhookConfig', fields ['resource', 'hook', 'action', 'third_party']
        db.create_unique(u'webhooks_webhookconfig', ['resource', 'hook', 'action', 'third_party_id'])

        # Adding index on 'WebhookConfig', fields ['resource', 'hook', 'action']
        db.create_index(u'webhooks_webhookconfig', ['resource', 'hook', 'action'])


    def backwards(self, orm):
        # Removing index on 'WebhookConfig', fields ['resource', 'hook', 'action']
        db.delete_index(u'webhooks_webhookconfig', ['resource', 'hook', 'action'])

        # Removing unique constraint on 'WebhookConfig', fields ['resource', 'hook', 'action', 'third_party']
        db.delete_unique(u'webhooks_webhookconfig', ['resource', 'hook', 'action', 'third_party_id'])

        # Deleting model 'WebhookConfig'
        db.delete_table(u'webhooks_webhookconfig')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'default': "'!'", 'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'fixmystreet.fmsuser': {
            'Meta': {'ordering': "['last_name']", 'object_name': 'FMSUser', '_ormbases': [u'auth.User']},
            'agent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'applicant': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'contractor': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fmsuser_created'", 'null': 'True', 'to': u"orm['fixmystreet.FMSUser']"}),
            'last_used_language': ('django.db.models.fields.CharField', [], {'default': "'FR'", 'max_length': '10', 'null': 'True'}),
            'leader': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'logical_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'manager': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fmsuser_modified'", 'null': 'True', 'to': u"orm['fixmystreet.FMSUser']"}),
            'organisation': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'team'", 'null': 'True', 'to': u"orm['fixmystreet.OrganisationEntity']"}),
            'quality': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'telephone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            u'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'fixmystreet.organisationentity': {
            'Meta': {'ordering': "['name_fr']", 'object_name': 'OrganisationEntity'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'organisationentity_created'", 'null': 'True', 'to': u"orm['fixmystreet.FMSUser']"}),
            'dependency': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'associates'", 'null': 'True', 'to': u"orm['fixmystreet.OrganisationEntity']"}),
            'dispatch_categories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'assigned_to_department'", 'blank': 'True', 'to': u"orm['fixmystreet.ReportCategory']"}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'feature_id': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'fmsproxy': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['fmsproxy.FMSProxy']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'organisationentity_modified'", 'null': 'True', 'to': u"orm['fixmystreet.FMSUser']"}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_nl': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'slug_fr': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'slug_nl': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1'})
        },
        u'fixmystreet.reportcategory': {
            'Meta': {'object_name': 'ReportCategory'},
            'category_class': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'categories'", 'to': u"orm['fixmystreet.ReportMainCategoryClass']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reportcategory_created'", 'null': 'True', 'to': u"orm['fixmystreet.FMSUser']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reportcategory_modified'", 'null': 'True', 'to': u"orm['fixmystreet.FMSUser']"}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_nl': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'organisation_communal': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'categories_communal'", 'null': 'True', 'to': u"orm['fixmystreet.OrganisationEntity']"}),
            'organisation_regional': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'categories_regional'", 'null': 'True', 'to': u"orm['fixmystreet.OrganisationEntity']"}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'secondary_category_class': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'categories'", 'to': u"orm['fixmystreet.ReportSecondaryCategoryClass']"}),
            'slug_fr': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'slug_nl': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'fixmystreet.reportcategoryhint': {
            'Meta': {'object_name': 'ReportCategoryHint'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label_fr': ('django.db.models.fields.TextField', [], {}),
            'label_nl': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'fixmystreet.reportmaincategoryclass': {
            'Meta': {'object_name': 'ReportMainCategoryClass'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reportmaincategoryclass_created'", 'null': 'True', 'to': u"orm['fixmystreet.FMSUser']"}),
            'hint': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['fixmystreet.ReportCategoryHint']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reportmaincategoryclass_modified'", 'null': 'True', 'to': u"orm['fixmystreet.FMSUser']"}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_nl': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'slug_fr': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'slug_nl': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'fixmystreet.reportsecondarycategoryclass': {
            'Meta': {'object_name': 'ReportSecondaryCategoryClass'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reportsecondarycategoryclass_created'", 'null': 'True', 'to': u"orm['fixmystreet.FMSUser']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reportsecondarycategoryclass_modified'", 'null': 'True', 'to': u"orm['fixmystreet.FMSUser']"}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_nl': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'slug_fr': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'slug_nl': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'fmsproxy.fmsproxy': {
            'Meta': {'object_name': 'FMSProxy'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '20'})
        },
        u'webhooks.webhookconfig': {
            'Meta': {'unique_together': "(('resource', 'hook', 'action', 'third_party'),)", 'object_name': 'WebhookConfig', 'index_together': "(('resource', 'hook', 'action'),)"},
            'action': ('django.db.models.fields.SlugField', [], {'max_length': '30'}),
            'data': ('django.db.models.fields.TextField', [], {'default': "'{}'", 'blank': 'True'}),
            'hook': ('django.db.models.fields.SlugField', [], {'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'resource': ('django.db.models.fields.SlugField', [], {'max_length': '30'}),
            'third_party': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['fixmystreet.OrganisationEntity']", 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['webhooks']
