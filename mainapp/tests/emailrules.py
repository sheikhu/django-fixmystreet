"""
"""

from django.test import TestCase
from mainapp.models import Report,ReportUpdate,EmailRule, City, Ward,ReportCategory,ReportCategoryClass, Councillor

class TestRules(TestCase):
    fixtures = ['test_email_rules.json']
    
    def setUp(self):
        # these are from the fixtures file.
        self.test_categoryclass = ReportCategoryClass.objects.get(name_en='Parks')
        self.test_category = ReportCategory.objects.get(name_en='Broken or Damaged Equipment/Play Structures')
        self.not_test_category = ReportCategory.objects.get(name_en='Damaged Curb')

        self.test_ward = Ward.objects.get(name = 'Ward1')
        self.test_report = Report(ward=self.test_ward,category=self.test_category)

        
    def testToCouncillor(self):
        self.failUnlessEqual( self.test_report.get_emails(), (['councillor_email@testward1.com'],[]) )

        self.test_report.ward = Ward.objects.get(name='Ward2')
        self.failUnlessEqual( self.test_report.get_emails(), (['void@testward1.com'],[]) )

        rule = EmailRule( rule = EmailRule.TO_COUNCILLOR, ward = self.test_report.ward, councillor=self.test_ward.councillor )
        rule.save()
        self.failUnlessEqual( self.test_report.get_emails(), (['void@testward1.com','councillor_email@testward1.com'],[]) )
        
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

