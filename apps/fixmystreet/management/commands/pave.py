# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError

from optparse import make_option

from apps.fixmystreet.models import Report, FMSUser

import csv, logging, datetime

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

    def handle(self, *args, **options):
        pave_csv = options['pave_csv'] if options['pave_csv'] else 'apps/resources/PAVE/pave.csv'

        with open(pave_csv, 'rb') as pave_file:
            pave_reader = csv.reader(pave_file, delimiter=';', quotechar='"')
            firstline = True

            errors = []

            for row in pave_reader:
                logger.info(row)

                if firstline:
                    firstline = False
                    continue

                report = Report(
                    citizen=self.get_pave_user()
                )

                try:
                    self.set_category(report, row)
                except KeyError:
                    errors.append(row)
                    continue

                # self.set_address(report, row)
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
