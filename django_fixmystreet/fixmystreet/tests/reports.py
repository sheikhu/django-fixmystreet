from datetime import date
import shutil, os
#from unittest import skip

from django.test import TestCase
from django.contrib.auth.models import User
from django.core import mail
from django.core.files.storage import FileSystemStorage

from django.conf import settings
from django_fixmystreet.fixmystreet.models import Report, ReportSubscription, ReportNotification, ReportCategory, ReportMainCategoryClass, OrganisationEntity, FMSUser, ReportFile


class NotificationTest(TestCase):
    
    fixtures = ["bootstrap","list_items"]
    
    def setUp(self):
        self.user = User.objects.create_user('admin', 'test@fixmystreet.irisnet.be', 'pwd')
        self.user.save()
        self.category = ReportMainCategoryClass.objects.all()[0] 
        #Create a FMSUser
        self.fmsuser = FMSUser(telephone="0123456789", last_used_language="fr", agent=False, manager=False, leader=False, impetrant=False, contractor=False)
        self.fmsuser.save();
        self.commune = OrganisationEntity(name='test ward')
    
    def testReportFileType(self):
        new_report = Report(status=Report.CREATED, category=self.category, description='Just a test', creator=self.user, postalcode = 1000, responsible_manager=self.fmsuser)
        
        reportFile = ReportFile(file_type=ReportFile.PDF, report = new_report, creator=self.user)
        self.assertTrue(reportFile.is_pdf())
        self.assertFalse(reportFile.is_word())
        self.assertFalse(reportFile.is_excel())
        self.assertFalse(reportFile.is_image())
        self.assertTrue(reportFile.is_a_document())
        self.assertFalse(reportFile.is_an_image())
        
        reportFile = ReportFile(file_type=ReportFile.WORD, report = new_report, creator=self.user)
        self.assertFalse(reportFile.is_pdf())
        self.assertTrue(reportFile.is_word())
        self.assertFalse(reportFile.is_excel())
        self.assertFalse(reportFile.is_image())
        self.assertTrue(reportFile.is_a_document())
        self.assertFalse(reportFile.is_an_image())
        
        reportFile = ReportFile(file_type=ReportFile.EXCEL, report = new_report, creator=self.user)
        self.assertFalse(reportFile.is_pdf())
        self.assertFalse(reportFile.is_word())
        self.assertTrue(reportFile.is_excel())
        self.assertFalse(reportFile.is_image())
        self.assertTrue(reportFile.is_a_document())
        self.assertFalse(reportFile.is_an_image())
        
        reportFile = ReportFile(file_type=ReportFile.IMAGE, report = new_report, creator=self.user)
        self.assertFalse(reportFile.is_pdf())
        self.assertFalse(reportFile.is_word())
        self.assertFalse(reportFile.is_excel())
        self.assertTrue(reportFile.is_image())
        self.assertFalse(reportFile.is_a_document())
        self.assertTrue(reportFile.is_an_image())

    #@skip("to conform")
    #def testToCouncillor(self):
    #    self.report = Report(ward=self.ward, category=self.category, title='Just a test', author=self.user)
    #    self.report.save()

    #    self.assertTrue(ReportNotification.objects.filter(report=self.report,to_councillor=self.councillor).exists())
    #    self.assertEquals(len(mail.outbox), 1)
    #    self.assertEquals(len(mail.outbox[0].to), 1)
    #    self.assertEquals(mail.outbox[0].to, [self.councillor.email])

    #    rule = NotificationRule(rule=NotificationRule.TO_COUNCILLOR, ward=self.ward, councillor=self.councillor2)
    #    rule.save()

    #    self.report = Report(ward=self.ward, category=self.category, title='Just a second test', author=self.user)
    #    self.report.save()

    #    self.assertTrue(ReportNotification.objects.filter(report=self.report,to_councillor=self.councillor).exists())
    #    self.assertTrue(ReportNotification.objects.filter(report=self.report,to_councillor=self.councillor2).exists())
    #    self.assertEquals(len(mail.outbox), 3)
    #    self.assertEquals(len(mail.outbox[1].to), 1)
    #    self.assertEquals(len(mail.outbox[2].to), 1)
    #    self.assertTrue(self.councillor2.email in mail.outbox[1].to or self.councillor2.email in mail.outbox[2].to)
    #    self.assertTrue(self.councillor.email in mail.outbox[1].to or self.councillor.email in mail.outbox[2].to)

    #@skip("to conform")
    #def testMatchingCategoryClass(self):
    #    rule = NotificationRule(rule=NotificationRule.MATCHING_CATEGORY_CLASS, ward=self.ward, category_class=self.categoryclass, councillor=self.councillor2)
    #    rule.save()

    #    self.report = Report(ward=self.ward, category=self.category, title='Just a test', author=self.user)
    #    self.report.save()

    #    self.assertTrue(ReportNotification.objects.filter(report=self.report,to_councillor=self.councillor).exists())
    #    self.assertTrue(ReportNotification.objects.filter(report=self.report,to_councillor=self.councillor2).exists())
    #    self.assertEquals(len(mail.outbox), 2)
    #    self.assertEquals(len(mail.outbox[0].to), 1)
    #    self.assertEquals(len(mail.outbox[1].to), 1)
    #    self.assertEquals(mail.outbox[0].to, [self.councillor.email])
    #    self.assertEquals(mail.outbox[1].to, [self.councillor2.email])

    #    self.report2 = Report(ward=self.ward, category=self.not_category, title='Just a second test', author=self.user)
    #    self.report2.save()

    #    self.assertFalse(ReportNotification.objects.filter(report=self.report2,to_councillor=self.councillor2).exists())
    #    self.assertEquals(len(mail.outbox), 3)
    #    self.assertEquals(len(mail.outbox[2].to), 1)
    #    self.assertEquals(mail.outbox[2].to, [self.councillor.email])
        

    #@skip("to conform")
    #def testNotMatchingCategoryClass(self):
    #    rule = NotificationRule(rule=NotificationRule.NOT_MATCHING_CATEGORY_CLASS, ward = self.ward, category_class = self.categoryclass, councillor=self.councillor2)
    #    rule.save()

    #    self.report = Report(ward=self.ward, category=self.category, title='Just a test', author=self.user)
    #    self.report.save()

    #    self.assertTrue(ReportNotification.objects.filter(report=self.report,to_councillor=self.councillor).exists())
    #    self.assertFalse(ReportNotification.objects.filter(report=self.report,to_councillor=self.councillor2).exists())
    #    self.assertEquals(len(mail.outbox), 1)
    #    self.assertEquals(mail.outbox[0].to, [self.councillor.email])

    #    self.report2 = Report(ward=self.ward, category=self.not_category, title='Just a second test', author=self.user)
    #    self.report2.save()

    #    self.assertTrue(ReportNotification.objects.filter(report=self.report2,to_councillor=self.councillor2).exists())
    #    self.assertEquals(len(mail.outbox), 3)
    #    self.assertEquals(mail.outbox[1].to, [self.councillor.email])
    #    self.assertEquals(mail.outbox[2].to, [self.councillor2.email])

    #@skip("to conform")
    #def testSubscrciber(self):
    #    self.report = Report(ward=self.ward, category=self.category, title='Just a test', author=self.user)
    #    self.report.save()

    #    self.assertTrue(ReportSubscription.objects.filter(report=self.report,subscriber=self.user).exists())


