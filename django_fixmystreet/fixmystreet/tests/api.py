from urllib2 import Request, urlopen, HTTPError
from urllib import urlencode
import urlparse

from django.test import TestCase
from django.utils import simplejson
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.conf import settings

from social_auth.backends.exceptions import AuthTokenError

from django_fixmystreet.fixmystreet.models import Report
from django_fixmystreet.fixmystreet.tests import SampleFilesTestCase

# https://developers.facebook.com/docs/test_users/
# https://developers.facebook.com/docs/authentication/#applogin


class ApiTest(SampleFilesTestCase):
    fixtures = ['sample']
    users = {
        '100003558692539': {
            'name':'Steven Test',
            'email': "steven_strubyi_test@tfbnw.net"
        }
    }

    def setUp(self):
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
        
        
    def testCreateReport(self):
        # check if Facebook can authenticate steven
        url = 'https://graph.facebook.com/me?access_token={0}'.format(self.steven['access_token'])
        request = Request(url)
        response = simplejson.loads(urlopen(request).read())
        self.assertEquals(response['email'],self.steven['email'])
        
        params = {
            'category': 1,
            'address': 'turlututu',
            'x': '1000',
            'y': '1000',
            'postalcode':'1000',
            'description':'hello',
            'access_token':self.steven['access_token'],
            'backend':'facebook'
        }

        client = Client()

        response = client.post(reverse('api_report_new'), params, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        result = simplejson.loads(response.content)

        self.assertEquals(result['status'], 'success', result.get('message'))
        report = Report.objects.get(id=result['report']['id'])
        self.assertEquals(report.desc, 'hello')
        self.assertEquals(report.category.id, 1)

        params['postalcode'] = "4321"
        response = client.post(reverse('api_report_new'), params, follow=True)
        self.assertEqual(response.status_code, 200)
        result = simplejson.loads(response.content)
        self.assertEquals(result['status'], 'error')
        self.assertEquals(result['errortype'], 'validation_error')

        del params['postalcode']
        response = client.post(reverse('api_report_new'), params, follow=True)
        self.assertEqual(response.status_code, 200)
        result = simplejson.loads(response.content)
        self.assertEquals(result['status'], 'error')
        self.assertEquals(result['errortype'], 'validation_error')

        params['postalcode'] = "1000"
        params['access_token'] = "broken_token"
        self.assertRaises(AuthTokenError, lambda:client.post(reverse('api_report_new'), params, follow=True))

    def testLoadReports(self):
        client = Client()
        response = client.get(reverse('api_reports'), {'x':1000,'y':1000}, follow=True)
        self.assertEqual(response.status_code, 200)
        result = simplejson.loads(response.content)
        self.assertEquals(result['status'], 'success')
        self.assertEquals(len(result['results']), 13) # sample contains 14 reports but 1 is fixed

