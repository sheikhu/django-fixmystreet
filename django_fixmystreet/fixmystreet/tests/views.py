from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils.translation import ugettext as _
from django.core import mail

from django_fixmystreet.fixmystreet.models import Report, ReportSubscription
from django.conf import settings

class ReportViewsTest(TestCase):
    fixtures = ['bootstrap', 'sample']
    def setUp(self):
        self.user = User.objects.create_user('test1', 'test1@fixmystreet.irisnet.be', 'pwd')
        self.user.save()
        self.client = Client()

    def test_home(self):
        """Tests the new report view."""
        response = self.client.get(reverse('home'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('report_counts' in response.context)
        self.assertTrue('zipcodes' in response.context)
        #Are the zipcodes well loaded from DB??
        self.assertTrue(len(response.context['zipcodes']) > 0)
    
    def test_about(self):
        """Tests the about view."""
        response = self.client.get(reverse('about'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('faq_entries' in response.context)
    
    def test_term_of_use(self):
        """Tests the term of use view."""
        response = self.client.get(reverse('terms_of_use'), follow=True)
        self.assertEqual(response.status_code, 200)
    
    def test_robots_file(self):
        """Tests the robots file."""
        response = self.client.get('/robots.txt', follow=True)
        self.assertEqual(response.status_code, 200)
    
    def test_posters_languages(self):
        """Tests the about view."""
        response = self.client.get(reverse('posters'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('languages' in response.context)
        
        frFound = False
        nlFound = False

        for current in response.context["languages"]:
             if current[0] == 'fr':
                  frFound = True
             if current[0] == 'nl':
                  nlFound = True
        self.assertTrue(frFound and nlFound)
    #def test_new_report(self):
    #    """Tests the new report view."""
        # Make sure that the list view exists
    #    url = reverse('report_new')
    #    response = self.client.get(url, {'x':'148360','y':'171177'}, follow=True)
    #    self.assertEqual(response.status_code, 200)
        # Assert that the list view has suitable content for templates
    #    self.assertTrue('reports' in response.context)
        # Assert that the list view displays minimal information about reports
    #    last_dist = 0
    #    for report in response.context['reports']:
    #        #self.assertContains(response, report.title)
    #        self.assertContains(response, report.get_absolute_url())
    #        self.assertTrue(report.distance < 1000) # limit to 1km around
    #        self.assertTrue(report.distance > last_dist) # ordered by distance
    #        last_dist = report.distance

    #def test_create_report(self):
    #    """Tests the creation of a report and test the view of it."""
    #    self.client.login(username='test1', password='pwd')
    #    url = reverse('report_new')
    #    response = self.client.post(url, {
    #        'x':'148360',
    #        'y':'171177',
    #        'title':'Just a test',
    #        'address': 'Av des arts',
    #        'category':1,
    #        'postalcode':'1000'
    #    }, follow=True)
    #    self.assertEqual(response.status_code, 200)

    #    self.assertTrue('report' in response.context)
    #    report = response.context['report']
    #    self.assertRedirects(response, report.get_absolute_url())
    #    self.assertContains(response, report.title)

    #def test_update_report(self):
    #    """Tests the update of a report and flag it as fixed."""
    #    self.client.login(username='test1', password='pwd')
    #    report = Report.objects.all()[0]
    #    nb_initial_attachment = report.attachments.count()
    #    report.is_fixed = False
    #    report.save()

    #    url = reverse('report_update',args=[report.id])
    #    response = self.client.post(url, {'desc':'Just a description test'}, follow=True)
    #    report = Report.objects.get(id=report.id)
    #    self.assertRedirects(response, report.get_absolute_url())
    #    self.assertEqual(response.status_code, 200)
    #    self.assertEqual(report.reportupdate_set.count(), nb_initial_update + 1)

    #    response = self.client.post(url, {'desc':'Just a fix test', 'is_fixed':'1'}, follow=True)
    #    report = Report.objects.get(id=report.id)
    #    self.assertRedirects(response, report.get_absolute_url())
    #    self.assertEqual(response.status_code, 200)
    #    self.assertEqual(report.reportupdate_set.count(), nb_initial_update + 2)
    #    self.assertTrue(report.reportupdate_set.all()[report.reportupdate_set.count()-1].is_fixed)
    #    self.assertTrue(report.is_fixed)

    #def test_subscription(self):
    #    """Tests the creation of a report and test the view of it."""
    #    report = Report.objects.all()[0]
    #    self.client.login(username='test1', password='pwd')

        #current user is not subscribed yet
    #    self.assertFalse(ReportSubscription.objects.filter(report=report,subscriber=self.user).exists())

        #subscribe to the report
    #    response = self.client.get(reverse('subscribe',args=[report.id]), {}, follow=True)
    #    self.assertRedirects(response, report.get_absolute_url())
    #    self.assertEqual(response.status_code, 200)

        #current user is subscribed
    #    self.assertTrue(ReportSubscription.objects.filter(report=report,subscriber=self.user).exists())

        #unsubscribe to the report
    #    response = self.client.get(reverse('unsubscribe',args=[report.id]), {}, follow=True)
    #    self.assertRedirects(response, report.get_absolute_url())
    #    self.assertEqual(response.status_code, 200)

        #current user is no more subscribed
    #    self.assertFalse(ReportSubscription.objects.filter(report=report,subscriber=self.user).exists())

    #    response = self.client.get(reverse('subscribe',args=[report.id]), {}, follow=True)
        #there is already a subscription => raise an IntegrityError
    #    with self.assertRaises(IntegrityError):
    #        response = self.client.get(reverse('subscribe',args=[report.id]), {}, follow=True)


    #def test_wards_city(self):
    #    """Tests the city and wards view."""
    #    response = self.client.get(reverse('bxl_wards'), follow=True)
    #    self.assertEqual(response.status_code, 200)
    #    self.assertTrue('city' in response.context)
    #    self.assertEquals(response.context['city'].id,1)
    #    response = self.client.get(reverse('ward_show',args=[1]), follow=True)
    #    self.assertEqual(response.status_code, 200)

    #def test_misc_pages(self):
    #    response = self.client.get(reverse('about'), follow=True)
    #    self.assertEqual(response.status_code, 200)

    #    response = self.client.get(reverse('contact'), follow=True)
    #    self.assertEqual(response.status_code, 200)
    #    response = self.client.post(reverse('contact'), {
    #        'name':'',
    #        'email':'test',
    #        'body':'This is just a test'
    #    }, follow=True)
    #    self.assertEquals(len(mail.outbox), 0)
    #    self.assertFormError(response, 'contact_form', 'name', _('This field is required.'))
    #    self.assertFormError(response, 'contact_form', 'email', _('Enter a valid e-mail address.'))

    #    response = self.client.post(reverse('contact'), {
    #        'name':'Test',
    #        'email':'test@test.irisnet.be',
    #        'body':'This is just a test'
    #    }, follow=True)
    #    self.assertEquals(len(mail.outbox), 1)
    #    self.assertEquals(len(mail.outbox[0].to), 1)
    #    self.assertEquals(mail.outbox[0].from_email, settings.EMAIL_FROM_USER)
        #self.assertEquals(mail.outbox[0].from_email, 'Test<test@test.irisnet.be>') TODO for reply behavior
    #    self.assertEquals(mail.outbox[0].to, [settings.EMAIL_ADMIN])

    #    self.assertEqual(response.status_code, 200)
    #    response = self.client.get(reverse('terms_of_use'), follow=True)
    #    self.assertEqual(response.status_code, 200)
    #    response = self.client.get('/robots.txt', follow=True)
    #    self.assertEqual(response.status_code, 200)
    #    self.assertEqual(response['Content-Type'], 'text/plain')



