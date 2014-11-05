from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from django_fixmystreet.fixmystreet.models import Report, ReportCategory, OrganisationEntity, FMSUser
from django_fixmystreet.fixmystreet.tests import FMSTestCase

class ReportProViewsTest(FMSTestCase):

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
