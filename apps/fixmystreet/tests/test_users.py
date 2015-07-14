from django.contrib.auth.models import User

from apps.fixmystreet.models import FMSUser
from apps.fixmystreet.tests import FMSTestCase
from apps.fixmystreet.forms import CitizenForm

class FMSUserTest(FMSTestCase):

    def setUp(self):
        # Create a FMSUser
        self.fmsuser = FMSUser(
            telephone="0123456789",
            last_used_language="fr",
            username="aaa",
            first_name="aaa",
            last_name="aaa",
            email="a@a.com")
        self.fmsuser.save()

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

    def test_double_citizen_case_insensitive(self):
        citizen_data = {
            "email"    : "user@fms.be",
            "last_name": "user",
            "telephone": "123456789",
            "quality"  : 1
        }

        # Create first citizen
        citizen_form = CitizenForm(citizen_data)

        # Form has to be valid
        self.assertTrue(citizen_form.is_valid())
        citizen_form.save()

        # Create second citizen with a caps in email
        citizen_data['email'] = citizen_data['email'].upper()
        citizen_form          = CitizenForm(citizen_data)

        # Form has to be valid
        self.assertTrue(citizen_form.is_valid())
        citizen_form.save()

        # And only one user with the same email case insensitive is created (it's the same citizen in both cases)
        self.assertEqual(1, FMSUser.objects.filter(username__iexact=citizen_data['email']).count())

    def test_citizen_with_pro_email(self):
        manager = FMSUser(
            is_active=True,
            telephone="0123456789",
            last_used_language="fr",
            password='test',
            first_name="manager",
            last_name="manager",
            email="manager@a.com",
            manager=True
        )
        manager.save()

        citizen_data = {
            "email"    : manager.email,
            "last_name": "user",
            "telephone": "123456789",
            "quality"  : 1
        }

        # Create a citizen user
        citizen_form = CitizenForm(citizen_data)

        # Form has to be INVALID because the citizen use a pro email
        self.assertFalse(citizen_form.is_valid())
        self.assertTrue(citizen_form.errors)
