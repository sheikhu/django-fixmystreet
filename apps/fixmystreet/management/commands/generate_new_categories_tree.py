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
    NEW_LVL_4 = []

    NEW_LVL_3_SUBCAT = {}

    FIXTURES_FMSPROXY = {}

    def handle(self, *args, **options):
        mapping_csv = options['mapping_csv'] if options['mapping_csv'] else 'apps/fixmystreet/migrations/categories_mapping.csv'

        with open(mapping_csv, 'rb') as mapping_file:
            mapping_reader = csv.reader(mapping_file, delimiter=',', quotechar='"')
            self.generate_fixtures(mapping_reader)

        new_categories_fixtures = self.NEW_LVL_1 + self.NEW_LVL_2 + self.NEW_LVL_3 + self.NEW_LVL_4

        categories_json = open('new_categories.json', 'w')
        categories_json.write(json.dumps(new_categories_fixtures, indent=4, default=self.date_handler))
        categories_json.close()

        categories_fmxproxy_json = open('new_categories_fmxproxy.json', 'w')
        categories_fmxproxy_json.write(json.dumps(self.FIXTURES_FMSPROXY.values(), indent=4))
        categories_fmxproxy_json.close()


    def generate_fixtures(self, mapping_reader):
            for row in mapping_reader:
                self.NEW_LVL_1.append(self.create_new_lvl1_category(row))
                self.NEW_LVL_2.append(self.create_new_lvl2_category(row))

                # LVL 4 has to be done before LVL 4 to compute subcats
                new_lvl_4 = self.create_new_lvl4_category(row)
                if new_lvl_4:
                    self.NEW_LVL_4.append(new_lvl_4)

                self.NEW_LVL_3.append(self.create_new_lvl3_category(row))

                # FMSProxy fixtures
                self.create_fmsproxy_mapping(row)

    def create_new_lvl1_category(self, data):
        return {
            "fields": {
                "name_en": data[NEW_LVL_1_NAME_EN_IDX].strip().capitalize(),
                "name_fr": data[NEW_LVL_1_NAME_FR_IDX].strip().capitalize(),
                "name_nl": data[NEW_LVL_1_NAME_NL_IDX].strip().capitalize(),
                "created": datetime.datetime.now(),
                "modified": datetime.datetime.now(),
                "slug_en": data[NEW_LVL_1_NAME_EN_IDX].strip(),
                "slug_fr": data[NEW_LVL_1_NAME_FR_IDX].strip(),
                "slug_nl": data[NEW_LVL_1_NAME_NL_IDX].strip()
            },
            "model": "fixmystreet.reportmaincategoryclass",
            "pk": int(data[NEW_LVL_1_ID_IDX])
        }


    def create_new_lvl2_category(self, data):
        return {
            "fields": {
                "name_en": data[NEW_LVL_2_NAME_EN_IDX].strip().capitalize(),
                "name_fr": data[NEW_LVL_2_NAME_FR_IDX].strip().capitalize(),
                "name_nl": data[NEW_LVL_2_NAME_NL_IDX].strip().capitalize(),
                "created": datetime.datetime.now(),
                "modified": datetime.datetime.now(),
                "slug_en": data[NEW_LVL_2_NAME_EN_IDX].strip(),
                "slug_fr": data[NEW_LVL_2_NAME_FR_IDX].strip(),
                "slug_nl": data[NEW_LVL_2_NAME_NL_IDX].strip()
            },
            "model": "fixmystreet.reportsecondarycategoryclass",
            "pk":  int(data[NEW_LVL_2_ID_IDX])
        }


    def create_new_lvl3_category(self, data):
        category_lvl_3 = ReportCategory.objects.get(id=int(data[LVL_3_ID_IDX]))

        try:
            self.NEW_LVL_3_SUBCAT[data[NEW_LVL_3_ID_IDX]]
        except KeyError:
            self.NEW_LVL_3_SUBCAT[data[NEW_LVL_3_ID_IDX]] = []

        field = {
            "fields": {
                "name_en": data[NEW_LVL_3_NAME_EN_IDX].strip().capitalize(),
                "name_fr": data[NEW_LVL_3_NAME_FR_IDX].strip().capitalize(),
                "name_nl": data[NEW_LVL_3_NAME_NL_IDX].strip().capitalize(),
                "created": datetime.datetime.now(),
                "category_class": int(data[NEW_LVL_1_ID_IDX]),
                "modified": datetime.datetime.now(),
                "public": True,
                "sub_categories": self.NEW_LVL_3_SUBCAT[data[NEW_LVL_3_ID_IDX]],
                "secondary_category_class": int(data[NEW_LVL_2_ID_IDX]),
                "slug_en": data[NEW_LVL_3_NAME_EN_IDX].strip(),
                "slug_fr": data[NEW_LVL_3_NAME_FR_IDX].strip(),
                "slug_nl": data[NEW_LVL_3_NAME_NL_IDX].strip()
            },
            "model": "fixmystreet.reportcategory",
            "pk": int(data[NEW_LVL_3_ID_IDX])
        }

        if category_lvl_3.organisation_regional:
            field['fields']['organisation_regional'] = category_lvl_3.organisation_regional.id
        if category_lvl_3.organisation_communal:
            field['fields']['organisation_communal'] = category_lvl_3.organisation_communal.id

        return field


    def create_new_lvl4_category(self, data):
        if data[LVL_4_ID_IDX] or data[NEW_LVL_4_ID_IDX]:
            try:
                self.NEW_LVL_3_SUBCAT[data[NEW_LVL_3_ID_IDX]].append(int(data[NEW_LVL_4_ID_IDX]))
            except KeyError:
                self.NEW_LVL_3_SUBCAT[data[NEW_LVL_3_ID_IDX]] = [int(data[NEW_LVL_4_ID_IDX])]

            return {
                "fields": {
                    "name_en": data[NEW_LVL_4_NAME_EN_IDX].strip().capitalize(),
                    "name_fr": data[NEW_LVL_4_NAME_FR_IDX].strip().capitalize(),
                    "name_nl": data[NEW_LVL_4_NAME_NL_IDX].strip().capitalize(),
                    "created": datetime.datetime.now(),
                    "modified": datetime.datetime.now(),
                    "slug_fr": "",
                    "slug_fr": "",
                    "slug_nl": ""
                },
                "model": "fixmystreet.reportsubcategory",
                "pk": int(data[NEW_LVL_4_ID_IDX])
            }

    def create_fmsproxy_mapping(self, data):

        if not data[ABP_TYPE_ID_IDX]:
            return

        try:
            # FMSProxy type
            fmsproxy_type = {
                "fields": {
                    "fms_id": int(data[NEW_LVL_2_ID_IDX]),
                    "abp_id": int(data[ABP_TYPE_ID_IDX])
                },
                "model": "abp.type",
                "pk": int(data[NEW_LVL_2_ID_IDX])
            }
            self.FIXTURES_FMSPROXY[int(data[NEW_LVL_2_ID_IDX])] = fmsproxy_type

            # FMSProxy nature
            try:
                nature_id = int(data[ABP_NATURE_ID_IDX])
                fms_id = int(data[NEW_LVL_3_ID_IDX])
            except ValueError:
                nature_id = int(data[ABP_NATURE_ID_ALT_IDX])
                fms_id = int(data[NEW_LVL_4_ID_IDX])

                logger.debug('ABP Nature Alt: %s - %s' %(int(data[ABP_NATURE_ID_ALT_IDX]), int(data[NEW_LVL_4_ID_IDX])))

            fmsproxy_nature = {
                "fields": {
                    "fms_id": fms_id,
                    "abp_id": nature_id
                },
                "model": "abp.nature",
                "pk": fms_id
            }
            self.FIXTURES_FMSPROXY[fms_id] = fmsproxy_nature

            # FMSProxy nature substitution
            try:
                fms_id = int(data[NEW_LVL_3_ID_IDX])
                fmsproxy_naturesubstitution = {
                    "fields": {
                        "fms_id": fms_id,
                        "abp_id": int(data[ABP_NATURESUBSTITUTION_ID_IDX])
                    },
                    "model": "abp.naturesubstitution",
                    "pk": fms_id
                }
                self.FIXTURES_FMSPROXY[10000 + fms_id] = fmsproxy_naturesubstitution

            except ValueError:
                pass

            # FMSProxy subnature
            try:
                fmsproxy_subnature = {
                    "fields": {
                        "fms_id": int(data[NEW_LVL_4_ID_IDX]),
                        "abp_id": int(data[ABP_SUBNATURE_ID_IDX])
                    },
                    "model": "abp.subnature",
                    "pk": int(data[NEW_LVL_4_ID_IDX])
                }
                self.FIXTURES_FMSPROXY[int(data[NEW_LVL_3_ID_IDX])] = fmsproxy_subnature
            except ValueError:
                pass

            # FMSProxy bagtype
            try:
                fmsproxy_bagtype = {
                    "fields": {
                        "fms_id": int(data[NEW_LVL_4_ID_IDX]),
                        "abp_id": int(data[ABP_BAGTYPE_ID_IDX])
                    },
                    "model": "abp.bagtype",
                    "pk": int(data[NEW_LVL_4_ID_IDX])
                }
                self.FIXTURES_FMSPROXY[int(data[NEW_LVL_4_ID_IDX])] = fmsproxy_bagtype
            except ValueError:
                pass

        except IndexError:
            pass


    def date_handler(self, obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        else:
            raise TypeError