class PhotosTest(TestCase):

    fixtures = ["bootstrap","list_items"]

    def setUp(self):
        self.user = User.objects.create_user('test', 'test@fixmystreet.irisnet.be', 'pwd')
        self.user.save()
        self.category = ReportMainCategoryClass.objects.all()[0] 
        #Create a FMSUser
        self.fmsuser = FMSUser(telephone="0123456789", last_used_language="fr", agent=False, manager=False, leader=False, impetrant=False, contractor=False)
        self.fmsuser.save();
        #self.ward = Ward.objects.all()[0]

    def testPhotoExifData(self):
        
        imgs_to_test = ({
            'path': 'top-left-1.jpg',
            'orientation': 1
        },{
            'path': 'top-right-6.jpg',
            'orientation': 6
        },{
            'path': 'bottom-left-8.jpg',
            'orientation': 8
        },{
            'path': 'bottom-right-3.jpg',
            'orientation': 3
        })

        for img in imgs_to_test:
            path = os.path.join(settings.MEDIA_ROOT, 'photos-test', img['path'])
            
            shutil.copyfile(path, os.path.join(settings.MEDIA_ROOT, 'tmp.jpg'))
            
            #report = Report(ward=self.ward, category=self.category, title='Just a test', author=self.user)
            report = Report(status=Report.CREATED, category=self.category, description='Just a test', creator=self.user, postalcode = 1000, responsible_manager=self.fmsuser)

            report.photo = 'tmp.jpg'
            report.save()

            self.assertEquals(report.photo.url, '{0}photos/photo_{1}.jpeg'.format(settings.MEDIA_URL, report.id))

            from PIL import Image, ImageOps
            from django_fixmystreet.fixmystreet.utils import get_exifs

            former_img = Image.open(path)
            exifs = get_exifs(former_img)
            self.assertTrue('Orientation' in exifs)
            self.assertEquals(exifs['Orientation'], img['orientation'])

            new_img = Image.open(report.photo.path)
            exifs = get_exifs(new_img)
            self.assertTrue('Orientation' not in exifs)
            
            # former_pix = former_img.load()
            # new_pix = new_img.load()
            # self.assertEquals(former_pix[0,0],new_pix[0,0]) # no image rotation but resized, how to test it ??
            # TODO check the image is correctly rotated


