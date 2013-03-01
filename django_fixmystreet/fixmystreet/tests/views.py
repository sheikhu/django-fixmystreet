from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from django_fixmystreet.fixmystreet.tests import SampleFilesTestCase
from django_fixmystreet.fixmystreet.models import FMSUser

class ReportViewsTest(SampleFilesTestCase):
    fixtures = ['bootstrap']

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
        #self.client.login(username='test1', password='test')

        # !!!!!!!!!!!!!!!!!!!!!!!!******************************!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! TODO fix me !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # !!!!!!!!!!!!!!!!!!!!!!!!******************************!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        return

        url = reverse('report_new')

        response = self.client.post(url, {
            'report-x':'150056.538',
            'report-y':'170907.56',
            'report-address_fr':'Avenue des Arts',
            'report-address_nl':'Kunstlaan',
            'report-address_number':'3',
            'report-postalcode':'1000',
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
        }, follow=True)

        self.assertEqual(response.status_code, 200)

        self.assertIn('report', response.context)
        report = response.context['report']
        self.assertRedirects(response, reverse('report_show', args=[report.id]))
        self.assertContains(response, report.postalcode)
        self.assertContains(response, report.status)

    #def test_add_comment(self):
    #    """Tests the update of a report and flag it as fixed."""
    #    self.client.login(username='test1', password='pbkdf2_sha256$10000$25rhVrjO5v94$hMupY1IKgJqvwl8lTH7oVODnBtgaMlqafPXRKceW3g=')
    #    report = Report.objects.all()[0]
    #    nb_initial_attachment = report.get_comments().count()
    #    report.is_fixed = False
    #    report.save()

    #    SessionManager.createComment("title 1","text 2","session_id_1")
    #    SessionManager.createComment("title 3","text 4","session_id_1")

    #    SessionManager.saveComments("session_id_1", report)
    #    report = Report.objects.get(id=report.id)
    #    aaa = ReportComment.objects.filter(report__id=report.id)
        #self.assertRedirects(response, report.get_absolute_url())
        #self.assertEqual(response.status_code, 200)
    #    self.assertNotEqual(aaa.count(), 0)


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



