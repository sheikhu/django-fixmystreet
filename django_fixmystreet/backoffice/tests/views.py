from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from django_fixmystreet.fixmystreet.models import Report, ReportCategory, OrganisationEntity, FMSUser

class ReportProViewsTest(TestCase):

    fixtures = ["bootstrap","list_items"]

    def setUp(self):
        self.user = User.objects.create_user(username='test1', email='test1@fixmystreet.irisnet.be', password='test')
        self.user.save()
        self.client = Client()
        self.citizen = FMSUser(
            telephone="0123456789",
            last_used_language="fr",
            first_name="citizen",
            last_name="citizen",
            email="citizen@a.com"
        )
        self.citizen.save()

        self.manager = FMSUser(
            is_active=True,
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
        self.manager.categories.add(ReportCategory.objects.get(pk=1))

        self.super_user = FMSUser(
            is_active=True,
            telephone="0123456789",
            last_used_language="fr",
            first_name="superuser",
            last_name="superuser",
            email="superuser@a.com"
        )
        self.super_user.set_password('test')
        self.super_user.is_superuser = True
        self.super_user.save()

        self.sample_post = {
            'report-x':'150056.538',
            'report-y':'170907.56',
            'report-address_fr':'Avenue des Arts, 3',
            'report-address_nl':'Kunstlaan, 3',
            'report-address_number':'3',
            'report-postalcode':'1210',
            'report-category':'1',
            'report-secondary_category':'1',
            'report-subscription':'on',
            'comment-text':'test',
            'files-TOTAL_FORMS': 0,
            'files-INITIAL_FORMS': 0,
            'files-MAX_NUM_FORMS': 0,
            'citizen-email':self.citizen.email,
            'citizen-firstname':self.citizen.first_name,
            'citizen-lastname':self.citizen.last_name,
            'citizen-quality':'1',
            'report-terms_of_use_validated': True
        }

    #~ def test_list_contractor(self):
        #~ """Tests list of contractors."""
        #~ self.client.login(username='manager@a.com', password='test')
#~
        #~ self.organisation = OrganisationEntity(name="Dummy Organisation", commune=False, region=False, subcontractor=True, applicant=False, dependency=self.manager.organisation, feature_id = 5)
        #~ self.organisation.save()
#~
        #~ response = self.client.get(reverse('list_contractors'))
        #~ self.assertEquals(response.status_code, 200)
#~
        #~ contractors = response.context['contractors']
        #~ self.assertTrue(len(contractors))
#~
    #~ def test_list_contractor_superuser(self):
        #~ """Tests list of contractors if superuser."""
        #~ self.client.login(username='superuser@a.com', password='test')
#~
        #~ self.organisation = OrganisationEntity(name="Dummy Organisation", commune=False, region=False, subcontractor=True, applicant=False)
        #~ self.organisation.save()
#~
        #~ response = self.client.get(reverse('list_contractors'))
        #~ self.assertEquals(response.status_code, 200)
#~
        #~ contractors = response.context['contractors']
        #~ self.assertTrue(len(contractors))
#~
    #~ def test_list_contractor_unauth(self):
        #~ """Tests list of contractors if unauth."""
        #~ self.organisation = OrganisationEntity(name="Dummy Organisation", commune=False, region=False, subcontractor=True, applicant=False)
        #~ self.organisation.save()
#~
        #~ response = self.client.get(reverse('list_contractors'))
        #~ self.assertEquals(response.status_code, 302)
