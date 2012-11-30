from datetime import date
import shutil, os
#from unittest import skip

from django.utils.translation import get_language
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core import mail
from django.core.files.storage import FileSystemStorage

from django.conf import settings
from django_fixmystreet.fixmystreet.models import Report, ReportSubscription, ReportNotification, ReportCategory, ReportMainCategoryClass, OrganisationEntity, FMSUser, ReportFile

class MailTest(TestCase):
	fixtures = ["bootstrap","list_items"]
	def setUp(self):
		self.citizen = FMSUser(telephone="0123456789", last_used_language="fr", agent=False, manager=False, leader=False, impetrant=False, contractor=False, username="citizen", first_name="citizen", last_name="citizen", email="citizen@a.com")
		self.citizen.save()
		self.manager = FMSUser(telephone="0123456789", last_used_language="fr", agent=False, manager=True, leader=False, impetrant=False, contractor=False, username="manager", password='test', first_name="manager", last_name="manager", email="manager@a.com")
		self.manager.set_password('test')
		self.manager.organisation = OrganisationEntity.objects.get(pk=14)
		self.manager.save()
		self.manager.categories.add(ReportCategory.objects.get(pk=1))
		self.client = Client()
	def testCreateUserMail(self):
		url = reverse('create_manager')
		#Login to access the pro page to create a user
		success = self.client.login(username='manager',password='test')
		#Send a post request with data filling the form on the user creation page
		response = self.client.post(url, {'username':'test','password1':'test','password2':'test','first_name':'test','last_name':'test','email':'test@email.com','telephone':'1234556','agentRadio':'1','managerRadio':'0','contractorRadio':'0'})
		#1 mail is sent to the created user
		self.assertEquals(len(mail.outbox),1)
		#The destination address must be equal to the one given to the created user
		self.assertEquals(len(mail.outbox[0].to),1)
		self.assertTrue('test@email.com' in mail.outbox[0].to)
	def testCreateReportMail(self):
		#Send a post request filling in the form to create a report
		self.client.post('/'+get_language()+'/report/new?x=150056.538&y=170907.56#form',{'x':'150056.538','y':'170907.56','address':'Avenue des Arts, 3','postalcode':'1210','category':'1','secondary_category':'1','quality':'0','description':'test','citizen_email':self.citizen.email,'citizen_firstname':self.citizen.first_name,'citizen_lastname':self.citizen.last_name,'citizen_subscription':'on','secondary_category_copy':'1','photo':''})
		#2 mails must be sent, one to the creator and 1 to the responsible manager
		self.assertEquals(len(mail.outbox), 2)
		self.assertEquals(len(mail.outbox[0].to), 1)
		self.assertEquals(len(mail.outbox[1].to), 1)
		#Mail to creator and manager must be sent
		self.assertTrue(self.citizen.email in mail.outbox[0].to or self.citizen.email in mail.outbox[1].to)
		self.assertTrue(self.manager.email in mail.outbox[0].to or self.manager.email in mail.outbox[1].to)
	def testCloseReportMail(self):
		#Send a post request filling in the form to create a report
		self.client.post('/'+get_language()+'/report/new?x=150056.538&y=170907.56#form',{'x':'150056.538','y':'170907.56','address':'Avenue des Arts, 3','postalcode':'1210','category':'1','secondary_category':'1','quality':'0','description':'test','citizen_email':self.citizen.email,'citizen_firstname':self.citizen.first_name,'citizen_lastname':self.citizen.last_name,'citizen_subscription':'on','secondary_category_copy':'1','photo':''})
		#Login to access the pro page to create a user
		success = self.client.login(username='manager',password='test')
		#Accept the created report
		self.client.get('/'+get_language()+'/pro/report/1/accept/')
		#The status of the report must now be MANAGER_ASSIGNED
		self.assertTrue(Report.objects.get(pk=1).status == Report.MANAGER_ASSIGNED)
		#Close the report
		self.client.get('/'+get_language()+'/pro/report/1/close/')
		#The status of the report must now be PROCESSED
		self.assertTrue(Report.objects.get(pk=1).status == Report.PROCESSED)
		#3 mails have been sent, 2 for the report creation and 1 for closing the report
		self.assertEquals(len(mail.outbox),3)
		#The last one must be sent to the citizen (= the closing report mail)
		self.assertTrue(self.citizen.email in mail.outbox[2].to)
	def testRefuseReportMail(self):
		#Send a post request filling in the form to create a report
		self.client.post('/'+get_language()+'/report/new?x=150056.538&y=170907.56#form',{'x':'150056.538','y':'170907.56','address':'Avenue des Arts, 3','postalcode':'1210','category':'1','secondary_category':'1','quality':'0','description':'test','citizen_email':self.citizen.email,'citizen_firstname':self.citizen.first_name,'citizen_lastname':self.citizen.last_name,'citizen_subscription':'on','secondary_category_copy':'1','photo':''})
		#Login to access the pro page to create a user
		success = self.client.login(username='manager',password='test')
		#Refuse the created report
		self.client.post('/'+get_language()+'/pro/report/1/refuse/',{'more_info_text':'more info'})
		#The status of the report must now be REFUSED
		self.assertTrue(Report.objects.get(pk=1).status == Report.REFUSED)
		#3 mails have been sent, 2 for the report creation and 1 for refusing the report
		self.assertEquals(len(mail.outbox),3)
		#The last one must be sent to the citizen (= the refusing report mail)
		self.assertTrue(self.citizen.email in mail.outbox[2].to)
	def testSubscriptionForCititzenMail(self):
		#Send a post request filling in the form to create a report
		self.client.post('/'+get_language()+'/report/new?x=150056.538&y=170907.56#form',{'x':'150056.538','y':'170907.56','address':'Avenue des Arts, 3','postalcode':'1210','category':'1','secondary_category':'1','quality':'0','description':'test','citizen_email':self.citizen.email,'citizen_firstname':self.citizen.first_name,'citizen_lastname':self.citizen.last_name,'citizen_subscription':'on','secondary_category_copy':'1','photo':''})
		#Send a post request subscribing a citizen to the just created report
		self.client.post('/'+get_language()+'/report/1/subscribe/',{'citizen_email':'post@test.com'})
		#3 mails have been sent, 2 for the report creation and 1 for subscribing to the report
		self.assertEquals(len(mail.outbox),3)
		self.assertTrue('post@test.com' in mail.outbox[2].to)
	def testMarkReportAsDoneMail(self):
		#Send a post request filling in the form to create a report
		self.client.post('/'+get_language()+'/report/new?x=150056.538&y=170907.56#form',{'x':'150056.538','y':'170907.56','address':'Avenue des Arts, 3','postalcode':'1210','category':'1','secondary_category':'1','quality':'0','description':'test','citizen_email':self.citizen.email,'citizen_firstname':self.citizen.first_name,'citizen_lastname':self.citizen.last_name,'citizen_subscription':'on','secondary_category_copy':'1','photo':''})
		#Send a post request to mark the report as done
		self.client.post('/'+get_language()+'/report/1/update/',{'is_fixed':'1'})
		#3 mails have been sent, 2 for the report creation and 1 for telling the responsible manager that the report is marked as done
		self.assertEquals(len(mail.outbox),3)
		self.assertTrue(self.manager.email in mail.outbox[2].to)
		#Send another post request to mark the report as done
		self.client.post('/'+get_language()+'/report/1/update/',{'is_fixed':'1'})
		#Again 3 mails have been sent, the extra mark as done request will not send an extra email to the responsible manager
		self.assertEquals(len(mail.outbox),3)
