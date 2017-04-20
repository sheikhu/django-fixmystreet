from django.core.management.base import BaseCommand, CommandError

from optparse import make_option
import datetime, logging, csv, json

from apps.fixmystreet.models import ReportCategory

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

    LVL_1_NAME_FR_IDX = 0
    LVL_1_NAME_NL_IDX = 1
    LVL_1_NAME_EN_IDX = 2

    LVL_2_NAME_FR_IDX = 3
    LVL_2_NAME_NL_IDX = 4
    LVL_2_NAME_EN_IDX = 5

    LVL_3_NAME_FR_IDX = 6
    LVL_3_NAME_NL_IDX = 7
    LVL_3_NAME_EN_IDX = 8

    LVL_4_NAME_FR_IDX = 9
    LVL_4_NAME_NL_IDX = 10
    LVL_4_NAME_EN_IDX = 11

    LVL_1_ID_IDX = 12
    LVL_2_ID_IDX = 13
    LVL_3_ID_IDX = 14
    LVL_4_ID_IDX = 15

    AUTO_DISPATCHING_COMMUNAL_IDX = 16
    AUTO_DISPATCHING_REGIONAL_IDX = 17

    ABP_TYPE_ID_IDX = 18
    ABP_NATURE_ID_IDX = 19
    ABP_BAGTYPE_ID_IDX = 20

    LVL_1 = []
    LVL_2 = []
    LVL_3 = []
    LVL_4 = []

    LVL_3_SUBCAT = {}

    FIXTURES_FMSPROXY = {}

    def handle(self, *args, **options):
        mapping_csv = options['mapping_csv'] if options['mapping_csv'] else 'apps/fixmystreet/migrations/categories_new.csv'

        with open(mapping_csv, 'rb') as mapping_file:
            mapping_reader = csv.reader(mapping_file, delimiter=',', quotechar='"')
            self.generate_fixtures(mapping_reader)

        new_categories_fixtures = self.LVL_1 + self.LVL_2 + self.LVL_3 + self.LVL_4

        categories_json = open('new_categories_append.json', 'w')
        categories_json.write(json.dumps(new_categories_fixtures, indent=4, default=self.date_handler))
        categories_json.close()

        categories_fmxproxy_json = open('new_categories_fmxproxy_append.json', 'w')
        categories_fmxproxy_json.write(json.dumps(self.FIXTURES_FMSPROXY.values(), indent=4))
        categories_fmxproxy_json.close()


    def generate_fixtures(self, mapping_reader):
            for row in mapping_reader:
                self.LVL_1.append(self.create_LVL1_category(row))
                self.LVL_2.append(self.create_LVL2_category(row))

                # LVL 4 has to be done before LVL 4 to compute subcats
                try:
                    LVL_4 = self.create_LVL4_category(row)
                    if LVL_4:
                        self.LVL_4.append(LVL_4)
                except IndexError:
                    pass

                self.LVL_3.append(self.create_LVL3_category(row))

                # FMSProxy fixtures
                self.create_fmsproxy_mapping(row)

    def create_LVL1_category(self, data):
        return {
            "fields": {
                "name_fr": data[self.LVL_1_NAME_FR_IDX].strip().capitalize(),
                "name_nl": data[self.LVL_1_NAME_NL_IDX].strip().capitalize(),
                "created": datetime.datetime.now(),
                "modified": datetime.datetime.now(),
                "slug_fr": data[self.LVL_1_NAME_FR_IDX].strip(),
                "slug_nl": data[self.LVL_1_NAME_NL_IDX].strip()
            },
            "model": "fixmystreet.reportmaincategoryclass",
            "pk": int(data[self.LVL_1_ID_IDX])
        }


    def create_LVL2_category(self, data):
        return {
            "fields": {
                "name_fr": data[self.LVL_2_NAME_FR_IDX].strip().capitalize(),
                "name_nl": data[self.LVL_2_NAME_NL_IDX].strip().capitalize(),
                "created": datetime.datetime.now(),
                "modified": datetime.datetime.now(),
                "slug_fr": data[self.LVL_2_NAME_FR_IDX].strip(),
                "slug_nl": data[self.LVL_2_NAME_NL_IDX].strip()
            },
            "model": "fixmystreet.reportsecondarycategoryclass",
            "pk":  int(data[self.LVL_2_ID_IDX])
        }


    def create_LVL3_category(self, data):
        try:
            self.LVL_3_SUBCAT[data[self.LVL_3_ID_IDX]]
        except KeyError:
            self.LVL_3_SUBCAT[data[self.LVL_3_ID_IDX]] = []

        field = {
            "fields": {
                "name_fr": data[self.LVL_3_NAME_FR_IDX].strip().capitalize(),
                "name_nl": data[self.LVL_3_NAME_NL_IDX].strip().capitalize(),
                "created": datetime.datetime.now(),
                "category_class": int(data[self.LVL_1_ID_IDX]),
                "modified": datetime.datetime.now(),
                "public": True,
                "sub_categories": self.LVL_3_SUBCAT[data[self.LVL_3_ID_IDX]],
                "secondary_category_class": int(data[self.LVL_2_ID_IDX]),
                "slug_fr": data[self.LVL_3_NAME_FR_IDX].strip(),
                "slug_nl": data[self.LVL_3_NAME_NL_IDX].strip()
            },
            "model": "fixmystreet.reportcategory",
            "pk": int(data[self.LVL_3_ID_IDX])
        }

        if data[self.AUTO_DISPATCHING_COMMUNAL_IDX]:
            field['fields']['organisation_communal'] = data[self.AUTO_DISPATCHING_COMMUNAL_IDX]
        if data[self.AUTO_DISPATCHING_REGIONAL_IDX]:
            field['fields']['organisation_regional'] = data[self.AUTO_DISPATCHING_REGIONAL_IDX]


        return field


    def create_LVL4_category(self, data):
        if data[self.LVL_4_ID_IDX] or data[self.LVL_4_ID_IDX]:
            try:
                self.LVL_3_SUBCAT[data[self.LVL_3_ID_IDX]].append(int(data[self.LVL_4_ID_IDX]))
            except KeyError:
                self.LVL_3_SUBCAT[data[self.LVL_3_ID_IDX]] = [int(data[self.LVL_4_ID_IDX])]

            return {
                "fields": {
                    "name_fr": data[self.LVL_4_NAME_FR_IDX].strip().capitalize(),
                    "name_nl": data[self.LVL_4_NAME_NL_IDX].strip().capitalize(),
                    "created": datetime.datetime.now(),
                    "modified": datetime.datetime.now(),
                    "slug_fr": "",
                    "slug_nl": ""
                },
                "model": "fixmystreet.reportsubcategory",
                "pk": int(data[self.LVL_4_ID_IDX])
            }

    def create_fmsproxy_mapping(self, data):

        if not data[self.ABP_TYPE_ID_IDX]:
            return

        try:
            # FMSProxy type
            fmsproxy_type = {
                "fields": {
                    "fms_id": int(data[self.LVL_2_ID_IDX]),
                    "abp_id": int(data[self.ABP_TYPE_ID_IDX])
                },
                "model": "abp.type"
            }
            self.FIXTURES_FMSPROXY[int(data[self.LVL_2_ID_IDX])] = fmsproxy_type

            # FMSProxy nature
            fmsproxy_nature = {
                "fields": {
                    "fms_id": int(data[self.LVL_3_ID_IDX]),
                    "abp_id": int(data[self.ABP_NATURE_ID_IDX])
                },
                "model": "abp.nature"
            }
            self.FIXTURES_FMSPROXY[int(data[self.LVL_3_ID_IDX])] = fmsproxy_nature

            try:
                # FMSProxy bagtype
                fmsproxy_bagtype = {
                    "fields": {
                        "fms_id": int(data[self.LVL_4_ID_IDX]),
                        "abp_id": int(data[self.ABP_BAGTYPE_ID_IDX])
                    },
                    "model": "abp.bagtype"
                }
                self.FIXTURES_FMSPROXY[int(data[self.LVL_4_ID_IDX])] = fmsproxy_bagtype
            except ValueError:
                pass

        except IndexError:
            pass


    def date_handler(self, obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        else:
            raise TypeError
