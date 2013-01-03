from datetime import date
import shutil, os
#from unittest import skip

from django.test import TestCase
from django.contrib.auth.models import User
from django.core import mail
from django.core.files.storage import FileSystemStorage

from django.conf import settings
from django_fixmystreet.fixmystreet.models import Report, ReportSubscription, ReportNotification, ReportCategory, ReportMainCategoryClass, OrganisationEntity, FMSUser
from django.db import IntegrityError

class FMSUserTest(TestCase):
    
    fixtures = ["bootstrap","list_items"]

    def setUp(self):
       self.user = User.objects.create_user('admin', 'test@fixmystreet.irisnet.be', 'pwd')
       self.user.save()

       # these are from the fixtures file.
       self.category = ReportCategory.objects.all()[0]
       self.categoryclass = self.category.category_class

       self.commune = OrganisationEntity(name='test ward')
       #Create a FMSUser
       self.fmsuser = FMSUser(telephone="0123456789", last_used_language="fr", agent=False, manager=False, leader=False, applicant=False, contractor=False, username="aaa", first_name="aaa", last_name="aaa", email="a@a.com")
       self.fmsuser.save();

    def testCreationOfFMSUser(self):
       '''Create a user and check if the row in database has been created'''
       self.assertTrue(self.fmsuser.id > 0)
    
    def testFMSCitizenOrProRole(self):
       '''Test the roles of the FMSUser created'''
       self.assertTrue(self.fmsuser.is_citizen())
       self.assertFalse(self.fmsuser.is_pro())
       self.fmsuser.agent = True
       self.assertFalse(self.fmsuser.is_citizen())
       self.assertTrue(self.fmsuser.is_pro())
       self.fmsuser.agent = False
       self.fmsuser.manager = True 
       self.assertFalse(self.fmsuser.is_citizen())
       self.assertTrue(self.fmsuser.is_pro())
       self.fmsuser.manager = False
       self.fmsuser.leader = True 
       self.assertFalse(self.fmsuser.is_citizen())
       self.assertTrue(self.fmsuser.is_pro())
       self.fmsuser.leader = False
       self.fmsuser.applicant = True 
       self.assertFalse(self.fmsuser.is_citizen())
       self.assertTrue(self.fmsuser.is_pro())
       self.fmsuser.applicant = False
       self.fmsuser.contractor = True 
       self.assertFalse(self.fmsuser.is_citizen())
       self.assertTrue(self.fmsuser.is_pro())
       self.fmsuser.contractor = False
       self.assertTrue(self.fmsuser.is_citizen())
       self.assertFalse(self.fmsuser.is_pro())
    
    def testFMSLanguage(self):
       '''Test the user language'''
       self.assertEquals(self.fmsuser.last_used_language, "fr")
    
    def testFMSSpecificRoles(self):
       '''Test the user roles boolean values'''
       self.assertFalse(self.fmsuser.agent)
       self.assertFalse(self.fmsuser.manager)
       self.assertFalse(self.fmsuser.leader)
       self.assertFalse(self.fmsuser.applicant)
       self.assertFalse(self.fmsuser.contractor)
       self.fmsuser.agent = True 
       self.fmsuser.manager = True 
       self.fmsuser.leader = True 
       self.fmsuser.applicant = True 
       self.fmsuser.contractor = True 
       self.assertTrue(self.fmsuser.agent)
       self.assertTrue(self.fmsuser.manager)
       self.assertTrue(self.fmsuser.leader)
       self.assertTrue(self.fmsuser.applicant)
       self.assertTrue(self.fmsuser.contractor)
