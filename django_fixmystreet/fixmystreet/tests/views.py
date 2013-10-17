from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from django_fixmystreet.fixmystreet.tests import SampleFilesTestCase
from django_fixmystreet.fixmystreet.models import Report, ReportCategory, OrganisationEntity, FMSUser

class ReportViewsTest(SampleFilesTestCase):

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
        self.sample_post_2 = {
            'report-x':'150056',
            'report-y':'170907.56',
            'report-address_fr':'Avenue des Arts, 3',
            'report-address_nl':'Kunstlaan, 3',
            'report-address_number':'5',
            'report-postalcode':'1210',
            'report-category':'1',
            'report-secondary_category':'1',
            'report-subscription':'on',
            'comment-text':'test2',
            'files-TOTAL_FORMS': 0,
            'files-INITIAL_FORMS': 0,
            'files-MAX_NUM_FORMS': 0,
            'citizen-email':self.citizen.email,
            'citizen-firstname':self.citizen.first_name,
            'citizen-lastname':self.citizen.last_name,
            'citizen-quality':'1',
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

    def test_about(self):
        """Tests the about view."""
        response = self.client.get(reverse('about'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('faq_entries' in response.context)

    def test_term_of_use(self):
        """Tests the term of use view."""
        response = self.client.get(reverse('terms_of_use'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_posters_languages(self):
        """Tests the posters view."""
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

    def test_new_report(self):
        """Tests the new report page."""
        url = reverse('report_new')
        response = self.client.get(url, {'x':'148360','y':'171177'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('reports' in response.context)
        # Assert that the list view displays minimal information about reports
        last_dist = 0
        for report in response.context['reports']:
            self.assertContains(response, report.get_absolute_url())
            self.assertTrue(report.distance.m <= 1000) # limit to 1km around
            self.assertTrue(report.distance.m >= last_dist) # ordered by distance
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

    def test_create_report_double(self):
        """Tests the creation of a double report and test the view of it."""

        url = "%s?x=148360&y=171177" % reverse('report_new')

        response = self.client.post(url, self.sample_post, follow=True)
        response = self.client.post(url, self.sample_post, follow=True)
        response = self.client.post(url, self.sample_post, follow=True)
        response = self.client.post(url, self.sample_post, follow=True)

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
        self.client.login(username='manager@a.com', password='test')

        url = "%s?x=148360&y=171177" % reverse('report_new')
        response = self.client.post(url, self.sample_post, follow=True)
        report = response.context['report']

        self.assertEqual(report.comments().count(), 1)
        report.save()

        response = self.client.post(reverse('report_show', kwargs={'report_id': report.id, 'slug':'hello'}), {
            'comment-text': 'new created comment',
            'files-TOTAL_FORMS': 0,
            'files-INITIAL_FORMS': 0,
            'files-MAX_NUM_FORMS': 0
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, report.get_absolute_url())

        self.assertEqual(report.comments().count(), 2)

    def test_change_category(self):
        self.client.login(username='manager@a.com', password='test')

        url = "%s?x=148360&y=171177" % reverse('report_new')
        response = self.client.post(url, self.sample_post, follow=True)
        report = response.context['report']

        self.assertEqual(Report.objects.get(id=report.id).category.id,1)
        self.assertEqual(Report.objects.get(id=report.id).secondary_category.id,1)

        response2 = self.client.post(reverse('update_category_for_report',args=[report.id]),{"main_category":"2","secondary_category":"32"})

        self.assertEqual(Report.objects.get(id=report.id).category.id,2)
        self.assertEqual(Report.objects.get(id=report.id).secondary_category.id,32)

    def test_subscription(self):
        """Tests the subscription of a report."""

        url = "%s?x=148360&y=171177" % reverse('report_new')
        response = self.client.post(url, self.sample_post, follow=True)
        report = response.context['report']

        # responsible manager has subscribed by default
        self.assertTrue(report.subscriptions.filter(subscriber=self.manager).exists())

        self.client.login(username='manager@a.com', password='test')

        #unsubscribe to the report
        response = self.client.get(reverse('unsubscribe_pro',args=[report.id]), {}, follow=True)
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
        response = self.client.get(reverse('unsubscribe',args=[report.id]) + '?citizen_email=' + self.citizen.email, {}, follow=True)
        self.assertRedirects(response, report.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        #current user is no more subscribed
        self.assertFalse(report.subscriptions.filter(subscriber=self.citizen).exists())


    def test_merge_reports(self):
        """Test merge reports. """

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
        response3 = self.client.post(reverse('login'), params)

        #Merge reports
        url2 = reverse('report_merge_pro',args=[report.id])
        response4 = self.client.get(url2,{"mergeId":report2.id})

        #Reference from merged to kept report
        self.assertEqual(report.id,Report.objects.get(id=report2.id).merged_with.id)

        #The first one (oldest one) is kept
        self.assertEqual(Report.objects.all()[0].id, report.id)

        #The comment of the second one is added to the first one
        self.assertEqual(Report.objects.get(id=report.id).comments().count(),2)


    def test_mark_done(self):
        """Tests marking report as done."""

        url = "%s?x=148360&y=171177" % reverse('report_new')
        response = self.client.post(url, self.sample_post, follow=True)
        report = response.context['report']

        self.assertFalse(report.mark_as_done_user)
        self.assertFalse(report.fixed_at)

        response = self.client.post(reverse('report_update', args=[report.id]), {'is_fixed':'True'}, follow=True)
        self.assertEqual(response.status_code, 200)

        report = response.context['report']
        self.assertTrue(report.fixed_at)
        self.assertEqual(report.status, Report.SOLVED)

    def test_mark_done_as_user(self):
        """Tests marking report as done."""

        url = "%s?x=148360&y=171177" % reverse('report_new')
        response = self.client.post(url, self.sample_post, follow=True)
        report = response.context['report']
        self.assertFalse(report.mark_as_done_user)
        self.assertFalse(report.fixed_at)

        # Auth as manager
        self.client.login(username='manager@a.com', password='test')
        response = self.client.post(reverse('report_update', args=[report.id]), {'is_fixed':'True'}, follow=True)
        self.assertEqual(response.status_code, 200)

        report = response.context['report']
        self.assertTrue(report.fixed_at)
        self.assertTrue(report.mark_as_done_user)
        self.assertEqual(report.status, Report.SOLVED)

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

    #def test_wards_city(self):
    #    """Tests the city and wards view."""
    #    response = self.client.get(reverse('bxl_wards'), follow=True)
    #    self.assertEqual(response.status_code, 200)
    #    self.assertTrue('city' in response.context)
    #    self.assertEquals(response.context['city'].id,1)
    #    response = self.client.get(reverse('ward_show',args=[1]), follow=True)
    #    self.assertEqual(response.status_code, 200)

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

        url = '%s?next=/fr/pro/reports/' %reverse('login')
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


