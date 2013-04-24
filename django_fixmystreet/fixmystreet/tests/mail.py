
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.core import mail

from django_fixmystreet.fixmystreet.models import Report, ReportCategory, OrganisationEntity, FMSUser


class MailTest(TestCase):
	fixtures = ["bootstrap", "list_items"]

	def setUp(self):
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
		self.client = Client()

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
			'citizen-quality':'1',
			'comment-text':'test',
			'files-TOTAL_FORMS': 0,
			'files-INITIAL_FORMS': 0,
			'files-MAX_NUM_FORMS': 0,
			'citizen-email':self.citizen.email,
			'citizen-firstname':self.citizen.first_name,
			'citizen-lastname':self.citizen.last_name,
		}

	def testCreateReportMail(self):
		#Send a post request filling in the form to create a report
		response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post)
		self.assertEquals(response.status_code, 200)
		# self.assertIn('/en/report/trou-en-revetements-en-trottoir-en-saint-josse-ten-noode/1', response['Location'])
		#2 mails must be sent, one to the creator and 1 to the responsible manager
		self.assertEquals(len(mail.outbox), 2)
		self.assertEquals(len(mail.outbox[0].to), 1) # to the citizen for aknowledge of creation
		self.assertEquals(len(mail.outbox[1].to), 1) # to the responsible for creation notify
		#Mail to creator and manager must be sent
		self.assertTrue(self.citizen.email in mail.outbox[0].to or self.citizen.email in mail.outbox[1].to)
		self.assertTrue(self.manager.email in mail.outbox[0].to or self.manager.email in mail.outbox[1].to)

	def testCloseReportMail(self):
		#Send a post request filling in the form to create a report
		response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post)
		self.assertEquals(response.status_code, 200)
		# self.assertIn('/en/report/trou-en-revetements-en-trottoir-en-saint-josse-ten-noode/1', response['Location'])


		# report_id = resolve(response.redirect_chain[-1][0]).kwargs['report_id']
		self.assertIn('report', response.context)

		report_id = response.context['report'].id
		report = Report.objects.get(id=report_id)
		self.assertEquals(report.subscriptions.all().count(), 2)
		self.assertEquals(len(mail.outbox), 2)

		#Login to access the pro page to create a user
		self.client.login(username='manager@a.com', password='test')

		#Accept the created report
		response = self.client.get(reverse('report_accept_pro', args=[report.id]), follow=True)
		#The status of the report must now be MANAGER_ASSIGNED
		self.assertEquals(response.status_code, 200)

		report = Report.objects.get(id=report.id)
		self.assertEquals(report.status, Report.MANAGER_ASSIGNED)
		#3 mails have been sent, 2 for the report creation + 1 notification to author for the report publishing
		self.assertEquals(len(mail.outbox), 3)
		#Close the report
		response = self.client.get(reverse('report_close_pro', args=[report.id]), follow=True)
		self.assertEquals(response.status_code, 200)

		report = Report.objects.get(id=report.id)
		self.assertEquals(report.status, Report.PROCESSED)
		#4 mails have been sent, 2 for the report creation, 1 for the report publishing and 1 for closing the report
		self.assertEquals(len(mail.outbox), 4)
		#The last one must be sent to the citizen (= the closing report mail)
		self.assertIn(self.citizen.email, mail.outbox[3].to)


	def testRefuseReportMail(self):
		#Send a post request filling in the form to create a report
		response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post)
		self.assertEquals(response.status_code, 200)
		self.assertTrue(response.context['report_form'].is_valid(), response.context['report_form'].errors)
		self.assertIn('report', response.context)

		report_id = response.context['report'].id
		report = Report.objects.get(id=report_id)
		self.assertEquals(report.subscriptions.all().count(), 2)
		self.assertEquals(len(mail.outbox), 2) # one for creator subscription, one for manager

		#Login to access the pro page to create a user
		self.client.login(username='manager@a.com', password='test')
		#Refuse the created report
		response = self.client.post(reverse('report_refuse_pro', args=[report_id]), {'refusal_motivation':'more info'}, follow=True)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(len(mail.outbox),3)
		#The status of the report must now be REFUSED
		report = Report.objects.get(id=report_id)
		self.assertEquals(report.status, Report.REFUSED)
		#3 mails have been sent, 2 for the report creation and 1 for refusing the report
		#The last one must be sent to the citizen (= the refusing report mail)
		self.assertIn(self.citizen.email, mail.outbox[2].to)

	def testSubscriptionForCititzenMail(self):
		#Send a post request filling in the form to create a report
		response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post)
		self.assertEquals(response.status_code, 200)
		self.assertIn('report', response.context)

		report_id = response.context['report'].id
		self.assertEquals(len(mail.outbox),2) # one for creator subscription, one for manager

		#Send a post request subscribing a citizen to the just created report
		response = self.client.post(reverse('subscribe', args=[report_id]),{'citizen_email':'post@test.com'}, follow=True)
		self.assertEquals(response.status_code, 200)
		#3 mails have been sent, 2 for the report creation and 1 for subscribing to the report
		self.assertEquals(len(mail.outbox),3)
		self.assertTrue('post@test.com' in mail.outbox[2].to)

	def testMarkReportAsDoneMail(self):
		#Send a post request filling in the form to create a report
		response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post)
		self.assertEquals(response.status_code, 200)
		self.assertIn('report', response.context)

		report_id = response.context['report'].id

		self.assertEquals(len(mail.outbox), 2) # one for creator subscription, one for manager

		#Login to access the pro page
		self.client.login(username='manager@a.com', password='test')
		#Publish the created report
		response = self.client.post(reverse('report_accept_pro', args=[report_id]), follow=True)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(len(mail.outbox), 3)

		#Send a post request to mark the report as done

		response = self.client.post(reverse('report_update', args=[report_id]), {'is_fixed':'True'})
		self.assertEquals(response.status_code, 302)
		# self.assertIn('/en/report/trou-en-revetements-en-trottoir-en-saint-josse-ten-noode/1', response['Location'])
		#4 mails have been sent, 2 for the report creation and 1 for telling the responsible manager that the report is marked as done, and 1 for the report change to the citizen subscriber
		self.assertEquals(Report.objects.get(id=report_id).status, Report.SOLVED)

		self.assertEquals(len(mail.outbox), 4)
		self.assertTrue(self.manager.email in mail.outbox[3].to)
		#Send another post request to mark the report as done
		response = self.client.post(reverse('report_update', args=[report_id]), {'is_fixed':'True'})
		self.assertEquals(response.status_code, 302)
		# self.assertIn('/en/report/trou-en-revetements-en-trottoir-en-saint-josse-ten-noode/1', response['Location'])
		#Again 4 mails have been sent, the extra mark as done request will not send an extra email to the responsible manager
		self.assertEquals(len(mail.outbox), 4)

