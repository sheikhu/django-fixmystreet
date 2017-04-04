from django.core.management.base import BaseCommand, CommandError

from optparse import make_option
import datetime, logging, csv, json

from apps.fixmystreet.models import ReportCategory
from .new_category_consts import *

logger = logging.getLogger("fixmystreet")


class Command(BaseCommand):
    help = 'Generate a new categories tree from existing'

    option_list = BaseCommand.option_list + (
        make_option('--mapping',
            action='store',
            dest='mapping_csv',
            default="",
            help='The mapping csv file'),
    )

    NEW_LVL_1 = []
    NEW_LVL_2 = []
    NEW_LVL_3 = []

    def handle(self, *args, **options):
        with open(options['mapping_csv'], 'rb') as mapping_file:
            mapping_reader = csv.reader(mapping_file, delimiter=',', quotechar='"')
            self.generate_fixtures(mapping_reader)

        new_categories_fixtures = self.NEW_LVL_1 + self.NEW_LVL_2 + self.NEW_LVL_3

        print json.dumps(new_categories_fixtures, indent=4, default=self.date_handler)


    def generate_fixtures(self, mapping_reader):
            for row in mapping_reader:
                self.NEW_LVL_1.append(self.create_new_lvl1_category(row))
                self.NEW_LVL_2.append(self.create_new_lvl2_category(row))
                self.NEW_LVL_3.append(self.create_new_lvl3_category(row))


    def create_new_lvl1_category(self, data):
        return {
            "fields": {
                "name_fr": data[NEW_LVL_1_NAME_IDX],
                "modified_by": None,
                "name_nl": data[NEW_LVL_1_NAME_IDX],
                "created": datetime.datetime.now(),
                "modified": datetime.datetime.now(),
                "created_by": None,
                "slug_fr": data[NEW_LVL_1_NAME_IDX],
                "slug_nl": data[NEW_LVL_1_NAME_IDX]
            },
            "model": "fixmystreet.reportmaincategoryclass",
            "pk": int(data[NEW_LVL_1_ID_IDX])
        }


    def create_new_lvl2_category(self, data):
        return {
            "fields": {
                "name_fr": data[NEW_LVL_2_NAME_IDX],
                "modified_by": None,
                "name_nl": data[NEW_LVL_2_NAME_IDX],
                "created": datetime.datetime.now(),
                "modified": datetime.datetime.now(),
                "created_by": None,
                "slug_fr": data[NEW_LVL_2_NAME_IDX],
                "slug_nl": data[NEW_LVL_2_NAME_IDX]
            },
            "model": "fixmystreet.reportsecondarycategoryclass",
            "pk":  int(data[NEW_LVL_2_ID_IDX])
        }


    def create_new_lvl3_category(self, data):
        category_lvl_3 = ReportCategory.objects.get(id=int(data[LVL_3_ID_IDX]))

        return {
            "fields": {
                "name_fr": data[NEW_LVL_3_NAME_IDX],
                "modified_by": None,
                "name_nl": data[NEW_LVL_3_NAME_IDX],
                "created": datetime.datetime.now(),
                "category_class": int(data[NEW_LVL_1_ID_IDX]),
                "modified": datetime.datetime.now(),
                "created_by": None,
                "public": True,
                "organisation_regional": category_lvl_3.organisation_regional.id if category_lvl_3.organisation_regional else None,
                "organisation_communal": category_lvl_3.organisation_communal.id if category_lvl_3.organisation_communal else None,
                # "sub_categories": [],
                "secondary_category_class": int(data[NEW_LVL_2_ID_IDX]),
                "slug_fr": data[NEW_LVL_3_NAME_IDX],
                "slug_nl": data[NEW_LVL_3_NAME_IDX]
            },
            "model": "fixmystreet.reportcategory",
            "pk": int(data[NEW_LVL_3_ID_IDX])
        }

    def date_handler(self, obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        else:
            raise TypeError
