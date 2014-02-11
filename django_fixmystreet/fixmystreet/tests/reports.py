
from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import Client

from django_fixmystreet.fixmystreet.models import Report, ReportCategory, ReportMainCategoryClass, OrganisationEntity, FMSUser, ReportFile, UserOrganisationMembership
from django_fixmystreet.fixmystreet.utils import dict_to_point


class NotificationTest(TestCase):

    fixtures = ["bootstrap", "list_items"]

    def setUp(self):
        self.secondary_category = ReportCategory.objects.all()[0]
        self.category = self.secondary_category.category_class
        #Create a FMSUser
        self.etterbeek = OrganisationEntity.objects.get(id=5)  # postal code = 1040 Etterbeek
        self.etterbeek.save()
        self.bxl = OrganisationEntity.objects.get(id=4)  # postal code = 1000 Bxl
        self.bxl.save()
        self.manager_etterbeek = FMSUser(
            is_active=True,
            email="manager@etterbeek.be",
            telephone="0123456789",
            last_used_language="fr",
            manager=True,
            organisation=self.etterbeek)
        self.manager_etterbeek.save()
        self.manager_bxl = FMSUser(
            is_active=True,
            email="manager@bxl.be",
            telephone="0123456789",
            last_used_language="fr",
            manager=True,
            organisation=self.bxl)
        self.manager_bxl.save()
        self.group = OrganisationEntity(
            type="D",
            name_nl="Werken",
            name_fr="Travaux",
            phone="090987",
            dependency=self.bxl,
            email="test@email.com"
            )
        self.group.save()
        self.usergroupmembership = UserOrganisationMembership(user_id=self.manager_bxl.id, organisation_id=self.group.id, contact_user=True)
        self.usergroupmembership.save()
        self.group2 = OrganisationEntity(
            type="D",
            name_nl="Werken",
            name_fr="Travaux",
            phone="090987",
            dependency=self.etterbeek,
            email="test@email.com"
            )
        self.group2.save()
        self.usergroupmembership2 = UserOrganisationMembership(user_id=self.manager_etterbeek.id, organisation_id=self.group2.id, contact_user=True)
        self.usergroupmembership2.save()
        self.citizen = FMSUser(
            email="citizen@fms.be",
            telephone="0123456789",
            last_used_language="fr")
        self.citizen.save()

    def testReportFileType(self):
        new_report = Report(status=Report.CREATED, category=self.category, description='Just a test', postalcode=1000, responsible_manager=self.manager_bxl)

        reportFile = ReportFile(file_type=ReportFile.PDF, report=new_report)
        self.assertTrue(reportFile.is_pdf())
        self.assertFalse(reportFile.is_word())
        self.assertFalse(reportFile.is_excel())
        self.assertFalse(reportFile.is_image())
        self.assertTrue(reportFile.is_document())

        reportFile = ReportFile(file_type=ReportFile.WORD, report=new_report)
        self.assertFalse(reportFile.is_pdf())
        self.assertTrue(reportFile.is_word())
        self.assertFalse(reportFile.is_excel())
        self.assertFalse(reportFile.is_image())
        self.assertTrue(reportFile.is_document())

        reportFile = ReportFile(file_type=ReportFile.EXCEL, report=new_report)
        self.assertFalse(reportFile.is_pdf())
        self.assertFalse(reportFile.is_word())
        self.assertTrue(reportFile.is_excel())
        self.assertFalse(reportFile.is_image())
        self.assertTrue(reportFile.is_document())

        reportFile = ReportFile(file_type=ReportFile.IMAGE, report=new_report)
        self.assertFalse(reportFile.is_pdf())
        self.assertFalse(reportFile.is_word())
        self.assertFalse(reportFile.is_excel())
        self.assertTrue(reportFile.is_image())
        self.assertFalse(reportFile.is_document())

    def testReportResponsibleAssignment(self):
        '''Test the assignment of a responsible when creating a report'''
        #When a responsible_manager is defined responsible_entity is not recomputed
        new_report = Report(
            status=Report.CREATED,
            secondary_category=self.secondary_category,
            category=self.category,
            description='Just a test',
            postalcode=1000,
            address='my address',
            point=dict_to_point({"x": '149776', "y": '170005'}),
            address_number='6h',
            created_by=self.manager_etterbeek
        )
        new_report.save()
        # when created by pro report is under responsibility of etterbeek, not bxl
        self.assertEquals(new_report.responsible_entity, self.etterbeek)
        #self.assertEquals(new_report.responsible_manager, self.manager_etterbeek)

        new_report = Report(
            status=Report.CREATED,
            secondary_category=self.secondary_category,
            category=self.category,
            description='Just a test',
            postalcode=1000,
            address='my address',
            point=dict_to_point({"x": '149776', "y": '170005'}),
            address_number='6h',
            citizen=self.citizen
        )
        new_report.save()
        # when created by citizen, postalcode used for resonsible
        self.assertEquals(new_report.responsible_entity, self.bxl)
        #self.assertEquals(new_report.responsible_manager, self.manager_bxl)


