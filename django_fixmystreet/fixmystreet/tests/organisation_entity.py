
from django.test import TestCase

from django_fixmystreet.fixmystreet.models import OrganisationEntity


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
       self.assertFalse(self.organisation.commune)
       self.assertFalse(self.organisation.region)
       self.assertFalse(self.organisation.subcontractor)
       self.assertFalse(self.organisation.applicant)
    
    def testOrganisationDependency(self):
       '''Test the organisation dependency'''
       self.assertTrue(self.organisation_dependency.id > 0)
