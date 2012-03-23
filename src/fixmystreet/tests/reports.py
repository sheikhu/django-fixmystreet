from datetime import date
import shutil, os

from django.test import TestCase
from django.contrib.auth.models import User
from django.core import mail
from django.core.files.storage import FileSystemStorage

import settings
from fixmystreet.models import Report, ReportUpdate, ReportSubscription, ReportNotification, NotificationRule, ReportCategory, ReportCategoryClass, Ward, City, Councillor


class NotificationTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user('admin', 'test@fixmystreet.irisnet.be', 'pwd')
        self.user.save()

        # these are from the fixtures file.
        self.category = ReportCategory.objects.get(name_en='Broken or Damaged Equipment/Play Structures')
        self.categoryclass = self.category.category_class
        self.not_category = ReportCategory.objects.get(name_en='Damaged Curb')

        self.councillor = Councillor(name='Test councillor', email='test@fixmystreet.irisnet.be')
        self.councillor.save()
        self.councillor2 = Councillor(name='Test councillor 2', email='test2@fixmystreet.irisnet.be')
        self.councillor2.save()
        self.ward = Ward(name='test ward',councillor=self.councillor, city=City.objects.all()[0])
        self.ward.save()

    def testToCouncillor(self):
        self.report = Report(ward=self.ward, category=self.category, title='Just a test', author=self.user)
        self.report.save()

        self.assertTrue(ReportNotification.objects.filter(report=self.report,to_councillor=self.councillor).exists())
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertEquals(mail.outbox[0].to, [self.councillor.email])

        rule = NotificationRule(rule=NotificationRule.TO_COUNCILLOR, ward=self.ward, councillor=self.councillor2)
        rule.save()

        self.report = Report(ward=self.ward, category=self.category, title='Just a second test', author=self.user)
        self.report.save()

        self.assertTrue(ReportNotification.objects.filter(report=self.report,to_councillor=self.councillor).exists())
        self.assertTrue(ReportNotification.objects.filter(report=self.report,to_councillor=self.councillor2).exists())
        self.assertEquals(len(mail.outbox), 3)
        self.assertEquals(len(mail.outbox[1].to), 1)
        self.assertEquals(len(mail.outbox[2].to), 1)
        self.assertTrue(self.councillor2.email in mail.outbox[1].to or self.councillor2.email in mail.outbox[2].to)
        self.assertTrue(self.councillor.email in mail.outbox[1].to or self.councillor.email in mail.outbox[2].to)
        
    def testMatchingCategoryClass(self):
        rule = NotificationRule(rule=NotificationRule.MATCHING_CATEGORY_CLASS, ward=self.ward, category_class=self.categoryclass, councillor=self.councillor2)
        rule.save()

        self.report = Report(ward=self.ward, category=self.category, title='Just a test', author=self.user)
        self.report.save()

        self.assertTrue(ReportNotification.objects.filter(report=self.report,to_councillor=self.councillor).exists())
        self.assertTrue(ReportNotification.objects.filter(report=self.report,to_councillor=self.councillor2).exists())
        self.assertEquals(len(mail.outbox), 2)
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertEquals(len(mail.outbox[1].to), 1)
        self.assertEquals(mail.outbox[0].to, [self.councillor.email])
        self.assertEquals(mail.outbox[1].to, [self.councillor2.email])

        self.report2 = Report(ward=self.ward, category=self.not_category, title='Just a second test', author=self.user)
        self.report2.save()

        self.assertFalse(ReportNotification.objects.filter(report=self.report2,to_councillor=self.councillor2).exists())
        self.assertEquals(len(mail.outbox), 3)
        self.assertEquals(len(mail.outbox[2].to), 1)
        self.assertEquals(mail.outbox[2].to, [self.councillor.email])
        

    def testNotMatchingCategoryClass(self):
        rule = NotificationRule(rule=NotificationRule.NOT_MATCHING_CATEGORY_CLASS, ward = self.ward, category_class = self.categoryclass, councillor=self.councillor2)
        rule.save()

        self.report = Report(ward=self.ward, category=self.category, title='Just a test', author=self.user)
        self.report.save()

        self.assertTrue(ReportNotification.objects.filter(report=self.report,to_councillor=self.councillor).exists())
        self.assertFalse(ReportNotification.objects.filter(report=self.report,to_councillor=self.councillor2).exists())
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].to, [self.councillor.email])

        self.report2 = Report(ward=self.ward, category=self.not_category, title='Just a second test', author=self.user)
        self.report2.save()

        self.assertTrue(ReportNotification.objects.filter(report=self.report2,to_councillor=self.councillor2).exists())
        self.assertEquals(len(mail.outbox), 3)
        self.assertEquals(mail.outbox[1].to, [self.councillor.email])
        self.assertEquals(mail.outbox[2].to, [self.councillor2.email])

    def testSubscrciber(self):
        self.report = Report(ward=self.ward, category=self.category, title='Just a test', author=self.user)
        self.report.save()

        self.assertTrue(ReportSubscription.objects.filter(report=self.report,subscriber=self.user).exists())
        # TODO


class PhotosTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('test', 'test@fixmystreet.irisnet.be', 'pwd')
        self.user.save()

        self.category = ReportCategory.objects.all()[0] 
        self.ward = Ward.objects.all()[0]

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
            
            report = Report(ward=self.ward, category=self.category, title='Just a test', author=self.user)

            report.photo = 'tmp.jpg'
            report.save()

            self.assertEquals(report.photo.url, '{0}photos/photo_{1}.jpeg'.format(settings.MEDIA_URL, report.id))

            from PIL import Image, ImageOps
            from fixmystreet.utils import get_exifs

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



    #def testMultiRecipients(self):
        #parks_category = ReportCategory.objects.get(name_en='Lights Malfunctioning in Park')
        #not_parks_category = ReportCategory.objects.get(name_en='Damaged Curb')
        #tree_category = ReportCategory.objects.get(name_en='Branches Blocking Signs or Intersection')
#
        #parks_category_class = parks_category.category_class
        #trees_category_class = tree_category.category_class
        #
        #park_c     = Councillor.objects.get(email='park@testward1.com')
        #non_park_c = Councillor.objects.get(email='non-park@testward1.com')
        #void_c     = Councillor.objects.get(email='void@testward1.com')
#
         #always CC the councillor
        #EmailRule(ward = self.test_ward, councillor=void_c,     rule=EmailRule.TO_COUNCILLOR,               is_cc=True).save()
        #EmailRule(ward = self.test_ward, councillor=park_c,     rule=EmailRule.MATCHING_CATEGORY_CLASS,     category_class = parks_category_class).save()
        #EmailRule(ward = self.test_ward, councillor=non_park_c, rule=EmailRule.NOT_MATCHING_CATEGORY_CLASS, category_class = parks_category_class).save()
        #EmailRule(ward = self.test_ward, councillor=non_park_c, rule=EmailRule.NOT_MATCHING_CATEGORY_CLASS, category_class = trees_category_class).save()
#
        #self.test_report.category = parks_category
        #self.failUnlessEqual( self.test_report.get_emails(), (['councillor_email@testward1.com','park@testward1.com'], ['void@testward1.com']) )
        #self.test_report.category = tree_category
        #self.failUnlessEqual( self.test_report.get_emails(), (['councillor_email@testward1.com'], ['void@testward1.com']) )
        #self.test_report.category = not_parks_category
        #self.failUnlessEqual( self.test_report.get_emails(), (['councillor_email@testward1.com', 'non-park@testward1.com'], ['void@testward1.com']) )
