from django.core.management.base import BaseCommand, CommandError

from optparse import make_option

from apps.fixmystreet.models import ReportCategory, ReportMainCategoryClass, ReportSecondaryCategoryClass

import logging, datetime, csv

logger = logging.getLogger("fixmystreet")

class Command(BaseCommand):
    help = 'Export categories as a CSV for FMX'

    option_list = BaseCommand.option_list + (
        make_option('--delete',
            action='store_true',
            dest='delete',
            default=False,
            help='Export categories as CSV'),
    )

    def handle(self, *args, **options):
        # CSV headers
        keys = ["ID", "PARENT_ID", "IS_ASSIGNABLE", "NAME_FR", "NAME_NL", "IS_ACTIVE", "IS_PUBLIC"]

        # Prepare file to write
        categories_csv = "categories.csv"
        categories_file = open(categories_csv, "wb")
        writer = csv.writer(categories_file)
        writer.writerow(keys)

        # Prepare list of values
        main_categories         = {}
        secondary_categories    = {}
        categories              = {}
        sub_categories          = []

        # Get all categories and browse the tree
        idx = 0
        report_categories = ReportCategory.objects.all()
        for category in report_categories:

            # Lvl1: MainCategory
            idx += 1
            main_category = category.category_class

            try:
                main_categories[main_category.id]
            except KeyError:
                main_categories[main_category.id] = [
                    idx,
                    "NULL",
                    False,
                    main_category.name_fr.encode('utf8'),
                    main_category.name_nl.encode('utf8'),
                    True,
                    True
                ]

            # Lvl2: SecondaryCategory
            idx += 1
            secondary_category = category.secondary_category_class
            secondary_key = "%s-%s" % (main_category.id, category.secondary_category_class.id)
            print secondary_key

            try:
                secondary_categories[secondary_key]
            except:
                secondary_categories[secondary_key] = [
                    idx,
                    main_categories[main_category.id][0],
                    False,
                    secondary_category.name_fr.encode('utf8'),
                    secondary_category.name_nl.encode('utf8'),
                    True,
                    True
                ]

            # Lvl3: Category
            idx += 1
            categories[category.id] = [
                idx,
                secondary_categories[secondary_key][0],
                not category.sub_categories.exists(),
                category.name_fr.encode('utf8'),
                category.name_nl.encode('utf8'),
                True,
                category.public
            ]

            # Lvl4: SubCategory (optional)
            for sub_category in category.sub_categories.all():
                idx += 1
                sub_categories.append([
                    idx,
                    categories[category.id][0],
                    True,
                    sub_category.name_fr.encode('utf8'),
                    sub_category.name_nl.encode('utf8'),
                    True,
                    True
                ])

        # Write to file
        for item in main_categories.values():
            writer.writerow(item)
        for item in secondary_categories.values():
            writer.writerow(item)
        for item in categories.values():
            writer.writerow(item)
        for item in sub_categories:
            writer.writerow(item)

        # Close file
        categories_file.close()
