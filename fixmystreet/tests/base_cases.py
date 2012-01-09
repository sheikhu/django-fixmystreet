from django.test import TestCase
from django.test.client import Client
from django.core import mail
from django.contrib.sites.models import Site
from fixmystreet.models import Report,ReportUpdate,ReportSubscription,City, \
    ReportCategory, ReportCategoryClass
import settings
import re

CREATE_PARAMS =  { 'title': 'A report from our API', 
                     'lat': '150035',
                     'lon': '170907',
                     'postalcode':'1000',
                     'address':'Avenue des arts 21a',
                     'category': 5,
                     'desc': 'The description',
                     'author': 'John Farmer',
                     'email': 'testcreator@hotmail.com',
                     'phone': '514-513-0475' } 

UPDATE_PARAMS = { 'author': 'John Farmer',
                      'email': 'testupdater@hotmail.com',
                      'desc': 'This problem has been fixed',
                      'phone': '514-513-0475',
                      'is_fixed': True }

class BaseTestCase(TestCase):
    """
        Some helper functions for our test base cases.
    """
    #    this fixture has one fixed report (id=1), and one unfixed (id=2).
    fixtures = ['test_report_basecases.json']
    c = Client()

    def _get_confirm_url(self, email ):
        m = re.search( 'http://(?P<domain>[\w\.]+(:\d+)?)/reports/(subscribers|updates)/confirm/(\S+)', email.body )
        self.assertIsNotNone(m,'url not found in %s' % email.body)
        self.assertEquals(m.group('domain'),Site.objects.get_current().domain)
        return( str(m.group(0)))

    def _get_unsubscribe_url(self,email):
        m = re.search( 'http://(?P<domain>[\w\.]+(:\d+)?)/reports/subscribers/unsubscribe/(\S+)', email.body )
        self.assertIsNotNone(m,'url not found in %s' % email.body)
        self.assertEquals(m.group('domain'),Site.objects.get_current().domain)
        return( str(m.group(0)))



    def testCreateReport(self):
        """
        Run through our regular report/submit/confirm/update-is-fixed/confirm
        lifecycle to make sure there's no issues, and the right
        emails are being sent.
        """
        response = self.c.post('/reports/new', CREATE_PARAMS, follow=True )
        self.assertEquals( response.status_code, 200 )
        self.assertEquals(response.template[0].name, 'reports/show.html', (response.context['report_form'].errors if 'report_form' in response.context else None))
        self.assertEquals(Report.objects.filter(title=CREATE_PARAMS['title']).count(), 1 )

        report = Report.objects.get(title=CREATE_PARAMS['title'])

        # a confirmation email should be sent to the user
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].to, [u'testcreator@hotmail.com'])
        self.assertIn(CREATE_PARAMS['title'],mail.outbox[0].body)
        self.assertIn('<strong>%s</strong>'%CREATE_PARAMS['title'],mail.outbox[0].alternatives[0][0])

        #test confirmation link
        confirm_url = self._get_confirm_url(mail.outbox[0])
        response = self.c.get(confirm_url, follow=True)
        self.assertEquals( response.status_code, 200 )

        #now there should be two emails in our outbox
        self.assertEquals(len(mail.outbox), 2)
        self.assertEquals(mail.outbox[1].to, report.get_emails()[0])
        self.assertEquals(mail.outbox[1].cc, report.get_emails()[1])
        self.assertIn(CREATE_PARAMS['title'],mail.outbox[1].body)
        
        #now submit a 'fixed' update.
        self.assertEquals( ReportUpdate.objects.filter(report=report).count(),1)
        update_url = report.get_absolute_url() + "/updates/"
        response = self.c.post(update_url,UPDATE_PARAMS, follow=True)
        self.assertEquals( response.status_code, 200 )
        self.assertEquals( ReportUpdate.objects.filter(report=report).count(),2)
        self.assertEquals( ReportUpdate.objects.filter( report=report, is_confirmed=True).count(),1)
        # we should have sent another confirmation link
        self.assertEquals(len(mail.outbox), 3)
        self.assertEquals(mail.outbox[2].to, [u'testupdater@hotmail.com'])

        #confirm the update
        confirm_url = self._get_confirm_url(mail.outbox[2])
        response = self.c.get(confirm_url, follow=True)
        self.assertEquals( response.status_code, 200 )
        self.assertEquals( ReportUpdate.objects.filter( report=report, is_confirmed=True).count(),2)
        self.assertIn(UPDATE_PARAMS['desc'],response.content)
        #make sure the creator of the report gets an update.
        self.assertEquals(len(mail.outbox), 4)
        self.assertEquals(mail.outbox[3].to, [u'testcreator@hotmail.com'])

    def testSubscribe(self):
        """
        Test subscribing and unsubscribing from a report.
        """
        Report.objects.get(id=3)
        response = self.c.post('/reports/3/subscribers/new', 
                               { 'email': 'subscriber@test.com'} , follow=True )

        self.assertEquals( response.status_code, 200, response.content)
        self.assertEquals(response.template[0].name, 'reports/subscribers/create.html')
        
        # an unconfirmed subscriber should be created, and an email sent.
        self.assertEquals( ReportSubscription.objects.count(),1)
        self.assertEquals( ReportSubscription.objects.get(email='subscriber@test.com').is_confirmed,False )
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].to, [u'subscriber@test.com'])
        
        #confirm the subscriber
        confirm_url = self._get_confirm_url(mail.outbox[0])
        response = self.c.get(confirm_url, follow=True)
        self.assertEquals( response.status_code, 200, '%s not found' % confirm_url)

        #subscriber should now be confirmed
        self.assertTrue(ReportSubscription.objects.get(email='subscriber@test.com').is_confirmed)

        # updating the report should send emails to report author, 
        # as well as all subscribers. 

        # -- send the update
        response = self.c.post('/reports/3/updates/',UPDATE_PARAMS, follow=True)
        self.assertEquals( response.status_code, 200 )
        self.assertEquals(len(mail.outbox), 2)

        # -- confirm the update
        #  self.assertNotEquals(m,mail.outbox[1])
        confirm_url = self._get_confirm_url(mail.outbox[1])
        response = self.c.get(confirm_url, follow=True)
        self.assertEquals( response.status_code, 200 )

        # check that the right ppl got emails
        self.assertEquals(len(mail.outbox), 4)
        self.assertEquals(mail.outbox[2].to, [u'subscriber@test.com'])
        self.assertEquals(mail.outbox[3].to, [u'reportcreator@test.com'])
        
        # test that the subscribed user can unsubscribe with the link provided.
        unsubscribe_url = self._get_unsubscribe_url(mail.outbox[2])
        response = self.c.get(unsubscribe_url, follow=True)
        self.assertEquals( response.status_code, 200 )
        self.assertEquals( ReportSubscription.objects.count(),0)

    def testFlagReport(self):
        """
        Test that flagging a report sends the admin an email
        """
        report = Report.objects.get(pk=2)
        flag_url = report.get_absolute_url() + "/flags/"
        response = self.c.post(flag_url,{}, follow=True)
        self.assertEquals( response.status_code, 200 )
        self.assertEquals( response.template[0].name, 'reports/flags/thanks.html')

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].to, [settings.ADMIN_EMAIL])
