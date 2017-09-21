# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import GEOSGeometry, Point
from django.conf import settings

from optparse import make_option

from apps.fixmystreet.models import Report, ReportComment, ReportEventLog, FMSUser, ReportMainCategoryClass, ReportCategory, ReportFile, OrganisationEntity

import csv, datetime, json, logging, requests, subprocess

logger = logging.getLogger("fixmystreet")

class Command(BaseCommand):
    help = 'Inject PAVE reports to FMS from CSV and pictures.'

    option_list = BaseCommand.option_list + (
        make_option('--csv',
            action='store',
            dest='pave_csv',
            default="",
            help='The pave csv file to parse'),

        make_option('--municipality',
            action='store',
            dest='municipality',
            default="",
            help='The municipality string to use as PAVE username and email'),

        make_option('--pictures_folder',
            action='store',
            dest='pictures_folder',
            default="",
            help='The folder containing original pictures'),

        make_option('--index_start',
            action='store',
            dest='index_start',
            default=None,
            help='The index to start PAVE parsing'),

        make_option('--index_end',
            action='store',
            dest='index_end',
            default=None,
            help='The index to end PAVE parsing'),
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

    PAVE_ID_IDX = 1
    PAVE_CATEGORY_IDX = 14
    PAVE_SOLUTION_IDX = 15
    PAVE_LAT_IDX = 6
    PAVE_LONG_IDX = 7
    PAVE_PICTURE_IDX = 33

    municipality = None
    pave_csv = None
    pictures_folder = None
    index_start = None
    index_end = None

    region_entity = OrganisationEntity.objects.get(id=20)

    def handle(self, *args, **options):
        if not options['municipality']:
            logger.error('No municipality supplied. See help. Aborted.')
            return

        if not options['pictures_folder']:
            logger.error('No pictures folder supplied. See help. Aborted.')
            return

        if not options['pave_csv']:
            logger.error('No csv file supplied. See help. Aborted.')
            return

        self.municipality = options['municipality']
        self.pave_csv = options['pave_csv']
        self.pictures_folder = options['pictures_folder']
        self.index_start = int(options['index_start']) if options['index_start'] else None
        self.index_end = int(options['index_end']) if options['index_end'] else None

        self.resize_pictures()
        self.inject_data()


    def resize_pictures(self):
        command = "convert {}/*.JPG".format(self.pictures_folder)
        command += " "
        command += "-resize 140x140 -set filename:myname '%t' '{}/%[filename:myname].thumbnail.JPG'".format(self.pictures_folder)

        subprocess.call(command, shell=True)


    def inject_data(self):
        with open(self.pave_csv, 'rb') as pave_file:
            pave_reader = csv.reader(pave_file, delimiter=';', quotechar='"')
            firstline = True

            errors = []

            for row in list(pave_reader)[self.index_start:self.index_end]:
                # logger.info(row)

                # Avoid CSV headers
                if firstline:
                    firstline = False
                    continue


                logger.info('Report with NEW PAVE id {}'.format(self._get_pave_id(row)))

                # Create new report
                report = Report(
                    citizen=self._get_pave_user(),
                    private=True,
                    pending=True
                )
                report.bypassNotification = True

                try:
                    self.set_category(report, row)
                except KeyError:
                    errors.append({self._get_pave_id(row): "Invalid categories"})
                    continue

                self.set_address(report, row)
                self.set_external_id(report, row)
                self.set_regional_flag(report, row)

                report.save()

                self.set_description(report, row)
                self.set_history(report, row)

                try:
                    ReportFile.objects.get(file__icontains=row[self.PAVE_PICTURE_IDX], report__id=report.id)
                    logger.info('   Image {} of Report {} ALREADY exists'.format(row[self.PAVE_PICTURE_IDX], report.id))
                except ReportFile.DoesNotExist:
                    logger.info('   NEW image {} for Report {}'.format(row[self.PAVE_PICTURE_IDX], report.id))
                    try:
                        self.set_pictures(report, row)
                    except:
                        errors.append({self._get_pave_id(row): "Picture problem"})
                        continue
                except ReportFile.MultipleObjectsReturned:
                    logger.info('   Oops, Report {} already has multiple same images {}'.format(report.id, row[self.PAVE_PICTURE_IDX]))

        if errors:
            logger.error(errors)
            logger.error("{} errors".format(len(errors)))


    def _get_pave_id(self, row):
        id = row[self.PAVE_ID_IDX].split('/')[0].strip()
        return "PAVE-{}".format(id)

    def _get_pave_name(self):
        return "PAVE [{}]".format(self.municipality)

    def _get_pave_email(self):
        return "pave-{}@noresponse.com".format(self.municipality)

    def _get_pave_user(self):
        pave_user, isCreated = FMSUser.objects.get_or_create(
            last_name=self._get_pave_name(),
            email=self._get_pave_email(),
            quality=FMSUser.OTHER,
            telephone="-"
        )

        return pave_user


    def set_category(self, report, row):
        pave_category = self.PAVE_CATEGORIES[unicode(row[self.PAVE_CATEGORY_IDX].strip(), 'utf-8')]

        report.category = ReportMainCategoryClass.objects.get(id=pave_category['category'])
        report.secondary_category = ReportCategory.objects.get(id=pave_category['secondary_category'])


    def set_address(self, report, row):
        # Set point
        y = float(row[self.PAVE_LAT_IDX].replace(',','.'))
        x = float(row[self.PAVE_LONG_IDX].replace(',','.'))

        point = Point(x=x, y=y, srid=4326)
        report.point = point

        # Fetch address from urbis
        # xy has to be inverted
        json_data = {
            "point": {
                "x": y,
                "y": x
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

        if address_nl:
            report.address_nl = address_nl.get('address').get('street').get('name')
            report.address_number = address_nl.get('address').get('number')
            report.postalcode = address_nl.get('address').get('street').get('postCode')

    def _get_urbis_address(self, json_data):
        response = requests.get("http://geoservices.irisnet.be/localization/Rest/Localize/getaddressfromxy?json=" + json.dumps(json_data))

        if response.status_code == requests.codes.ok:
            return response.json().get('result')

        logger.error('Address cannot be fetched from urbis')
        return None


    def set_description(self, report, row):
        description = "{} - {}: {}".format(
            self._get_pave_id(row),
            row[self.PAVE_CATEGORY_IDX],
            row[self.PAVE_SOLUTION_IDX]
        )

        comment = ReportComment(
            text=description,
            security_level=ReportComment.PRIVATE,
            report=report,
            created_by=self._get_pave_user()
        )
        comment.bypassNotification = True
        comment.save()


    def set_history(self, report, row):
        ReportEventLog(
            report=report,
            event_type=ReportEventLog.CREATED,
            user=self._get_pave_user(),
            related_new=report.responsible_department
        ).save()


    def set_external_id(self, report, row):
        report.contractor_reference_id = self._get_pave_id(row)


    def set_pictures(self, report, row):
        # Generate path and name
        now = datetime.datetime.now()
        picture_name= row[self.PAVE_PICTURE_IDX]
        thumbnail_name = picture_name[:-3] + "thumbnail.JPG"

        path = "files/{}/{}/{}/".format(now.year, now.month, report.id)
        file_path = path + picture_name

        # Move pictures to expected path
        self._move_to_media(picture_name, thumbnail_name, path)

        # Create FMS attachment
        report_file = ReportFile(
            file_type=ReportFile.IMAGE,
            file_creation_date=now,
            title=self._get_pave_id(row),
            report=report,
            file=file_path,
            image=file_path,
            created_by=self._get_pave_user()
        )
        report_file.bypassNotification = True
        report_file.save()

    def _move_to_media(self, picture_name, thumbnail_name, path):
        target_path = "{}".format(self.pictures_folder) + "/" + path

        subprocess.call("mkdir -p {}".format(target_path), shell=True)
        subprocess.call("cp {}/{} {}/{}".format(self.pictures_folder, picture_name, target_path, picture_name), shell=True)
        subprocess.call("cp {}/{} {}/{}".format(self.pictures_folder, thumbnail_name, target_path, thumbnail_name), shell=True)
        subprocess.call("cp -r {}/files {}".format(self.pictures_folder, settings.MEDIA_ROOT), shell=True)

    def set_regional_flag(self, report, row):
        template_url = 'http://geoservices-urbis.irisnet.be/geoserver/wfs?service=wfs&request=GetFeature&version=2.0&typeName=UrbisAdm:Ss&outputFormat=application/json&FILTER=<Filter xmlns="http://www.opengis.net/ogc" xmlns:gml="http://www.opengis.net/gml"><Intersects><PropertyName>GEOM</PropertyName><gml:Point srsName="EPSG:4326"><gml:coordinates>coord_x,coord_y</gml:coordinates></gml:Point></Intersects></Filter>&propertyName=SSA_ADMIN,SSA_DESCRIPTION_FRE'

        template_url = template_url.replace("coord_x", str(report.point.x))
        template_url = template_url.replace("coord_y", str(report.point.y))

        response = requests.get(template_url)

        if response.status_code == requests.codes.ok:
            try:
                feature = response.json()['features'][0]

                if feature['properties']['SSA_ADMIN'] in ["REGION", "33"]:
                    report.address_regional = True
                    report.responsible_entity = self.region_entity

                    logger.info('   Address is regional: ' + feature['properties']['SSA_ADMIN'])
            except AttributeError:
                pass
            except IndexError:
                pass
