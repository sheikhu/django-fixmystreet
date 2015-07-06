import json
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.gis.geos import Polygon

from apps.fixmystreet.models import (
    Report, OrganisationEntity, FMSUser, ReportCategory,
    UserOrganisationMembership, OrganisationEntitySurface,
    GroupMailConfig
)
from apps.fixmystreet.tests import FMSTestCase

from django.core.exceptions import ObjectDoesNotExist


class ApiTest(FMSTestCase):

    def setUp(self):

        try:
            organisation = OrganisationEntity.objects.get(id=1)
        except ObjectDoesNotExist:
            organisation = OrganisationEntity(id=1, name="Test organisation")
            organisation.save()

        p1 = (148776, 171005)
        p2 = (150776, 171005)
        p3 = (150776, 169005)
        p4 = (148776, 169005)

        surface = OrganisationEntitySurface(
            geom=Polygon([p1, p2, p3, p4, p1]),
            owner=OrganisationEntity.objects.get(pk=14)
        )
        surface.save()

        #user_auth = User.objects.create_user(username='superuser', email='test1@fixmystreet.irisnet.be', password='test')
        #user_auth.save()
        user = FMSUser(
            is_active=True,
            password="test",
            first_name="zaza",
            telephone="00000000",
            last_used_language="fr",
            organisation=organisation,
            username='superuser')
        user.save()

        #~ main_category = ReportMainCategoryClass(id=2,name_en='test main en',name_nl='test main nl',name_fr='test main fr')
        #~ main_category.save()
        #~
        #~ secondary_category = ReportSecondaryCategoryClass(id=2,name_en='test second en',name_nl='test second nl',name_fr='test second fr')
        #~ secondary_category.save()
        #~
        #~ category = ReportCategory(id=2,name_en='test parent en',name_nl='test parent nl',name_fr='test parent fr', public=True, category_class=main_category, secondary_category_class=secondary_category)
        #~ category.save()
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

        self.group = OrganisationEntity(
            type="D",
            name_nl="Werken",
            name_fr="Travaux",
            phone="090987",
            dependency=OrganisationEntity.objects.get(pk=14),
            email="test@email.com"
            )
        self.group.save()

        self.group_mail_config       = GroupMailConfig()
        self.group_mail_config.group = self.group
        self.group_mail_config.save()

        self.usergroupmembership = UserOrganisationMembership(user_id=self.manager.id, organisation_id=self.group.id, contact_user=True)
        self.usergroupmembership.save()

        self.sample_post = {
            'report-x': '150056.538',
            'report-y': '170907.56',
            'report-address_fr': 'Avenue des Arts, 3',
            'report-address_nl': 'Kunstlaan, 3',
            'report-address_number': '3',
            'report-postalcode': '1210',
            'report-category': '1',
            'report-secondary_category': '1',
            'report-subscription': 'on',
            'report-terms_of_use_validated': True,

            'comment-text': 'test',

            'files-TOTAL_FORMS': 0,
            'files-INITIAL_FORMS': 0,
            'files-MAX_NUM_FORMS': 1000,

            'citizen-quality': '1',
            'citizen-email': self.citizen.email,
            'citizen-firstname': self.citizen.first_name,
            'citizen-lastname': self.citizen.last_name
        }

        """
        self.steven = self.users['100003558692539']

        params = {
            'client_id': settings.FACEBOOK_APP_ID,
            'client_secret': settings.FACEBOOK_API_SECRET,
            'grant_type': 'client_credentials'
        }
        url='https://graph.facebook.com/oauth/access_token?{0}'.format(urlencode(params))
        request = Request(url)
        try:
            response = urlparse.parse_qs(urlopen(request).read())
            self.app_access_token = response['access_token'][0]
            #print settings.FACEBOOK_APP_ID,self.app_access_token
        except HTTPError as e:
            print e.code
            print simplejson.loads(e.read())['error']['message']
            raise e

        url = 'https://graph.facebook.com/{0}/accounts/test-users?access_token={1}'\
                .format(settings.FACEBOOK_APP_ID,self.app_access_token)
        try:
            response = simplejson.loads(urlopen(url).read())
            for user in response['data']:
                if user['id'] not in self.users:
                    self.users[user['id']] = {}
                self.users[user['id']]['access_token'] = user['access_token']
            # print self.users
        except HTTPError as e:
            print e.code
            print simplejson.loads(e.read())['error']['message']
            raise e
        """

    def testCreateReportCitizen(self):
        #Create a client to launch requests
        client = Client()

        #Get the request response
        response = client.post(reverse('create_report_citizen'), self.sample_post, follow=True)

        #Test the http response code (200 = OK)
        self.assertEqual(response.status_code, 200)

        #Test if the response if JSON structured.
        self.assertEqual(response['Content-Type'], 'application/json; charset=utf-8')

        self.assertEqual(1, len(Report.objects.all()))

        #Load the response data as JSON object
        result = simplejson.loads(response.content)

        # Get in the DB the created report
        report = Report.objects.get(id=result['id'])

        # Check that source is correct
        self.assertEqual(Report.SOURCES['MOBILE'], report.source)

    def testCreateReportDoubleCitizen(self):
        #Parameters to save the report in database.

        #Create a client to launch requests
        client = Client()
        #Get the request response
        response = client.post(reverse('create_report_citizen'), self.sample_post, follow=True)
        response = client.post(reverse('create_report_citizen'), self.sample_post, follow=True)
        response = client.post(reverse('create_report_citizen'), self.sample_post, follow=True)
        response = client.post(reverse('create_report_citizen'), self.sample_post, follow=True)

        self.assertEqual(1, len(Report.objects.all()))

        #Load the response data as JSON object
        result = simplejson.loads(response.content)

    def testCreateReportPro(self):
        self.sample_post['username'] = self.manager.username
        self.sample_post['password'] = 'test'

        #Create a client to launch requests
        client = Client()
        #Get the request response

        response = client.post('/fr/api/login/', {
            'username': self.manager.username,
            'password': 'test'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        #Load the response data as JSON object
        result = simplejson.loads(response.content)
        self.assertIn('email', result)

        response = client.post(reverse('create_report_citizen'), self.sample_post, follow=True)
        #Test the http response code (200 = OK)
        self.assertEqual(response.status_code, 200)

        #Test if the response if JSON structured.
        self.assertEqual(response['Content-Type'], 'application/json; charset=utf-8')

        #Load the response data as JSON object
        result = simplejson.loads(response.content)

        #Verify if the report_id is returned by the webservice
        self.assertTrue(result['id'])

        #Get in the DB the created report
        report = Report.objects.get(id=result['id'])

        #Verify the persisted data for the new created report
        self.assertEquals(report.address, self.sample_post['report-address_fr'])
        self.assertTrue(report.is_pro())

        # Check that source is correct
        self.assertEqual(Report.SOURCES['MOBILE'], report.source)

    def testCreateReportDoublePro(self):
        self.sample_post['username'] = self.manager.username
        self.sample_post['password'] = 'test'

        #Create a client to launch requests
        client = Client()

        #Get the request response
        client.post(reverse('create_report_citizen'), self.sample_post, follow=True)
        client.post(reverse('create_report_citizen'), self.sample_post, follow=True)
        client.post(reverse('create_report_citizen'), self.sample_post, follow=True)
        client.post(reverse('create_report_citizen'), self.sample_post, follow=True)

        self.assertEqual(1, len(Report.objects.all()))

    def testLoadCategories(self):
        #Parameters to save the report in database.
        params = {
            "user_name": "superuser"
        }
        #Create a client to launch requests
        client = Client()
        #Get the request response
        response = client.get(reverse('load_categories'), params, follow=True)
        #Test the http response code (200 = OK)
        self.assertEqual(response.status_code, 200)
        #Test if the response if JSON structured.
        self.assertEqual(response['Content-Type'], 'application/json')
        #Load the response data as JSON object
        result = simplejson.loads(response.content)

    """
    def testLoadReports(self):
        client = Client()
        response = client.get(reverse('api_reports'), {'x':1000,'y':1000}, follow=True)
        self.assertEqual(response.status_code, 200)
        result = simplejson.loads(response.content)
        self.assertEquals(result['status'], 'success')
        self.assertEquals(len(result['results']), 13) # sample contains 14 reports but 1 is fixed
    """

    def test_login_user(self):
        params = {
            'username': self.manager.email,
            'password': 'test'
        }
        response = self.client.post(reverse('login_user'), params)

        self.assertEqual(response.status_code, 200)

        result = simplejson.loads(response.content)
        self.assertEqual(result['id'], self.manager.id)
        self.assertEqual(result['first_name'], self.manager.first_name)

    def test_login_user_fail(self):
        params = {
            'username': self.manager.email,
            'password': 'badpassword'
        }
        response = self.client.post(reverse('login_user'), params)

        self.assertEqual(response.status_code, 403)

        result = simplejson.loads(response.content)
        self.assertEqual("ERROR_LOGIN_INVALID_PARAMETERS", result["error_key"])

    def test_login_user_fail_empty_field(self):
        params = {
            'username': self.manager.email
        }
        response = self.client.post(reverse('login_user'), params)

        self.assertEqual(response.status_code, 400)

        result = simplejson.loads(response.content)
        self.assertEqual("ERROR_LOGIN_INVALID_PARAMETERS", result["error_key"])

    def test_login_user_bad_username(self):
        params = {
            'username': "hello@a.com",
            'password': "kikoo"
        }
        response = self.client.post(reverse('login_user'), params)

        self.assertEqual(response.status_code, 403)

        result = simplejson.loads(response.content)
        self.assertEqual("ERROR_LOGIN_INVALID_PARAMETERS", result["error_key"])

    def test_logout_user(self):
        response = self.client.post(reverse('logout_user'))
        self.assertEqual(response.status_code, 200)

        self.assertEqual('', response.content)
