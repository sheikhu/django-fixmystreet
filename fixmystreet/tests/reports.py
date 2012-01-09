from datetime import date

from django.test import TestCase
from django.contrib.auth.models import User
from django.core import mail

from fixmystreet.models import Report, ReportUpdate, ReportSubscription, ReportNotification, ReportCategory, ReportCategoryClass, Ward, City, Councillor


class ReportsTest(TestCase):
    fixtures = ['sample']
    def setUp(self):
        self.user = User.objects.create_user('admin', 'test@fixmystreet.irisnet.be', 'pwd')
        self.user.save()

    #def test_reportupdate_order(self):
        #report = Report.objects.all()[0]
        #for u in report.reportupdate_set.all():
            #u.remove()
        #report.reportupdate_set.create(desc="foo",created_at=date(2012,01,02),author=self.user)
        #report.reportupdate_set.create(desc="bar",created_at=date(2012,01,01),author=self.user)
        #
        #self.assertEqual(ReportUpdate.objects.filter(report=report).values_list('created_at',flat=True), [date(2012,01,01),date(2012,01,02)])
        #self.assertEqual(ReportUpdate.objects.filter(report=report).values_list('desc',flat=True), ['bar','foo'])
        #self.assertEqual(report.reportupdate_set.all()[0].values_list('desc',flat=True), ['bar','foo'])


class NotificationTest(TestCase):
    #fixtures = ['test_email_rules.json']
    
    def setUp(self):
        self.user = User.objects.create_user('admin', 'test@fixmystreet.irisnet.be', 'pwd')
        self.user.save()

        # these are from the fixtures file.
        self.categoryclass = ReportCategoryClass.objects.get(name_en='Parks')
        self.category = ReportCategory.objects.get(name_en='Broken or Damaged Equipment/Play Structures')
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

        rule = NotificationtionRule(rule=NotificationRule.TO_COUNCILLOR, ward=self.ward, councillor=self.concillor2)
        rule.save()

        self.report = Report(ward=self.ward, category=self.category, title='Just a second test', author=self.user)
        self.report.save()

        self.assertEqual(ReportNotification.objects.filter(report=self.report,to_councillor=self.councillor).count(),2)
        self.assertTrue(ReportNotification.objects.filter(report=self.report,to_councillor=self.councillor2).exists())
        self.assertEquals(len(mail.outbox), 3)
        self.assertEquals(len(mail.outbox[1].to), 1)
        self.assertEquals(len(mail.outbox[2].to), 1)
        self.assertTrue(self.councillor2.email in mail.outbox[1].to or self.councillor2.email in mail.outbox[2].to)
        self.assertTrue(self.councillor.email in mail.outbox[1].to or self.councillor.email in mail.outbox[2].to)
        
    def testToWardAddress(self):
        email_ward = 'councillor_email@testward1.com'
        email_add = 'park@testward1.com'
        rule = EmailRule( rule=EmailRule.TO_COUNCILLOR, ward = self.test_ward, councillor=Councillor.objects.get(email=email_add) )
        rule.save()
        self.failUnlessEqual( self.test_report.get_emails(), ([email_ward,email_add],[]) )


    def testMatchingCategoryClass(self):
        email = 'park@testward1.com'
        rule = EmailRule( rule=EmailRule.MATCHING_CATEGORY_CLASS, ward = self.test_ward, category_class = self.test_categoryclass, councillor=Councillor.objects.get(email=email) )
        rule.save()
        self.failUnlessEqual( self.test_report.get_emails(), (['councillor_email@testward1.com',email],[]) )
        report2 = Report(ward=self.test_ward,category=self.not_test_category)
        self.failUnlessEqual( report2.get_emails(), (['councillor_email@testward1.com'],[]) )
        

    def testNotMatchingCategoryClass(self):
        email = 'park@testward1.com'
        rule = EmailRule( rule=EmailRule.NOT_MATCHING_CATEGORY_CLASS, ward = self.test_ward, category_class = self.test_categoryclass, councillor=Councillor.objects.get(email=email) )
        rule.save()
        self.failUnlessEqual( self.test_report.get_emails(), (['councillor_email@testward1.com'],[]) )

        report2 = Report(ward=self.test_ward,category=self.not_test_category)
        self.failUnlessEqual( report2.get_emails(), (['councillor_email@testward1.com',email],[]) )

        report3 = Report(ward=self.test_ward,category=self.not_test_category)
        rule = EmailRule( rule=EmailRule.NOT_MATCHING_CATEGORY_CLASS, ward=self.test_ward, category_class=self.not_test_category.category_class, councillor=self.test_ward.councillor)
        rule.save()
        self.failUnlessEqual( report3.get_emails(), ([email],[]) )


    def testMultiRecipients(self):
        parks_category = ReportCategory.objects.get(name_en='Lights Malfunctioning in Park')
        not_parks_category = ReportCategory.objects.get(name_en='Damaged Curb')
        tree_category = ReportCategory.objects.get(name_en='Branches Blocking Signs or Intersection')

        parks_category_class = parks_category.category_class
        trees_category_class = tree_category.category_class
        
        park_c     = Councillor.objects.get(email='park@testward1.com')
        non_park_c = Councillor.objects.get(email='non-park@testward1.com')
        void_c     = Councillor.objects.get(email='void@testward1.com')

        # always CC the councillor
        EmailRule(ward = self.test_ward, councillor=void_c,     rule=EmailRule.TO_COUNCILLOR,               is_cc=True).save()
        EmailRule(ward = self.test_ward, councillor=park_c,     rule=EmailRule.MATCHING_CATEGORY_CLASS,     category_class = parks_category_class).save()
        EmailRule(ward = self.test_ward, councillor=non_park_c, rule=EmailRule.NOT_MATCHING_CATEGORY_CLASS, category_class = parks_category_class).save()
        EmailRule(ward = self.test_ward, councillor=non_park_c, rule=EmailRule.NOT_MATCHING_CATEGORY_CLASS, category_class = trees_category_class).save()

        self.test_report.category = parks_category
        self.failUnlessEqual( self.test_report.get_emails(), (['councillor_email@testward1.com','park@testward1.com'], ['void@testward1.com']) )
        self.test_report.category = tree_category
        self.failUnlessEqual( self.test_report.get_emails(), (['councillor_email@testward1.com'], ['void@testward1.com']) )
        self.test_report.category = not_parks_category
        self.failUnlessEqual( self.test_report.get_emails(), (['councillor_email@testward1.com', 'non-park@testward1.com'], ['void@testward1.com']) )
