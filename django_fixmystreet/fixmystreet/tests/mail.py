
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
			username="citizen",
			first_name="citizen",
			last_name="citizen",
			email="citizen@a.com"
		)
		self.citizen.save()
		self.manager = FMSUser(
			telephone="0123456789",
			last_used_language="fr",
			username="manager",
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
			'x':'150056.538',
			'y':'170907.56',
			'address':'Avenue des Arts, 3',
			'address_number':'3',
			'postalcode':'1210',
			'category':'1',
			'secondary_category':'1',
			'quality':'1',
			'description':'test',
			'citizen_email':self.citizen.email,
			'citizen_firstname':self.citizen.first_name,
			'citizen_lastname':self.citizen.last_name,
			'citizen_subscription':'on',
			'secondary_category_copy':'1',
			'photo':''
		}

	def testCreateReportMail(self):
		#Send a post request filling in the form to create a report
		response = self.client.post('/en/report/new?x=150056.538&y=170907.56#form', self.sample_post)
		self.assertEquals(response.status_code, 302)
		self.assertIn('/en/report/trou-en-revetements-en-trottoir-en-saint-josse-ten-noode/1', response['Location'])

		#2 mails must be sent, one to the creator and 1 to the responsible manager
		self.assertEquals(len(mail.outbox), 2)
		self.assertEquals(len(mail.outbox[0].to), 1)
		self.assertEquals(len(mail.outbox[1].to), 1)
		#Mail to creator and manager must be sent
		self.assertTrue(self.citizen.email in mail.outbox[0].to or self.citizen.email in mail.outbox[1].to)
		self.assertTrue(self.manager.email in mail.outbox[0].to or self.manager.email in mail.outbox[1].to)

	def testCloseReportMail(self):
		#Send a post request filling in the form to create a report
		response = self.client.post('/en/report/new?x=150056.538&y=170907.56#form', self.sample_post)
		self.assertEquals(response.status_code, 302)
		self.assertIn('/en/report/trou-en-revetements-en-trottoir-en-saint-josse-ten-noode/1', response['Location'])

		# report_id = resolve(response.redirect_chain[-1][0]).kwargs['report_id']
		report_id = 1
		#Login to access the pro page to create a user
		self.client.login(username='manager', password='test')

		#Accept the created report
		response = self.client.get(reverse('report_accept_pro', args=[report_id]), follow=True)
		#The status of the report must now be MANAGER_ASSIGNED
		self.assertEquals(response.status_code, 200)
		self.assertTrue(Report.objects.get(pk=1).status == Report.MANAGER_ASSIGNED)
		#Close the report
		response = self.client.get(reverse('report_close_pro', args=[report_id]), follow=True)
		self.assertEquals(response.status_code, 200)
		#The status of the report must now be PROCESSED
		self.assertTrue(Report.objects.get(pk=1).status == Report.PROCESSED)
		#3 mails have been sent, 2 for the report creation and 1 for closing the report
		self.assertEquals(len(mail.outbox),3)
		#The last one must be sent to the citizen (= the closing report mail)
		self.assertTrue(self.citizen.email in mail.outbox[2].to)

	def testRefuseReportMail(self):
		#Send a post request filling in the form to create a report
		response = self.client.post('/en/report/new?x=150056.538&y=170907.56#form', self.sample_post)
		self.assertEquals(response.status_code, 302)
		self.assertIn('/en/report/trou-en-revetements-en-trottoir-en-saint-josse-ten-noode/1', response['Location'])

		self.assertEquals(len(mail.outbox),2) # one for creator subscription, one for manager
		#Login to access the pro page to create a user
		self.client.login(username='manager', password='test')
		#Refuse the created report
		response = self.client.post('/en/pro/report/1/refuse/',{'more_info_text':'more info'}, follow=True)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(len(mail.outbox),3)
		#The status of the report must now be REFUSED
		self.assertTrue(Report.objects.get(pk=1).status == Report.REFUSED)
		#3 mails have been sent, 2 for the report creation and 1 for refusing the report
		#The last one must be sent to the citizen (= the refusing report mail)
		self.assertTrue(self.citizen.email in mail.outbox[2].to)

	def testSubscriptionForCititzenMail(self):
		#Send a post request filling in the form to create a report
		response = self.client.post('/en/report/new?x=150056.538&y=170907.56#form', self.sample_post)
		self.assertEquals(response.status_code, 302)
		self.assertIn('/en/report/trou-en-revetements-en-trottoir-en-saint-josse-ten-noode/1', response['Location'])

		self.assertEquals(len(mail.outbox),2) # one for creator subscription, one for manager
		#Send a post request subscribing a citizen to the just created report
		response = self.client.post('/en/report/1/subscribe/',{'citizen_email':'post@test.com'}, follow=True)
		self.assertEquals(response.status_code, 200)
		#3 mails have been sent, 2 for the report creation and 1 for subscribing to the report
		self.assertEquals(len(mail.outbox),3)
		self.assertTrue('post@test.com' in mail.outbox[2].to)

	def testMarkReportAsDoneMail(self):
		#Send a post request filling in the form to create a report
		response = self.client.post('/en/report/new?x=150056.538&y=170907.56#form', self.sample_post)
		self.assertEquals(response.status_code, 302)
		self.assertIn('/en/report/trou-en-revetements-en-trottoir-en-saint-josse-ten-noode/1', response['Location'])

		self.assertEquals(len(mail.outbox),2) # one for creator subscription, one for manager
		#Send a post request to mark the report as done
		response = self.client.post('/en/report/1/update/',{'is_fixed':'1'}, follow=True)
		self.assertEquals(response.status_code, 200)
		#3 mails have been sent, 2 for the report creation and 1 for telling the responsible manager that the report is marked as done
		self.assertEquals(len(mail.outbox),3)
		self.assertTrue(self.manager.email in mail.outbox[2].to)
		#Send another post request to mark the report as done
		response = self.client.post('/en/report/1/update/',{'is_fixed':'1'}, follow=True)
		self.assertEquals(response.status_code, 200)
		#Again 3 mails have been sent, the extra mark as done request will not send an extra email to the responsible manager
		self.assertEquals(len(mail.outbox),3)
