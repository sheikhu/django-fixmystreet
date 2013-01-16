from urllib2 import Request, urlopen, HTTPError
from urllib import urlencode
import urlparse

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import simplejson
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.conf import settings

from django_fixmystreet.fixmystreet.models import Report, OrganisationEntity, FMSUser, ReportSecondaryCategoryClass, ReportMainCategoryClass, ReportCategory
from django_fixmystreet.fixmystreet.tests import SampleFilesTestCase

from django.core.exceptions import ObjectDoesNotExist

# https://developers.facebook.com/docs/test_users/
# https://developers.facebook.com/docs/authentication/#applogin


class ApiTest(SampleFilesTestCase):
    fixtures = ['bootstrap', 'sample']
    users = {
        '100003558692539': {
            'name':'Steven Test',
            'email': "steven_strubyi_test@tfbnw.net"
        }
    }

    def setUp(self):

        try:
            organisation = OrganisationEntity.objects.get(id=1)
        except ObjectDoesNotExist:        
            organisation = OrganisationEntity(id=1, name="Test organisation")
            organisation.save()
        
        
        #user_auth = User.objects.create_user(username='superuser', email='test1@fixmystreet.irisnet.be', password='test')
        #user_auth.save()
        user = FMSUser(password="test", first_name="zaza", telephone="00000000", last_used_language="fr", organisation=organisation, username='superuser')
        user.save()

        main_category = ReportMainCategoryClass(id=2,name_en='test main en',name_nl='test main nl',name_fr='test main fr')
        main_category.save()
        
        secondary_category = ReportSecondaryCategoryClass(id=2,name_en='test second en',name_nl='test second nl',name_fr='test second fr')        
        secondary_category.save()
        
        category = ReportCategory(id=2,name_en='test parent en',name_nl='test parent nl',name_fr='test parent fr', public=True, category_class=main_category, secondary_category_class=secondary_category)
        category.save()
		
		
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
        #Parameters to save the report in database.
        params = {
            "user_email": "test@test.com",
            "user_firstname": "Thibo",
            "user_lastname": "Bilbao",
            "user_phone": "324324324",
            "report_quality": "2",
            "report_description": "zazadescr",
            "report_address": "Avenue des emeutes",
            "report_address_number":"2",
            "report_category_id": "2",
            "report_main_category_id": "2",
            "report_zipcode": "1000",
            #"username": "thierryallent",
            "report_y": "170375.278",
            "report_x": "149157.349"
        }
        
        #Create a client to launch requests
        client = Client()
        #Get the request response
        response = client.post(reverse('create_report_citizen'), params, follow=True)      
        #Test the http response code (200 = OK)
        self.assertEqual(response.status_code, 200)        
        #Test if the response if JSON structured.
        self.assertEqual(response['Content-Type'], 'application/json')
        #Load the response data as JSON object
        result = simplejson.loads(response.content)
        #Verify if the report_id is returned by the webservice
        self.assertTrue(result['report_id'] != None)
        #Get in the DB the created report
        report = Report.objects.get(id=result['report_id'])
        #Verify the persisted data for the new created report
        self.assertEquals(report.description, 'zazadescr')                
    
    #def testCreateReportPro(self):
        #Parameters to save the report in database.
    #    params = {
    #        "user_name": "superuser",
    #        "report_category_id": "2",
    #        "report_description": "zazadescr",
    #        "user_firstname": "Thibo",
    #        "report_address": "Avenue des emeutes",
    #        "user_lastname": "Bilbao",
    #        "report_main_category_id": "2",
    #        "report_zipcode": "1000",
    #        "report_id": "22",
    #        "report_y": "170375.278",
    #        "report_x": "149157.349"
    #    }
        
        #Create a client to launch requests
    #    client = Client()
        #Get the request response
    #    response = client.post(reverse('create_report_pro'), params, follow=True)        
        #Test the http response code (200 = OK)
    #    self.assertEqual(response.status_code, 200)        
        #Test if the response if JSON structured.
    #    self.assertEqual(response['Content-Type'], 'application/json')
        #Load the response data as JSON object
    #    result = simplejson.loads(response.content)
        #Verify if the report_id is returned by the webservice
    #    self.assertTrue(result['report_id'] != None)
        #Get in the DB the created report
    #    report = Report.objects.get(id=result['report_id'])
        #Verify the persisted data for the new created report
    #    self.assertEquals(report.description, 'zazadescr')
    
    def testLoadCategories(self):                
        #Parameters to save the report in database.
        params = {
            "user_name": "superuser"
        }
        #Create a client to launch requests
        client = Client()
        #Get the request response
        response = client.post(reverse('load_categories'), params, follow=True)        
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