class PhotosTest(TestCase):

    fixtures = ["bootstrap", "list_items"]

    def setUp(self):
        self.user = User.objects.create_user('test', 'test@fixmystreet.irisnet.be', 'pwd')
        self.user.save()
        self.category = ReportMainCategoryClass.objects.all()[0]
        #Create a FMSUser
        self.fmsuser = FMSUser(telephone="0123456789", last_used_language="fr", agent=False, manager=False, leader=False, applicant=False, contractor=False)
        self.fmsuser.save()
        #self.ward = Ward.objects.all()[0]


class ValueUpdate(TestCase):

    fixtures = ["bootstrap", "list_items"]

    def setUp(self):
        self.secondary_category = ReportCategory.objects.all()[0]
        self.category = self.secondary_category.category_class
        #Create a FMSUser
        self.etterbeek = OrganisationEntity.objects.get(id=5)  # postal code = 1040 Etterbeek
        self.etterbeek.save()
        self.bxl = OrganisationEntity.objects.get(id=4)  # postal code = 1000 Bxl
        self.bxl.save()
        self.manager_etterbeek = FMSUser(email="manager@etterbeek.be", telephone="0123456789", last_used_language="fr", manager=True, organisation=self.etterbeek)
        self.manager_etterbeek.save()
        self.manager_bxl = FMSUser(email="manager@bxl.be", telephone="0123456789", last_used_language="fr", manager=True, organisation=self.bxl)
        self.manager_bxl.save()
        self.citizen = FMSUser(email="citizen@fms.be", telephone="0123456789", last_used_language="fr")
        self.citizen.save()
        self.client = Client()
        self.manager = FMSUser(
            telephone="0123456789",
            last_used_language="fr",
            password='test',
            first_name="manager",
            last_name="manager",
            email="manager@a.com",
            manager=True
        )
        self.manager.set_password('test')
        self.manager.organisation = OrganisationEntity.objects.get(pk=14)
        self.manager.save()

    #def testPhotoExifData(self):
    #
    #    imgs_to_test = ({
    #        'path': 'top-left-1.jpg',
    #        'orientation': 1
    #    },{
    #        'path': 'top-right-6.jpg',
    #        'orientation': 6
    #    },{
    #        'path': 'bottom-left-8.jpg',
    #        'orientation': 8
    #    },{
    #        'path': 'bottom-right-3.jpg',
    #        'orientation': 3
    #    })
    #
    #    for img in imgs_to_test:
    #        path = os.path.join(settings.MEDIA_ROOT, 'photos-test', img['path'])
    #
    #        shutil.copyfile(path, os.path.join(settings.MEDIA_ROOT, 'tmp.jpg'))
    #
            #report = Report(ward=self.ward, category=self.category, title='Just a test', author=self.user)
    #        report = Report(status=Report.CREATED, category=self.category, description='Just a test', postalcode = 1000, responsible_manager=self.fmsuser)

    #        report.photo = 'tmp.jpg'
    #        report.save()

    #        self.assertEquals(report.photo.url, '{0}photos/photo_{1}.jpeg'.format(settings.MEDIA_URL, report.id))

    #        from PIL import Image, ImageOps
    #        from django_fixmystreet.fixmystreet.utils import get_exifs

    #        former_img = Image.open(path)
    #        exifs = get_exifs(former_img)
    #        self.assertTrue('Orientation' in exifs)
    #        self.assertEquals(exifs['Orientation'], img['orientation'])

    #        new_img = Image.open(report.photo.path)
    #        exifs = get_exifs(new_img)
    #        self.assertTrue('Orientation' not in exifs)

            # former_pix = former_img.load()
            # new_pix = new_img.load()
            # self.assertEquals(former_pix[0,0],new_pix[0,0]) # no image rotation but resized, how to test it ??
            # TODO check the image is correctly rotated


