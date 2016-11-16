from django.core.management.base import BaseCommand, CommandError

from optparse import make_option

import logging, datetime, json

logger = logging.getLogger("fixmystreet")

class Command(BaseCommand):
    help = 'Generate ABP fixtures from typology'

    option_list = BaseCommand.option_list + (
        make_option('--typology',
            action='store',
            dest='typology',
            default="",
            help='The file typology.json'),
        make_option('--category_classes',
            action='store',
            dest='category_classes',
            default="",
            help='Category classes to generate (ids comma separated)'),
        make_option('--abp_entity_id',
            action='store',
            dest='abp_entity_id',
            default="",
            help='ABP entity id'),
        make_option('--dump',
            action='store',
            dest='dump',
            default="",
            help='Dump to generate (values are fms or fmsproxy)'),
    )

    idx_reportsecondarycategoryclass = 9
    idx_reportsubcategory = 0
    idx_reportcategory = 118

    def handle(self, *args, **options):
        logger.info('Loading file %s' % options['typology'])

        fixtures_fms = []
        fixtures_fmsproxy = []

        bagtype_ids = []

        nature_type_ids = {}
        types_bagtypes_flag = {}

        with open(options['typology']) as json_data:
            typology = json.load(json_data)
            logger.info('Typology file loaded')


            logger.info('Processing types')
            idx = 0
            types_ids = {}
            for typology_type in typology['data']['types']:
                types_ids[typology_type['type_id']] = self.idx_reportsecondarycategoryclass +idx

                reportsecondarycategoryclass = {
                    "pk": types_ids[typology_type['type_id']],
                    "model": "fixmystreet.reportsecondarycategoryclass",
                    "fields": {
                        "name_fr": typology_type['label']['fr'],
                        "name_nl": typology_type['label']['nl']
                    }
                }
                fixtures_fms.append(reportsecondarycategoryclass)

                # Map natures id's and type id's
                for nature in typology_type['nature_ids']:
                    nature_type_ids[nature] = types_ids[typology_type['type_id']]

                # Flag if bagtypes
                for bagtype in typology_type['bagtype_ids']:
                    types_bagtypes_flag[types_ids[typology_type['type_id']]] = True

                # FMSProxy
                fmsproxy_type = {
                    "fields": {
                        "fms_id": types_ids[typology_type['type_id']],
                        "abp_id": typology_type['type_id']
                    },
                    "model": "abp.type",
                    "pk": idx
                }
                fixtures_fmsproxy.append(fmsproxy_type)

                idx = idx +1

            logger.info('Processing bagtypes')
            idx = 1
            bagtypes_ids = {}
            for typology_bagtype in typology['data']['bagtypes']:
                bagtypes_ids[typology_bagtype['bagtype_id']] = self.idx_reportsubcategory +idx

                reportsubcategory = {
                    "pk": bagtypes_ids[typology_bagtype['bagtype_id']],
                    "model": "fixmystreet.reportsubcategory",
                    "fields": {
                        "name_fr": typology_bagtype['label']['fr'],
                        "name_nl": typology_bagtype['label']['nl']
                    }
                }
                fixtures_fms.append(reportsubcategory)
                bagtype_ids.append(bagtypes_ids[typology_bagtype['bagtype_id']])

                # FMSProxy
                fmsproxy_bagtype = {
                    "fields": {
                        "fms_id": bagtypes_ids[typology_bagtype['bagtype_id']],
                        "abp_id": typology_bagtype['bagtype_id']
                    },
                    "model": "abp.bagtype",
                    "pk": idx
                }
                fixtures_fmsproxy.append(fmsproxy_bagtype)

                idx = idx +1

            if options['category_classes']:
                category_classes = options['category_classes'].split(',')

                logger.info('Processing natures')
                idx = 0
                natures_ids = {}
                for typology_nature in typology['data']['natures']:

                    for category_class in category_classes:
                        natures_ids[typology_nature['nature_id']] = self.idx_reportcategory +idx

                        reportcategory = {
                            "pk": natures_ids[typology_nature['nature_id']],
                            "model": "fixmystreet.reportcategory",
                            "fields": {
                                "name_fr": typology_nature['label']['fr'],
                                "name_nl": typology_nature['label']['nl'],
                                "public": True,
                                "organisation_regional": int(options['abp_entity_id']),
                                "organisation_communal": int(options['abp_entity_id']),

                                "category_class": int(category_class),
                                "secondary_category_class": nature_type_ids[typology_nature['nature_id']]
                            },
                        }

                        # Set bagtypes if needed
                        try:
                            if types_bagtypes_flag[nature_type_ids[typology_nature['nature_id']]]:
                                reportcategory['fields']['sub_categories'] = bagtype_ids
                        except KeyError:
                            pass

                        fixtures_fms.append(reportcategory)

                        # FMSProxy
                        fmsproxy_nature = {
                            "fields": {
                                "fms_id": natures_ids[typology_nature['nature_id']],
                                "abp_id": typology_nature['nature_id']
                            },
                            "model": "abp.nature",
                            "pk": idx
                        }
                        fixtures_fmsproxy.append(fmsproxy_nature)

                        idx = idx +1

        if options['dump'] == 'fms':
            logger.info('Dump fixtures fms')
            print json.dumps(fixtures_fms, indent=4)

        if options['dump'] == 'fmsproxy':
            logger.info('Dump fixtures fmsproxy')
            print json.dumps(fixtures_fmsproxy, indent=4)
