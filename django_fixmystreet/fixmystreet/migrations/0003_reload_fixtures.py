# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration
from django.core.management import call_command


class Migration(SchemaMigration):

    def forwards(self, orm):
        #~ call_command("loaddata", "bootstrap.json")
        #~ db.execute("""
            #~ UPDATE fixmystreet_organisationentity o
                #~ SET active = true
                    #~ WHERE exists (
                        #~ SELECT * FROM fixmystreet_fmsuser
                        #~ WHERE manager=true AND organisation_id=o.id
                    #~ );
        #~ """)

        # On a des problèmes : à cause du loaddata qui créée des oragnisationentity. Un champ email est défini dans le model, mais pas encore créée en DB à ce niveau de la procédure de south.
        pass
    def backwards(self, orm):
        pass

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'fixmystreet.faqentry': {
            'Meta': {'ordering': "['order']", 'object_name': 'FaqEntry'},
            'a_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'a_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'a_nl': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'q_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'q_fr': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'q_nl': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        'fixmystreet.fmsuser': {
            'Meta': {'object_name': 'FMSUser', '_ormbases': ['auth.User']},
            'agent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'applicant': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'type'", 'blank': 'True', 'to': "orm['fixmystreet.ReportCategory']"}),
            'contractor': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fmsuser_created'", 'null': 'True', 'to': "orm['fixmystreet.FMSUser']"}),
            'last_used_language': ('django.db.models.fields.CharField', [], {'default': "'FR'", 'max_length': '10', 'null': 'True'}),
            'leader': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'logical_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'manager': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fmsuser_modified'", 'null': 'True', 'to': "orm['fixmystreet.FMSUser']"}),
            'organisation': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'team'", 'null': 'True', 'to': "orm['fixmystreet.OrganisationEntity']"}),
            'quality': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'telephone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'}),
            'work_for': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'workers'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['fixmystreet.OrganisationEntity']"})
        },
        'fixmystreet.historicalfmsuser': {
            'Meta': {'ordering': "('-history_date', '-history_id')", 'object_name': 'HistoricalFMSUser'},
            'agent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'applicant': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'contractor': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'created_by_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'db_index': 'True', 'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'history_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'history_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'history_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'history_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'last_used_language': ('django.db.models.fields.CharField', [], {'default': "'FR'", 'max_length': '10', 'null': 'True'}),
            'leader': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'logical_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'manager': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'modified_by_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'organisation_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'quality': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'telephone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'user_ptr_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '75', 'db_index': 'True'})
        },
        'fixmystreet.historicalorganisationentity': {
            'Meta': {'ordering': "('-history_date', '-history_id')", 'object_name': 'HistoricalOrganisationEntity'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'applicant': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'commune': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'created_by_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'dependency_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'feature_id': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'history_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'history_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'history_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'history_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'modified_by_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_nl': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'region': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug_en': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'slug_fr': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'slug_nl': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'subcontractor': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'fixmystreet.historicalreport': {
            'Meta': {'ordering': "('-history_date', '-history_id')", 'object_name': 'HistoricalReport'},
            'address_en': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'address_fr': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'address_nl': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'address_number': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'address_number_as_int': ('django.db.models.fields.IntegerField', [], {'max_length': '255'}),
            'address_regional': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'category_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'citizen_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'close_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'contractor_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'created_by_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'fixed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'hash_code': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'history_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'history_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'history_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'history_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'mark_as_done_motivation': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'modified_by_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'photo': ('django.db.models.fields.TextField', [], {'max_length': '100', 'blank': 'True'}),
            'point': ('django.contrib.gis.db.models.fields.PointField', [], {'srid': '31370', 'null': 'True', 'blank': 'True'}),
            'postalcode': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'private': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'quality': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'refusal_motivation': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'responsible_entity_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'responsible_manager_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'responsible_manager_validated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'secondary_category_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'fixmystreet.listitem': {
            'Meta': {'object_name': 'ListItem'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'label_fr': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'label_nl': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'model_class': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'model_field': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'fixmystreet.organisationentity': {
            'Meta': {'object_name': 'OrganisationEntity'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'applicant': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'commune': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'organisationentity_created'", 'null': 'True', 'to': "orm['fixmystreet.FMSUser']"}),
            'dependency': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'associates'", 'null': 'True', 'to': "orm['fixmystreet.OrganisationEntity']"}),
            'feature_id': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'organisationentity_modified'", 'null': 'True', 'to': "orm['fixmystreet.FMSUser']"}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_nl': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'region': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug_en': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'slug_fr': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'slug_nl': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'subcontractor': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'fixmystreet.report': {
            'Meta': {'object_name': 'Report'},
            'address_en': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'address_fr': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'address_nl': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'address_number': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'address_number_as_int': ('django.db.models.fields.IntegerField', [], {'max_length': '255'}),
            'address_regional': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fixmystreet.ReportMainCategoryClass']", 'null': 'True', 'blank': 'True'}),
            'citizen': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'citizen_reports'", 'null': 'True', 'to': "orm['fixmystreet.FMSUser']"}),
            'close_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'contractor': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assigned_reports'", 'null': 'True', 'to': "orm['fixmystreet.OrganisationEntity']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'report_created'", 'null': 'True', 'to': "orm['fixmystreet.FMSUser']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'fixed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'hash_code': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mark_as_done_motivation': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'report_modified'", 'null': 'True', 'to': "orm['fixmystreet.FMSUser']"}),
            'photo': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'point': ('django.contrib.gis.db.models.fields.PointField', [], {'srid': '31370', 'null': 'True', 'blank': 'True'}),
            'postalcode': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'private': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'quality': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'refusal_motivation': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'responsible_entity': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'reports_in_charge'", 'null': 'True', 'to': "orm['fixmystreet.OrganisationEntity']"}),
            'responsible_manager': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'reports_in_charge'", 'null': 'True', 'to': "orm['fixmystreet.FMSUser']"}),
            'responsible_manager_validated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'secondary_category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fixmystreet.ReportCategory']", 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'fixmystreet.reportattachment': {
            'Meta': {'object_name': 'ReportAttachment'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reportattachment_created'", 'null': 'True', 'to': "orm['fixmystreet.FMSUser']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logical_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reportattachment_modified'", 'null': 'True', 'to': "orm['fixmystreet.FMSUser']"}),
            'report': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attachments'", 'to': "orm['fixmystreet.Report']"}),
            'security_level': ('django.db.models.fields.IntegerField', [], {'default': '2'})
        },
        'fixmystreet.reportcategory': {
            'Meta': {'object_name': 'ReportCategory'},
            'category_class': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'categories'", 'to': "orm['fixmystreet.ReportMainCategoryClass']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reportcategory_created'", 'null': 'True', 'to': "orm['fixmystreet.FMSUser']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reportcategory_modified'", 'null': 'True', 'to': "orm['fixmystreet.FMSUser']"}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_nl': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'secondary_category_class': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'categories'", 'to': "orm['fixmystreet.ReportSecondaryCategoryClass']"}),
            'slug_en': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'slug_fr': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'slug_nl': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'fixmystreet.reportcategoryhint': {
            'Meta': {'object_name': 'ReportCategoryHint'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'label_fr': ('django.db.models.fields.TextField', [], {}),
            'label_nl': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'fixmystreet.reportcomment': {
            'Meta': {'object_name': 'ReportComment', '_ormbases': ['fixmystreet.ReportAttachment']},
            'reportattachment_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['fixmystreet.ReportAttachment']", 'unique': 'True', 'primary_key': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        'fixmystreet.reporteventlog': {
            'Meta': {'object_name': 'ReportEventLog'},
            'event_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'event_type': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organisation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'activities'", 'to': "orm['fixmystreet.OrganisationEntity']"}),
            'related_content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True'}),
            'related_new_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'related_old_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'report': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'activities'", 'to': "orm['fixmystreet.Report']"}),
            'status_new': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'status_old': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'activities'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'fixmystreet.reportfile': {
            'Meta': {'object_name': 'ReportFile', '_ormbases': ['fixmystreet.ReportAttachment']},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'file_creation_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'file_type': ('django.db.models.fields.IntegerField', [], {}),
            'image': ('django_fixmystreet.fixmystreet.utils.FixStdImageField', [], {'max_length': '100', 'name': "'image'", 'blank': 'True'}),
            'reportattachment_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['fixmystreet.ReportAttachment']", 'unique': 'True', 'primary_key': 'True'}),
            'title': ('django.db.models.fields.TextField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'})
        },
        'fixmystreet.reportmaincategoryclass': {
            'Meta': {'object_name': 'ReportMainCategoryClass'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reportmaincategoryclass_created'", 'null': 'True', 'to': "orm['fixmystreet.FMSUser']"}),
            'hint': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fixmystreet.ReportCategoryHint']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reportmaincategoryclass_modified'", 'null': 'True', 'to': "orm['fixmystreet.FMSUser']"}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_nl': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'slug_en': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'slug_fr': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'slug_nl': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'fixmystreet.reportnotification': {
            'Meta': {'object_name': 'ReportNotification'},
            'content_template': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'error_msg': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'notifications'", 'to': "orm['fixmystreet.FMSUser']"}),
            'related_content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'related_object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'reply_to': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'sent_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'success': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'fixmystreet.reportsecondarycategoryclass': {
            'Meta': {'object_name': 'ReportSecondaryCategoryClass'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reportsecondarycategoryclass_created'", 'null': 'True', 'to': "orm['fixmystreet.FMSUser']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reportsecondarycategoryclass_modified'", 'null': 'True', 'to': "orm['fixmystreet.FMSUser']"}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_nl': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'slug_en': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'slug_fr': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'slug_nl': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'fixmystreet.reportsubscription': {
            'Meta': {'unique_together': "(('report', 'subscriber'),)", 'object_name': 'ReportSubscription'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'report': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subscriptions'", 'to': "orm['fixmystreet.Report']"}),
            'subscriber': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fixmystreet.FMSUser']"})
        },
        'fixmystreet.zipcode': {
            'Meta': {'object_name': 'ZipCode'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'commune': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fixmystreet.OrganisationEntity']"}),
            'hide': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_nl': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['fixmystreet']
