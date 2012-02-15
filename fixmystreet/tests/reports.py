from datetime import date

from django.test import TestCase
from django.contrib.auth.models import User
from django.core import mail

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
#
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
