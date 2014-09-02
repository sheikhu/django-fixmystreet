from unittest import skip
from datetime import datetime

from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.gis.geos import Polygon

from django_fixmystreet.fixmystreet.tests import SampleFilesTestCase
from django_fixmystreet.fixmystreet.models import (
    Report, ReportCategory, OrganisationEntity, FMSUser,
    OrganisationEntitySurface
)


class ReportViewsTest(SampleFilesTestCase):

    fixtures = ["bootstrap", "list_items"]

    def setUp(self):

        self.user = FMSUser(username='test1', email='test1@fixmystreet.irisnet.be', password='test')
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

        self.group = OrganisationEntity(
            type="D",
            name_nl="Werken",
            name_fr="Travaux",
            phone="090987",
            dependency=OrganisationEntity.objects.get(pk=14),
            email="test@email.com"
            )
        self.group.save()

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
        self.group.dispatch_categories.add(ReportCategory.objects.get(pk=1))

        p1 = (148776, 171005)
        p2 = (150776, 171005)
        p3 = (150776, 169005)
        p4 = (148776, 169005)

        surface = OrganisationEntitySurface(
            geom=Polygon([p1, p2, p3, p4, p1]),
            owner=OrganisationEntity.objects.get(pk=14),
        )
        surface.save()

        self.manager.memberships.create(organisation=self.group, contact_user=True)

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
            'comment-text': 'test',
            'files-TOTAL_FORMS': 0,
            'files-INITIAL_FORMS': 0,
            'files-MAX_NUM_FORMS': 0,
            'citizen-email': self.citizen.email,
            'citizen-firstname': self.citizen.first_name,
            'citizen-lastname': self.citizen.last_name,
            'citizen-quality': '1',
            'report-terms_of_use_validated': True
        }
        self.sample_post_2 = {
            'report-x': '150056',
            'report-y': '170907.56',
            'report-address_fr': 'Avenue des Arts, 3',
            'report-address_nl': 'Kunstlaan, 3',
            'report-address_number': '5',
            'report-postalcode': '1210',
            'report-category': '1',
            'report-secondary_category': '1',
            'report-subscription': 'on',
            'comment-text': 'test2',
            'files-TOTAL_FORMS': 0,
            'files-INITIAL_FORMS': 0,
            'files-MAX_NUM_FORMS': 0,
            'citizen-email': self.citizen.email,
            'citizen-firstname': self.citizen.first_name,
            'citizen-lastname': self.citizen.last_name,
            'citizen-quality': '1',
            'report-terms_of_use_validated': True
        }

    def test_home(self):
        """Tests the new report view."""
        response = self.client.get(reverse('home'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('report_counts' in response.context)
        self.assertTrue('zipcodes' in response.context)
        #Are the zipcodes well loaded from DB??
        self.assertTrue(len(response.context['zipcodes']) > 0)

    @skip('replaced by database pages')
    def test_about(self):
        """Tests the about view."""
        response = self.client.get(reverse('about'), follow=True)
        self.assertEqual(response.status_code, 200)

    @skip('replaced by database pages')
    def test_term_of_use(self):
        """Tests the term of use view."""
        response = self.client.get(reverse('terms_of_use'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_new_report(self):
        """Tests the new report page."""
        url = reverse('report_new')
        response = self.client.get(url, {'x': '148360', 'y': '171177'}, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_verify_report(self):
        """Tests the new report page get verify existings."""
        url = "%s?x=148360&y=171177" % reverse('report_new')
        response = self.client.post(url, self.sample_post, follow=True)
        self.assertEqual(response.status_code, 200)

        url = reverse('report_verify')
        response = self.client.get(url, {'x': '150056', 'y': '170907'}, follow=True)
        self.assertEqual(response.status_code, 200)

        self.assertIn('reports_nearby', response.context)
        # Assert that the list view displays minimal information about reports
        last_dist = 0
        for report in response.context['reports_nearby']:
            self.assertContains(response, report.get_absolute_url())
            self.assertTrue(report.distance.m <= 20)  # limit to 1km around
            self.assertTrue(report.distance.m >= last_dist)  # ordered by distance
            last_dist = report.distance.m

    def test_create_report(self):
        """Tests the creation of a report and test the view of it."""

        url = "%s?x=148360&y=171177" % reverse('report_new')

        response = self.client.post(url, self.sample_post, follow=True)

        self.assertEqual(response.status_code, 200)

        self.assertIn('report', response.context)

        report = response.context['report']

        self.assertContains(response, report.postalcode)
        self.assertContains(response, report.status)

        self.assertEqual(1, len(Report.objects.all()))

        # Get in the DB the created report
        report = Report.objects.all()[0]

        # Check that source is correct
        self.assertEqual(Report.SOURCES['WEB'], report.source)

    def test_create_report_double(self):
        """Tests the creation of a double report and test the view of it."""

        url = "%s?x=148360&y=171177" % reverse('report_new')

        self.client.post(url, self.sample_post, follow=True)
        self.client.post(url, self.sample_post, follow=True)
        self.client.post(url, self.sample_post, follow=True)
        self.client.post(url, self.sample_post, follow=True)

        self.assertEqual(1, len(Report.objects.all()))

    def test_accept_report(self):
        """Tests acceptation a report and test the view of it."""

        url = "%s?x=148360&y=171177" % reverse('report_new')
        response = self.client.post(url, self.sample_post, follow=True)
        self.assertEqual(response.status_code, 200)

        report = response.context['report']

        self.client.login(username='manager@a.com', password='test')

        url = reverse('report_accept_pro', args=[report.id])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

        report = response.context['report']

        self.assertTrue(report.accepted_at is not None)

    def test_refuse_report(self):
        """Tests refuse a report and test the view of it."""

        url = "%s?x=148360&y=171177" % reverse('report_new')
        response = self.client.post(url, self.sample_post, follow=True)
        self.assertEqual(response.status_code, 200)

        report = response.context['report']

        self.client.login(username='manager@a.com', password='test')

        url = reverse('report_refuse_pro', args=[report.id])
        response = self.client.post(url, {'text': "Message de refus"}, follow=True)
        self.assertEqual(response.status_code, 200)

        report = response.context['report']

        self.assertTrue(report.accepted_at is None)
        self.assertEqual(report.status, Report.REFUSED)

    def test_publish_report(self):
        """Tests publishing a report and test the view of it."""

        url = "%s?x=148360&y=171177" % reverse('report_new')
        response = self.client.post(url, self.sample_post, follow=True)
        self.assertEqual(response.status_code, 200)

        report = response.context['report']

        self.client.login(username='manager@a.com', password='test')
        url = reverse('report_publish_pro', args=[report.id])
        response = self.client.get(url, {}, follow=True)

        report = response.context['report']

        self.assertTrue(report.accepted_at is not None)
        self.assertFalse(report.private)

    def test_add_comment(self):
        """Tests the update of a report."""
        url = "%s?x=148360&y=171177" % reverse('report_new')
        response = self.client.post(url, self.sample_post, follow=True)
        report = response.context['report']

        self.assertEqual(report.comments().count(), 1)
        self.assertEqual(report.comments()[0].created_by, self.citizen)
        report.save()

        response = self.client.post(reverse('report_document', kwargs={'report_id': report.id, 'slug': 'hello'}), {
            'comment-text': 'new created comment',
            'citizen-email': self.user.email,
            'citizen-quality': 1,
            'files-TOTAL_FORMS': 0,
            'files-INITIAL_FORMS': 0,
            'files-MAX_NUM_FORMS': 0
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, report.get_absolute_url())

        self.assertEqual(report.comments().count(), 2)
        self.assertEqual(report.comments()[1].created_by, self.user)

    def test_add_comment_as_pro(self):
        """Tests the update of a report as a pro."""
        self.client.login(username='manager@a.com', password='test')

        url = "%s?x=148360&y=171177" % reverse('report_new_pro')
        response = self.client.post(url, self.sample_post, follow=True)
        report = response.context['report']

        self.assertEqual(report.comments().count(), 1)
        self.assertEqual(report.comments()[0].created_by, self.manager)
        report.save()

        response = self.client.post(reverse('report_show_pro', kwargs={'report_id': report.id, 'slug': 'hello'}), {
            'comment-text': 'new created comment',
            'files-TOTAL_FORMS': 0,
            'files-INITIAL_FORMS': 0,
            'files-MAX_NUM_FORMS': 0
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, report.get_absolute_url_pro())

        self.assertEqual(report.comments().count(), 2)
        self.assertEqual(report.comments()[1].created_by, self.manager)

    def test_change_category_private(self):
        self.client.login(username='manager@a.com', password='test')

        url = "%s?x=148360&y=171177" % reverse('report_new')
        response = self.client.post(url, self.sample_post, follow=True)
        report = response.context['report']

        self.assertEqual(Report.objects.get(id=report.id).category.id, 1)
        self.assertEqual(Report.objects.get(id=report.id).secondary_category.id, 1)

        # Setting a private sec_cat to a public report is not allowed
        self.client.post(reverse('update_category_for_report', args=[report.id]), {"main_category": "2", "secondary_category": "32"})

        # So, cat not changed
        self.assertEqual(Report.objects.get(id=report.id).category.id, 1)
        self.assertEqual(Report.objects.get(id=report.id).secondary_category.id, 1)

    def test_change_category_public(self):
        self.client.login(username='manager@a.com', password='test')

        url = "%s?x=148360&y=171177" % reverse('report_new')
        response = self.client.post(url, self.sample_post, follow=True)
        report = response.context['report']

        self.assertEqual(Report.objects.get(id=report.id).category.id, 1)
        self.assertEqual(Report.objects.get(id=report.id).secondary_category.id, 1)

        self.client.post(reverse('update_category_for_report', args=[report.id]), {"main_category": "2", "secondary_category": "2"})

        self.assertEqual(Report.objects.get(id=report.id).category.id, 2)
        self.assertEqual(Report.objects.get(id=report.id).secondary_category.id, 2)

    def test_subscription(self):
        """Tests the subscription of a report."""

        url = "%s?x=148360&y=171177" % reverse('report_new')
        response = self.client.post(url, self.sample_post, follow=True)
        report = response.context['report']

        # responsible manager has subscribed by default
        self.assertTrue(report.subscriptions.filter(subscriber=self.manager).exists())

        self.client.login(username='manager@a.com', password='test')

        #unsubscribe to the report
        response = self.client.get(reverse('unsubscribe_pro', args=[report.id]), {}, follow=True)
        self.assertRedirects(response, report.get_absolute_url_pro())
        self.assertEqual(response.status_code, 200)

        #current user is no more subscribed
        self.assertFalse(report.subscriptions.filter(subscriber=self.manager).exists())

        # subscribe to the report
        response = self.client.get(reverse('subscribe_pro', args=[report.id]), {}, follow=True)
        self.assertRedirects(response, report.get_absolute_url_pro())
        self.assertEqual(response.status_code, 200)

        #current user is subscribed
        self.assertTrue(report.subscriptions.filter(subscriber=self.manager).exists())

    def test_subscription_citizen(self):
        """Tests the subscription of a report."""

        url = "%s?x=148360&y=171177" % reverse('report_new')
        response = self.client.post(url, self.sample_post, follow=True)
        report = response.context['report']

        # current user is not subscribed yet
        self.assertTrue(report.subscriptions.filter(subscriber=self.citizen).exists())

        #unsubscribe to the report
        response = self.client.get(reverse('unsubscribe', args=[report.id]) + '?citizen_email=' + self.citizen.email, {}, follow=True)
        self.assertRedirects(response, report.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        #current user is no more subscribed
        self.assertFalse(report.subscriptions.filter(subscriber=self.citizen).exists())

    def test_do_merge_reports(self):
        """Test do merge reports. """

        #Add first report
        url = "%s?x=148360&y=171177" % reverse('report_new')
        response = self.client.post(url, self.sample_post, follow=True)
        report = response.context['report']

        #Add second report
        response2 = self.client.post(url, self.sample_post_2, follow=True)
        report2 = response2.context['report']

        #Login user
        params = {
            'username': self.manager.email,
            'password': 'test'
        }
        self.client.post(reverse('login'), params)

        #Merge reports
        url2 = reverse('report_do_merge_pro', args=[report.id])
        self.client.post(url2, {"mergeId": report2.id})

        #Reference from merged to kept report
        self.assertEqual(report.id, Report.objects.get(id=report2.id).merged_with.id)

        #The first one (oldest one) is kept
        self.assertEqual(Report.objects.all().visible()[0].id, report.id)

        #The comment of the second one is added to the first one
        self.assertEqual(Report.objects.get(id=report.id).comments().count(), 2)

    def test_merge_reports(self):
        """Test merge reports. """

        # Add first report
        url = "%s?x=148360&y=171177" % reverse('report_new')
        response = self.client.post(url, self.sample_post, follow=True)
        report = response.context['report']

        # Add second report
        response2      = self.client.post(url, self.sample_post_2, follow=True)
        report2        = response2.context['report']
        report2.status = Report.IN_PROGRESS
        report2.save()

        # Login user
        params = {
            'username': self.manager.email,
            'password': 'test'
        }
        self.client.post(reverse('login'), params)

        # Display mergeable reports list
        url = reverse('report_merge_pro', args=[report.get_slug(), report.id])
        response = self.client.get(url)

        self.assertEqual(report, response.context['report'])
        self.assertEqual(1, len(response.context['reports_nearby']))

    def test_merge_reports_search_ticket(self):
        """Test merge reports with search of ticket number """

        # Add first report
        url = "%s?x=148360&y=171177" % reverse('report_new')
        response = self.client.post(url, self.sample_post, follow=True)
        report = response.context['report']

        # Add second report
        response2 = self.client.post(url, self.sample_post_2, follow=True)
        report2 = response2.context['report']

        # Login user
        params = {
            'username': self.manager.email,
            'password': 'test'
        }
        self.client.post(reverse('login'), params)

        # Display mergeable report according to ticket number
        url2 = reverse('report_merge_pro', args=[report.get_slug(), report.id])
        response = self.client.get("%s?ticketNumber=%s" % (url2, report2.id))

        self.assertEqual(report, response.context['report'])
        self.assertEqual(1, len(response.context['reports_nearby']))
        self.assertEqual(report2.id, response.context['reports_nearby'][0].id)

    def test_mark_done(self):
        """Tests marking report as done."""

        url = "%s?x=148360&y=171177" % reverse('report_new')
        response = self.client.post(url, self.sample_post, follow=True)
        report = response.context['report']

        self.client.login(username='manager@a.com', password='test')
        url = reverse('report_accept_pro', args=[report.id])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.client.logout()

        self.assertFalse(report.mark_as_done_comment)
        self.assertFalse(report.fixed_at)

        response = self.client.post(reverse('report_update', args=[report.id]), {'is_fixed': 'True', 'text': 'commentaire'}, follow=True)
        self.assertEqual(response.status_code, 200)

        report = response.context['report']
        self.assertTrue(report.fixed_at)
        self.assertFalse(report.mark_as_done_comment)
        self.assertEqual(report.status, Report.SOLVED)

        self.client.login(username=self.manager.email, password='test')
        response = self.client.post(reverse('report_close_pro', args=[report.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        report = response.context['report']
        self.assertTrue(report.fixed_at)
        self.assertEqual(report.status, Report.PROCESSED)

    def test_mark_done_as_user(self):
        """Tests marking report as done."""

        url = "%s?x=148360&y=171177" % reverse('report_new')
        response = self.client.post(url, self.sample_post, follow=True)
        report = response.context['report']
        self.assertFalse(report.mark_as_done_comment)
        self.assertFalse(report.fixed_at)

        self.client.login(username='manager@a.com', password='test')
        url = reverse('report_accept_pro', args=[report.id])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse('report_fix_pro', args=[report.id]),
            {'is_fixed': 'True', 'text': 'commentaire'},
            follow=True)
        self.assertEquals(response.status_code, 200)

        report = response.context['report']
        self.assertTrue(report.fixed_at)
        self.assertTrue(report.mark_as_done_comment)
        self.assertEquals(report.status, Report.SOLVED)

        self.client.login(username=self.manager.email, password='test')
        response = self.client.post(reverse('report_close_pro', args=[report.id]), follow=True)
        self.assertEquals(response.status_code, 200)
        report = response.context['report']
        self.assertTrue(report.fixed_at)
        self.assertTrue(report.close_date)
        self.assertEquals(report.status, Report.PROCESSED)

    def test_search_ticket(self):
        """Tests searching ticket."""
        url = "%s?x=148360&y=171177" % reverse('report_new')
        response = self.client.post(url, self.sample_post, follow=True)
        report = response.context['report']

        url = '%s?report_id=%s' % (reverse('search_ticket'), report.id)
        response = self.client.get(url, follow=True)

        self.assertEqual(response.status_code, 200)
        report_result = response.context['report']

        self.assertEqual(report, report_result)

    def test_login_user(self):
        params = {
            'username': self.manager.email,
            'password': 'test'
        }
        response = self.client.post(reverse('login'), params)

        self.assertEqual(response.status_code, 302)

    def test_login_user_with_redirect(self):
        params = {
            'username': self.manager.email,
            'password': 'test'
        }

        url = '%s?next=/fr/pro/reports/' % reverse('login')
        response = self.client.post(url, params)

        self.assertEqual(response.status_code, 302)

    def test_login_user_fail(self):
        params = {
            'username': self.manager.email,
            'password': 'badpassword'
        }
        response = self.client.post(reverse('login'), params)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct username and password. Note that both fields are case-sensitive.')

    def test_logout_user(self):
        params = {
            'username': self.manager.email,
            'password': 'test'
        }
        self.client.post(reverse('login'), params)

        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)

    def test_marker_detail_citizen(self):
        url = "%s?x=148360&y=171177" % reverse('report_new')

        response = self.client.post(url, self.sample_post, follow=True)

        self.assertEqual(response.status_code, 200)

        self.assertIn('report', response.context)

        report = response.context['report']
        jsonResult = report.full_marker_detail_JSON()
        #Now test on all mandatory fields
        self.assertIn('id', jsonResult)
        self.assertIn('point', jsonResult)
        self.assertIn('category', jsonResult)
        self.assertIn('address', jsonResult)
        self.assertIn('address_number', jsonResult)
        self.assertIn('postalcode', jsonResult)
        self.assertIn('address_commune_name', jsonResult)
        self.assertIn('address_regional', jsonResult)
        self.assertIn('thumb', jsonResult)
        self.assertIn('contractor', jsonResult)
        self.assertIn('date_planned', jsonResult)
        self.assertNotIn('is_closed', jsonResult)
        self.assertNotIn('citizen', jsonResult)
        self.assertNotIn('priority', jsonResult)

    def test_marker_detail_pro(self):
        url = "%s?x=148360&y=171177" % reverse('report_new')

        response = self.client.post(url, self.sample_post, follow=True)

        self.assertEqual(response.status_code, 200)

        self.assertIn('report', response.context)

        report = response.context['report']
        jsonResult = report.full_marker_detail_pro_JSON()
        #Now test on all mandatory fields
        self.assertIn('id', jsonResult)
        self.assertIn('point', jsonResult)
        self.assertIn('category', jsonResult)
        self.assertIn('address', jsonResult)
        self.assertIn('address_number', jsonResult)
        self.assertIn('postalcode', jsonResult)
        self.assertIn('address_commune_name', jsonResult)
        self.assertIn('address_regional', jsonResult)
        self.assertIn('thumb', jsonResult)
        self.assertIn('contractor', jsonResult)
        self.assertIn('date_planned', jsonResult)
        self.assertIn('is_closed', jsonResult)
        self.assertIn('citizen', jsonResult)
        self.assertIn('priority', jsonResult)

    def test_reopen_report_refused(self):
        url = "%s?x=148360&y=171177" % reverse('report_new')
        response = self.client.post(url, self.sample_post, follow=True)
        self.assertEqual(response.status_code, 200)

        report = response.context['report']
        report.status = Report.REFUSED
        report.save()

        self.client.login(username='manager@a.com', password='test')

        url = reverse('report_reopen_pro', args=[report.id])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

        report_reopen = response.context['report']

        self.assertEqual(Report.MANAGER_ASSIGNED, report_reopen.status)
        self.assertNotEqual(report.status  , report_reopen.status)
        self.assertEqual(report.created    , report_reopen.created)
        self.assertEqual(report.close_date , report_reopen.close_date)

        # accepted_at need to be initialized
        self.assertFalse(report.accepted_at)
        self.assertTrue(report_reopen.accepted_at)

        self.assertEqual(report.subscriptions.all().count(), report_reopen.subscriptions.all().count())
        self.assertEqual(report.responsible_entity         , report_reopen.responsible_entity)
        self.assertEqual(report.responsible_department     , report_reopen.responsible_department)

    def test_reopen_report_processed(self):
        url = "%s?x=148360&y=171177" % reverse('report_new')
        response = self.client.post(url, self.sample_post, follow=True)
        self.assertEqual(response.status_code, 200)

        report = response.context['report']
        report.status = Report.PROCESSED
        report.accepted_at = datetime.now()
        report.save()

        self.client.login(username='manager@a.com', password='test')

        url = reverse('report_reopen_pro', args=[report.id])
        response = self.client.get(url, follow=True)

        self.assertEqual(response.status_code, 200)

        report_reopen = response.context['report']

        self.assertEqual(Report.MANAGER_ASSIGNED, report_reopen.status)
        self.assertNotEqual(report.status  , report_reopen.status)
        self.assertEqual(report.created    , report_reopen.created)
        self.assertEqual(report.accepted_at, report_reopen.accepted_at)
        self.assertEqual(report.close_date , report_reopen.close_date)

        self.assertEqual(report.subscriptions.all().count(), report_reopen.subscriptions.all().count())
        self.assertEqual(report.responsible_entity         , report_reopen.responsible_entity)
        self.assertEqual(report.responsible_department     , report_reopen.responsible_department)

    def test_reopen_report_badstatus(self):
        url = "%s?x=148360&y=171177" % reverse('report_new')
        response = self.client.post(url, self.sample_post, follow=True)
        self.assertEqual(response.status_code, 200)

        report = response.context['report']
        report.accepted_at = datetime.now()
        report.save()

        self.client.login(username='manager@a.com', password='test')

        url = reverse('report_reopen_pro', args=[report.id])
        response = self.client.get(url, follow=True)

        self.assertEqual(response.status_code, 200)

        report_not_reopen = response.context['report']

        self.assertNotEqual(Report.MANAGER_ASSIGNED, report_not_reopen.status)
        self.assertEqual(report.status        , report_not_reopen.status)
        self.assertEqual(report.created       , report_not_reopen.created)
        self.assertEqual(report.modified      , report_not_reopen.modified)
        self.assertEqual(report.accepted_at   , report_not_reopen.accepted_at)
        self.assertEqual(report.close_date    , report_not_reopen.close_date)

        self.assertEqual(report.subscriptions.all().count(), report_not_reopen.subscriptions.all().count())
        self.assertEqual(report.responsible_entity         , report_not_reopen.responsible_entity)
        self.assertEqual(report.responsible_department     , report_not_reopen.responsible_department)
