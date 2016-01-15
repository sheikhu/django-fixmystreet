from django.core.management.base import BaseCommand, CommandError
from apps.fixmystreet.models import OrganisationEntity, ReportMainCategoryClass, ReportSecondaryCategoryClass, ReportCategory
from django.utils import translation
import os

class Command(BaseCommand):
    help = 'Update sibelga incidents (one time script)'

    def add_arguments(self, parser):
        parser.add_argument('commune', nargs='+', type=int)

    def handle(self, *args, **options):
        translation.activate('fr')
        main_cats = ReportMainCategoryClass.objects.all()
        for commune in options['commune']:
            file_name = '/tmp/temp_groups_{}'.format(commune)
            try:
                os.remove(file_name)
            except OSError:
                pass
            f = open(file_name, 'a')
            self.stdout.write ('"Export commune {}"'.format(commune))

            for secCat in ReportSecondaryCategoryClass.objects.all():
                # Column: For one SecondaryCategory, build each columns concerning MainCategoryClass
                for mainCat in ReportMainCategoryClass.objects.all():
                    categories = ReportCategory.objects.filter(category_class_id=mainCat.id, secondary_category_class_id=secCat.id)

                    # Cell: Inside each cell, list all groups
                    for cat in categories:
                        f.write('"{}";"{}";"{}";"{}"\n'.format(mainCat.name.encode('utf-8'), secCat.name.encode('utf-8'), cat.name.encode('utf-8'), cat.assigned_to_department.filter(dependency=commune).get().name_fr.encode('utf-8')))
            f.close()
            self.stdout.write ('Fichier : {}'.format(file_name))
