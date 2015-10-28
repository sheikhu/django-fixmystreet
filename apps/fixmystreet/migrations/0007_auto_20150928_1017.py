# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from django.conf import settings

from apps.fixmystreet.models import OrganisationEntity as OrganisationEntityModel
from apps.fixmystreet.models import Report



def migrate_osiris_entity(apps, schema_editor):
    if settings.ENVIRONMENT == "jenkins":
        return

    OrganisationEntity = apps.get_model("fixmystreet", "OrganisationEntity")
    ReportCategory     = apps.get_model("fixmystreet", "ReportCategory")

    try:
        # Change type of osiris
        osiris = OrganisationEntity.objects.get(name_fr__iexact="osiris")
        osiris.type = OrganisationEntityModel.REGION
        osiris.save()

        # Fix dispatching of osiris group
        osiris_group = osiris.associates.all()[0]

        for category in ReportCategory.objects.all():
            osiris_group.dispatch_categories.add(category)
    except:
        pass

def migrate_reports(apps, schema_editor):
    if settings.ENVIRONMENT == "jenkins":
        return

    osiris = OrganisationEntityModel.objects.get(name_fr__iexact="osiris")
    osiris_group = osiris.associates.all()[0]

    reports_osiris = Report.objects.filter(contractor=osiris)

    for report in reports_osiris:
        report.contractor = None
        report.responsible_entity = osiris
        report.responsible_department = osiris_group
        report.status = Report.MANAGER_ASSIGNED
        report.save()



class Migration(migrations.Migration):

    dependencies = [
        ('fixmystreet', '0006_faqpage'),
    ]

    operations = [
        # Migrations irrelevant. We keep assignment and OSIRIS as "impétrant".

        #~ migrations.RunPython(migrate_osiris_entity),
        #~ migrations.RunPython(migrate_reports),
    ]
