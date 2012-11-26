from datetime import date
import shutil, os
#from unittest import skip

from django.test import TestCase
from django.contrib.auth.models import User
from django.core import mail
from django.core.files.storage import FileSystemStorage

from django.conf import settings
from django_fixmystreet.fixmystreet.models import Report, ReportSubscription, ReportNotification, ReportCategory, ReportMainCategoryClass, OrganisationEntity, FMSUser


class OrganisationEntityTest(TestCase):
    
    fixtures = ["bootstrap","list_items"]
    
    def setUp(self):
       '''Create organisation test structure'''
       self.organisation_dependency = OrganisationEntity(name="Dependency Organisation", commune=False, region=True, subcontractor=False, applicant=False)
       self.organisation_dependency.save()
       self.organisation = OrganisationEntity(name="Dummy Organisation", commune=False, region=False, subcontractor=False, applicant=False, dependency=self.organisation_dependency, feature_id = 5)
       self.organisation.save()

    def testCreationOfOrganisation(self):
       '''Create an organisation and check if the row in database has been created'''
       self.assertTrue(self.organisation.id > 0)
    
    def testOrganisationRoles(self):
       '''Test the roles of the FMSUser created'''
       self.assertFalse(self.organisation.is_commune())
       self.assertFalse(self.organisation.is_region())
       self.assertFalse(self.organisation.is_subcontractor())
       self.assertFalse(self.organisation.is_applicant())
       
       self.organisation.commune=True
       self.assertTrue(self.organisation.is_commune())
       self.assertFalse(self.organisation.is_region())
       self.assertFalse(self.organisation.is_subcontractor())
       self.assertFalse(self.organisation.is_applicant())
       
       self.organisation.commune=False
       self.organisation.region=True
       self.assertFalse(self.organisation.is_commune())
       self.assertTrue(self.organisation.is_region())
       self.assertFalse(self.organisation.is_subcontractor())
       self.assertFalse(self.organisation.is_applicant())
       
       self.organisation.region=False
       self.organisation.subcontractor=True
       self.assertFalse(self.organisation.is_commune())
       self.assertFalse(self.organisation.is_region())
       self.assertTrue(self.organisation.is_subcontractor())
       self.assertFalse(self.organisation.is_applicant())
       
       self.organisation.subcontractor=False
       self.organisation.applicant=True
       self.assertFalse(self.organisation.is_commune())
       self.assertFalse(self.organisation.is_region())
       self.assertFalse(self.organisation.is_subcontractor())
       self.assertTrue(self.organisation.is_applicant())
    
    def testOrganisationDependency(self):
       '''Test the organisation dependency'''
       self.assertTrue(self.organisation_dependency.id > 0)
