# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import GEOSGeometry

from optparse import make_option

from apps.fixmystreet.models import Report, FMSUser

import csv, json, logging, requests

logger = logging.getLogger("fixmystreet")

class Command(BaseCommand):
    help = 'Inject PAVE reports to FMS from CSV and pictures.'

    option_list = BaseCommand.option_list + (
        make_option('--csv',
            action='store',
            dest='pave_csv',
            default="",
            help='The pave csv file'),
    )

    PAVE_CATEGORIES = {
        u"Dégradation ponctuelle source de danger": {
            "category" : 1001,
            "secondary_category" : 3027
        },
        u"Ligne de guidage menant à un danger": {
            "category" : 1007,
            "secondary_category" : 3045
        },
        u"Marquage du passage piétons": {
            "category" : 1001,
            "secondary_category" : 3040
        },
        u"Obstacle à la chaîne de déplacement source de danger": {
            "category" : 1001,
            "secondary_category" : 3027
        },
        u"Obstacle à la circulation" : {
            "category" : 1007,
            "secondary_category" : 3045
        }
    }

    PAVE_CATEGORY_IDX = 1

    PAVE_LAT_IDX = 3
    PAVE_LONG_IDX = 4

    def handle(self, *args, **options):
        pave_csv = options['pave_csv'] if options['pave_csv'] else 'apps/resources/PAVE/pave.csv'

        with open(pave_csv, 'rb') as pave_file:
            pave_reader = csv.reader(pave_file, delimiter=';', quotechar='"')
            firstline = True

            errors = []

            for row in pave_reader:
                logger.info(row)

                # Avoid CSV headers
                if firstline:
                    firstline = False
                    continue

                # Create new report
                report = Report(
                    citizen=self.get_pave_user(),
                    private=True
                )

                # try:
                #     self.set_category(report, row)
                # except KeyError:
                #     errors.append(row)
                #     continue

                self.set_address(report, row)
                # self.dispatch(report, row)
                # self.set_description(report, row)
                # self.set_attachments(report, row)

        if errors:
            logger.error(errors)


    def get_pave_user(self):
        pave_user, isCreated = FMSUser.objects.get_or_create(
            first_name='PAVE',
            last_name='PAVE',
            email="pave@noresponse.com",
            quality=FMSUser.OTHER,
            telephone="-"
        )

        if isCreated:
            logger.info("Pave user CREATED")
        else:
            logger.info("Pave user ALREADY EXISTS")

        return pave_user


    def set_category(self, report, row):
        pave_category = self.PAVE_CATEGORIES[row[self.PAVE_CATEGORY_IDX]]

        report.category = pave_category['category']
        report.secondary_category = pave_category['secondary_category']


    def set_address(self, report, row):
        # Set point
        x = row[self.PAVE_LAT_IDX].replace(',','.')
        y = row[self.PAVE_LONG_IDX].replace(',','.')

        report.point = GEOSGeometry(
            "POINT(" + x + " " + y + ")",
            srid=4326
        )

        # Fetch address from urbis
        json_data = {
            "point": {
                "x": x,
                "y": y
            },
            "SRS_In":"4326"
        }
        json_data_fr = json_data
        json_data_fr["language"] = "fr"

        json_data_nl = json_data
        json_data_nl["language"] = "nl"

        address_fr = self._get_urbis_address(json_data_fr)
        address_nl = self._get_urbis_address(json_data_nl)

        # Set address
        if address_fr:
            report.address_fr = address_fr.get('address').get('street').get('name')
            report.address_number = address_fr.get('address').get('number')
            report.postalcode = address_fr.get('address').get('street').get('postCode')
            # report.address_regional

        if address_nl:
            report.address_nl = address_fr.get('address').get('street').get('name')
            report.address_number = address_fr.get('address').get('number')
            report.postalcode = address_fr.get('address').get('street').get('postCode')
            # report.address_regional

    def _get_urbis_address(self, json_data):
        response = requests.get("http://geoservices.irisnet.be/localization/Rest/Localize/getaddressfromxy?json=" + json.dumps(json_data))

        if response.status_code == requests.codes.ok:
            return response.json().get('result')

        logger.error('Address: cannot fetch urbis address')
        return None
