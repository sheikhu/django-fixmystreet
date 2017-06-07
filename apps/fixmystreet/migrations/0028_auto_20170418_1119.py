# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings

from apps.fixmystreet.models import OrganisationEntity, ReportCategory

import logging, os
logger = logging.getLogger("fixmystreet")

class Migration(migrations.Migration):

    def fix_dispatching_by_looking_similar_categories(apps, schema_editor):
        if os.environ.get('SKIP_MIGRATIONS', False) or settings.ENVIRONMENT == "jenkins":
            return

        # Check and fix missing dispatching
        categories = ReportCategory.objects.filter(id__gte=3000)
        entities = OrganisationEntity.objects.filter(type__in=[OrganisationEntity.REGION, OrganisationEntity.COMMUNE])

        for category in categories:
            for entity in entities:
                # Do not associate more than 1 group from the same entity to the same category
                if not category.assigned_to_department.filter(dependency=entity).exists():
                    logger.info('-- Missing dispatching: %s - %s' % (category.id, entity.id))

                    # Find a pertinent department by looking at similar categories (same first level)
                    for inner_category in category.category_class.categories.all():
                        if inner_category.assigned_to_department.filter(dependency=entity).exists():
                            # Assign to dispatching
                            logger.info('---- Fix dispatching')
                            department = inner_category.assigned_to_department.filter(dependency=entity)[0]
                            department.dispatch_categories.add(category)
                            break


    def fix_dispatching_force(apps, schema_editor):
        if os.environ.get('SKIP_MIGRATIONS', False) or settings.ENVIRONMENT == "jenkins":
            return

        # Check and fix missing dispatching
        categories = ReportCategory.objects.filter(id__gte=3000)
        arbitrary_category = ReportCategory.objects.get(id=3314)
        departments = arbitrary_category.assigned_to_department.all()

        for category in categories:
            for department in departments:
                # Do not associate more than 1 group from the same entity to the same category
                if not category.assigned_to_department.filter(dependency=department.dependency).exists():
                    logger.info('-- Force fix dispatching: %s - %s' % (category.id, department.id))
                    department.dispatch_categories.add(category)



    dependencies = [
        ('fixmystreet', '0027_auto_20170418_1151'),
    ]

    operations = [
        migrations.RunPython(fix_dispatching_by_looking_similar_categories),
        migrations.RunPython(fix_dispatching_force),
    ]
