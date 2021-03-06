# -*- coding: utf-8 -*-

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
        make_option('--dump',
            action='store',
            dest='dump',
            default="",
            help='Dump to generate (values are fms or fmsproxy)'),
    )

    idx_reportsecondarycategoryclass = 9
    idx_reportsubcategory = 0
    idx_reportcategory = 150

    abp_entity_id = 23
    abp_group_id = 300
    abp_groupmail_id = 200
    abp_user_id = 10673

    def handle(self, *args, **options):
        logger.info('Loading file %s' % options['typology'])

        fixtures_fms = []
        fixtures_fmsproxy = []

        subnature_ids = []
        bagtype_ids = []

        nature_type_ids = {}
        types_bagtypes_flag = {}

        translations_corrections = {
            u"...autre...": u"Propreté",
            u"...andere...": u"Netheid",
            u"autre (Inclassable)": u"Inclassable",
            u"andere (Onklasseerbaar)": u"Onklasseerbaar"
        }

        with open(options['typology']) as json_data:
            typology = json.load(json_data)
            logger.info('Typology file loaded')


            logger.info('Processing types')
            idx = 0
            types_ids = {}
            for typology_type in typology['data']['types']:
                types_ids[typology_type['type_id']] = self.idx_reportsecondarycategoryclass +idx

                try:
                    name_fr = translations_corrections[typology_type['label']['fr']]
                    name_nl = translations_corrections[typology_type['label']['nl']]
                except KeyError:
                    name_fr = typology_type['label']['fr']
                    name_nl = typology_type['label']['nl']

                reportsecondarycategoryclass = {
                    "pk": types_ids[typology_type['type_id']],
                    "model": "fixmystreet.reportsecondarycategoryclass",
                    "fields": {
                        "name_en": name_fr,
                        "name_fr": name_fr,
                        "name_nl": name_nl
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

                logger.info('Processing subnatures')
                idx = 1
                subnatures_ids = {}
                for typology_subnature in typology['data']['subnatures']:
                    subnatures_ids[typology_subnature['subnature_id']] = self.idx_reportsubcategory +idx

                    try:
                        name_fr = translations_corrections[typology_subnature['label']['fr']]
                        name_nl = translations_corrections[typology_subnature['label']['nl']]
                    except KeyError:
                        name_fr = typology_subnature['label']['fr']
                        name_nl = typology_subnature['label']['nl']

                    reportsubcategory = {
                        "pk": subnatures_ids[typology_subnature['subnature_id']],
                        "model": "fixmystreet.reportsubcategory",
                        "fields": {
                            "name_en": name_fr,
                            "name_fr": name_fr,
                            "name_nl": name_nl
                        }
                    }
                    fixtures_fms.append(reportsubcategory)
                    subnature_ids.append(subnatures_ids[typology_subnature['subnature_id']])

                    # FMSProxy
                    fmsproxy_subnature = {
                        "fields": {
                            "fms_id": subnatures_ids[typology_subnature['subnature_id']],
                            "abp_id": typology_subnature['subnature_id']
                        },
                        "model": "abp.subnature",
                        "pk": idx
                    }
                    fixtures_fmsproxy.append(fmsproxy_subnature)

                    idx = idx +1

            logger.info('Processing bagtypes')
            idx = 1
            bagtypes_ids = {}
            for typology_bagtype in typology['data']['bagtypes']:
                bagtypes_ids[typology_bagtype['bagtype_id']] = self.idx_reportsubcategory +idx

                try:
                    name_fr = translations_corrections[typology_bagtype['label']['fr']]
                    name_nl = translations_corrections[typology_bagtype['label']['nl']]
                except KeyError:
                    name_fr = typology_bagtype['label']['fr']
                    name_nl = typology_bagtype['label']['nl']

                reportsubcategory = {
                    "pk": bagtypes_ids[typology_bagtype['bagtype_id']],
                    "model": "fixmystreet.reportsubcategory",
                    "fields": {
                        "name_en": name_fr,
                        "name_fr": name_fr,
                        "name_nl": name_nl
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

                        try:
                            name_fr = translations_corrections[typology_nature['label']['fr']]
                            name_nl = translations_corrections[typology_nature['label']['nl']]
                        except KeyError:
                            name_fr = typology_nature['label']['fr']
                            name_nl = typology_nature['label']['nl']

                        reportcategory = {
                            "pk": natures_ids[typology_nature['nature_id']],
                            "model": "fixmystreet.reportcategory",
                            "fields": {
                                "name_en": name_fr,
                                "name_fr": name_fr,
                                "name_nl": name_nl,
                                "public": True,
                                "organisation_regional": self.abp_entity_id,
                                "organisation_communal": self.abp_entity_id,

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

            # Add ABP Entity
            fixtures_fms.append({
                "fields": {
                    "name_en": "Bruxelles-Propreté",
                    "name_fr": "Bruxelles-Propreté",
                    "name_nl": "Net Brussels",
                    "email": "pro@arp-gan.be",
                    "phone": "0800 981 81",
                    "active": True,
                    "type": "R",
                },
                "model": "fixmystreet.organisationentity",
                "pk": self.abp_entity_id
            })

            # Add ABP Group and generate dispatching for it
            fixtures_fms.append({
                "fields": {
                    "name_en": "Bruxelles-Propreté Group",
                    "name_fr": "Bruxelles-Propreté Groupe",
                    "name_nl": "Net Brussels Group",
                    "created": datetime.datetime.now(),
                    "dispatch_categories": natures_ids.values(),
                    "dependency": self.abp_entity_id,
                    "modified": datetime.datetime.now(),
                    "email": "pro@arp-gan.be",
                    "phone": "0800 981 81",
                    "active": True,
                    "slug_fr": "Bruxelles-Propreté Groupe",
                    "type": "D",
                    "slug_nl": "Net Brussels Group"
                },
                "model": "fixmystreet.organisationentity",
                "pk": self.abp_group_id
            })

            # Add GroupMailConfig for Abp Group
            fixtures_fms.append({
                "fields": {
                    "notify_members": False,
                    "group": self.abp_group_id,
                    "digest_closed": False,
                    "digest_other": False,
                    "digest_created": False,
                    "digest_inprogress": False,
                    "notify_group": False
                },
                "model": "fixmystreet.groupmailconfig",
                "pk": self.abp_groupmail_id
            })

            # Fix abp user entity
            fixtures_fms.append({
                "fields": {
                    "applicant": False,
                    "logical_deleted": False,
                    "organisation": self.abp_entity_id,
                    "telephone": "0800 981 81",
                    "agent": False,
                    "contractor": False,
                    "manager": True,
                    "groups": [],
                    "modified": datetime.datetime.now(),
                    "user_permissions": [],
                    "quality": None,
                    "leader": False
                },
                "model": "fixmystreet.fmsuser",
                "pk": self.abp_user_id
            })

            # Create membership to group
            fixtures_fms.append({
                "fields": {
                    "created": datetime.datetime.now(),
                    "organisation": self.abp_group_id,
                    "contact_user": True,
                    "modified": datetime.datetime.now(),
                    "user": self.abp_user_id
                },
                "model": "fixmystreet.userorganisationmembership"
            })

        if options['dump'] == 'fms':
            logger.info('Dump fixtures fms')
            print json.dumps(fixtures_fms, indent=4, default=self.date_handler)

        if options['dump'] == 'fmsproxy':
            logger.info('Dump fixtures fmsproxy')
            print json.dumps(fixtures_fmsproxy, indent=4)

    def date_handler(self, obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        else:
            raise TypeError
