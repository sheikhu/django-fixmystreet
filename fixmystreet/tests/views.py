from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.db import IntegrityError

from fixmystreet.models import Report, ReportSubscription

class ReportViewsTest(TestCase):
    fixtures = ['sample']
    def setUp(self):
        self.user = User.objects.create_user('admin', 'test@fixmystreet.irisnet.be', 'pwd')
        self.user.save()
        self.client = Client()

    def test_new_report(self):
        """Tests the new report view."""
        # Make sure that the list view exists
        url = reverse('report_new')

        response = self.client.get(url, {'x':'1000','y':'1000'}, follow=True)
        self.assertEqual(response.status_code, 200)
        # Assert that the list view has suitable content for templates
        self.assertTrue('reports' in response.context)
        # Assert that the list view displays minimal information about reports
        last_dist = 0
        for report in response.context['reports']:
            #self.assertContains(response, report.title)
            self.assertContains(response, report.get_absolute_url())
            self.assertTrue(report.distance > last_dist) # ordered by distance
            last_dist = report.distance

    def test_create_report(self):
        """Tests the creation of a report and test the view of it."""
        self.client.login(username='admin', password='pwd')
        url = reverse('report_new')
        response = self.client.post(url, {'x':'1000','y':'1000','title':'Just a test', 'address': 'Av des arts', 'category':1,'postalcode':'1000'}, follow=True)
        self.assertEqual(response.status_code, 200)

        self.assertTrue('report' in response.context)
        report = response.context['report']
        self.assertRedirects(response, report.get_absolute_url())
        self.assertContains(response, report.title)

    def test_update_report(self):
        """Tests the update of a report and flag it as fixed."""
        self.client.login(username='admin', password='pwd')
        report = Report.objects.all()[0]
        nb_initial_update = report.reportupdate_set.count()
        report.is_fixed = False
        report.save()

        url = reverse('report_update',args=[report.id])
        response = self.client.post(url, {'desc':'Just a description test'}, follow=True)
        report = Report.objects.get(id=report.id)
        self.assertRedirects(response, report.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(report.reportupdate_set.count(), nb_initial_update + 1)

        response = self.client.post(url, {'desc':'Just a fix test', 'is_fixed':'1'}, follow=True)
        report = Report.objects.get(id=report.id)
        self.assertRedirects(response, report.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(report.reportupdate_set.count(), nb_initial_update + 2)
        self.assertTrue(report.reportupdate_set.all()[report.reportupdate_set.count()-1].is_fixed)
        self.assertTrue(report.is_fixed)

    def test_subscription(self):
        """Tests the creation of a report and test the view of it."""
        report = Report.objects.all()[0]
        self.client.login(username='admin', password='pwd')

        #current user is not subscribed yet
        self.assertFalse(ReportSubscription.objects.filter(report=report,subscriber=self.user).exists())

        #subscribe to the report
        response = self.client.get(reverse('subscribe',args=[report.id]), {}, follow=True)
        self.assertRedirects(response, report.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        #current user is subscribed
        self.assertTrue(ReportSubscription.objects.filter(report=report,subscriber=self.user).exists())

        #unsubscribe to the report
        response = self.client.get(reverse('unsubscribe',args=[report.id]), {}, follow=True)
        self.assertRedirects(response, report.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        #current user is no more subscribed
        self.assertFalse(ReportSubscription.objects.filter(report=report,subscriber=self.user).exists())

        response = self.client.get(reverse('subscribe',args=[report.id]), {}, follow=True)
        #there is already a subscription => raise an IntegrityError
        with self.assertRaises(IntegrityError):
            response = self.client.get(reverse('subscribe',args=[report.id]), {}, follow=True)
