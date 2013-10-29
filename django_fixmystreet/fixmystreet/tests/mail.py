
from django.test import TestCase
from django.utils import unittest
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.core import mail

from django_fixmystreet.fixmystreet.models import Report, ReportCategory, OrganisationEntity, FMSUser, UserOrganisationMembership

from datetime import datetime, timedelta


class MailTest(TestCase):
    fixtures = ["bootstrap","list_items"]

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

        self.group = OrganisationEntity(
            type="D",
            name_nl="Werken",
            name_fr="Travaux",
            phone="090987",
            dependency = OrganisationEntity.objects.get(pk=14),
            email="test@email.com"
            )
        self.group.save()
        self.usergroupmembership = UserOrganisationMembership(user_id = self.manager.id, organisation_id = self.group.id)
        self.usergroupmembership.save()


        self.client = Client()

        self.manager2 = FMSUser(
            telephone="9876543210",
            last_used_language="nl",
            password='test',
            first_name="manager2",
            last_name="manager2",
            email="manager2@a.com",
            manager=True
        )
        self.manager2.set_password('test2')
        self.manager2.organisation = OrganisationEntity.objects.get(pk=14)
        self.manager2.save()
        self.manager2.categories.add(ReportCategory.objects.get(pk=2))

        self.group2 = OrganisationEntity(
            type="D",
            name_nl="Werken",
            name_fr="Travaux",
            phone="090987",
            dependency = OrganisationEntity.objects.get(pk=21),
            email="test@email.com"
            )
        self.group2.save()
        self.usergroupmembership2 = UserOrganisationMembership(user_id = self.manager2.id, organisation_id = self.group2.id)
        self.usergroupmembership2.save()

        self.manager3 = FMSUser(
            telephone="000000000",
            last_used_language="nl",
            password='test',
            first_name="manager3",
            last_name="manager3",
            email="manager3@a.com",
            manager=True
        )
        self.manager3.set_password('test3')
        self.manager3.organisation = OrganisationEntity.objects.get(pk=21)
        self.manager3.save()
        self.manager3.categories.add(ReportCategory.objects.get(pk=1))

        self.usergroupmembership3 = UserOrganisationMembership(user_id = self.manager3.id, organisation_id = self.group2.id)
        self.usergroupmembership3.save()

        self.impetrant = OrganisationEntity(
            name_nl="MIVB",
            name_fr="STIB",
            commune=False,
            region=False,
            subcontractor=False,
            email="stib@mivb.be",
            applicant=True)

        self.impetrant.save()

        self.contractor = OrganisationEntity(
            name_nl="Fabricom GDF",
            name_fr="Fabricom GDF",
            commune=False,
            region=False,
            subcontractor=True,
            applicant=False)
        self.contractor.save()

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
            'citizen-quality': '1',
            'comment-text': 'test',
            'files-TOTAL_FORMS': 0,
            'files-INITIAL_FORMS': 0,
            'files-MAX_NUM_FORMS': 0,
            'citizen-email': self.citizen.email,
            'citizen-firstname': self.citizen.first_name,
            'citizen-lastname': self.citizen.last_name,
            'report-terms_of_use_validated': True
        }

        self.sample_post_pro = {
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
            'report-terms_of_use_validated': True
        }

        self.sample_post_mail_pdf_pro = {
        'comments':'test comment',
        'privacy':'private',
        'to':'test@test.com,filip@test.com;test@filip.com'
        }

        self.sample_post_mail_pdf_citzen = {
        'comments':'test comment',
        'privacy':'public',
        'to':'test@test.com,filip@test.com;test@filip.com'
        }

    def testCreateReportMail(self):
        #Send a post request filling in the form to create a report
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post)
        self.assertEquals(response.status_code, 200)
        # self.assertIn('/en/report/trou-en-revetements-en-trottoir-en-saint-josse-ten-noode/1', response['Location'])
        #2 mails must be sent, one to the creator and 1 to the responsible manager
        self.assertEquals(len(mail.outbox), 2)
        self.assertEquals(len(mail.outbox[0].to), 1)  # to the citizen for aknowledge of creation
        self.assertEquals(len(mail.outbox[1].to), 1)  # to the responsible for creation notify
        #Mail to creator and manager must be sent
        self.assertTrue(self.citizen.email in mail.outbox[0].to or self.citizen.email in mail.outbox[1].to)
        self.assertTrue(self.group.email in mail.outbox[0].to or self.group.email in mail.outbox[1].to)

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
        self.assertEquals(len(mail.outbox), 2)  # one for creator subscription, one for manager

        #Login to access the pro page to create a user
        self.client.login(username='manager@a.com', password='test')
        #Refuse the created report
        refused_url = reverse('report_refuse_pro', args=[report_id])
        refused_params = {'refusal_motivation': 'more info'}
        response = self.client.post(refused_url, refused_params, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(mail.outbox), 3)
        #The status of the report must now be REFUSED
        report = Report.objects.get(id=report_id)
        self.assertEquals(report.status, Report.REFUSED)
        #3 mails have been sent, 2 for the report creation and 1 for refusing the report
        #The last one must be sent to the citizen (= the refusing report mail)
        self.assertIn(self.citizen.email, mail.outbox[2].to)

    def testSubscriptionForCitizenMail(self):
        #Send a post request filling in the form to create a report
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post)
        self.assertEquals(response.status_code, 200)
        self.assertIn('report', response.context)

        report_id = response.context['report'].id
        self.assertEquals(len(mail.outbox), 2)  # one for creator subscription, one for manager

        #Send a post request subscribing a citizen to the just created report
        subscribe_url = reverse('subscribe', args=[report_id])
        subscribe_params = {'citizen_email': 'post@test.com'}
        response = self.client.post(subscribe_url, subscribe_params, follow=True)
        self.assertEquals(response.status_code, 200)
        #3 mails have been sent, 2 for the report creation and 1 for subscribing to the report
        self.assertEquals(len(mail.outbox), 3)
        self.assertTrue('post@test.com' in mail.outbox[2].to)

    def testMarkReportAsDoneMail(self):
        #Send a post request filling in the form to create a report
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post)
        self.assertEquals(response.status_code, 200)
        self.assertIn('report', response.context)

        report_id = response.context['report'].id

        self.assertEquals(len(mail.outbox),  2)  # one for creator subscription, one for manager

        #Login to access the pro page
        self.client.login(username='manager@a.com', password='test')
        #Publish the created report
        response = self.client.post(reverse('report_accept_pro', args=[report_id]), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(mail.outbox), 3)

        #Send a post request to mark the report as done
        self.client.logout()
        update_url = reverse('report_update', args=[report_id])
        update_params = {'is_fixed': 'True'}
        response = self.client.post(update_url, update_params)
        self.assertEquals(response.status_code, 302)
        # self.assertIn('/en/report/trou-en-revetements-en-trottoir-en-saint-josse-ten-noode/1', response['Location'])
        #4 mails have been sent, 2 for the report creation and 1 for telling the responsible manager that the report is marked as done, and 1 for the report change to the citizen subscriber
        #FLE is error it should only be send to the responsible
        self.assertEquals(Report.objects.get(id=report_id).status, Report.SOLVED)
        self.assertEquals(len(mail.outbox), 4)
        self.assertTrue(self.manager.email in mail.outbox[3].to)
        #Send another post request to mark the report as done
        response = self.client.post(update_url, update_params)
        self.assertEquals(response.status_code, 302)
        # self.assertIn('/en/report/trou-en-revetements-en-trottoir-en-saint-josse-ten-noode/1', response['Location'])
        #Again 4 mails have been sent, the extra mark as done request will not send an extra email to the responsible manager
        self.assertEquals(len(mail.outbox), 4)

    def testAcceptReportMail(self):
        #Send a post request filling in the form to create a report
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post)
        self.assertEquals(response.status_code, 200)
        self.assertIn('report', response.context)

        report_id = response.context['report'].id
        report = Report.objects.get(id=report_id)

        self.assertEquals(report.subscriptions.all().count(), 2)
        self.assertEquals(len(mail.outbox), 2)  # one for creator subscription, one for manager

        self.client.login(username='manager@a.com', password='test')

        url = reverse('report_accept_pro', args=[report_id])
        response = self.client.get(url, follow=True)

        #last one has to be the creator
        self.assertEquals(len(mail.outbox), 3)
        self.assertIn(self.citizen.email, mail.outbox[2].to)

    def testPublishReportMail(self):
        #Send a post request filling in the form to create a report
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post)
        self.assertEquals(response.status_code, 200)
        self.assertIn('report', response.context)

        report_id = response.context['report'].id
        report = Report.objects.get(id=report_id)

        self.assertEquals(report.subscriptions.all().count(), 2)
        self.assertEquals(len(mail.outbox), 2)  # one for creator subscription, one for manager

        self.client.login(username='manager@a.com', password='test')

        url = reverse('report_publish_pro', args=[report_id])
        response = self.client.get(url, follow=True)
        #import pdb;
        #pdb.set_trace()

        self.assertEquals(len(mail.outbox), 3)

    def testPlannedReportMail(self):
        #Send a post request filling in the form to create a report
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post)
        self.assertEquals(response.status_code, 200)
        self.assertIn('report', response.context)

        report_id = response.context['report'].id

        report = Report.objects.get(id=report_id)
        report.accepted_at = datetime.now()
        report.save()

        self.assertEquals(report.subscriptions.all().count(), 2)
        self.assertEquals(len(mail.outbox), 2)  # one for creator subscription, one for manager

        # Set as planned
        date_planned = (datetime.now() + timedelta(days=1)).strftime("%m/%Y")
        url = '%s?date_planned=%s' % (reverse('report_planned_pro', args=[report_id]), date_planned)

        self.client.login(username='manager@a.com', password='test')
        response = self.client.get(url,   follow=True)

        self.assertEquals(len(mail.outbox), 3)

        # Planned another date
        date_planned = (datetime.now() + timedelta(days=40)).strftime("%m/%Y")
        url = '%s?date_planned=%s' % (reverse('report_planned_pro', args=[report_id]), date_planned)

        self.client.login(username='manager@a.com', password='test')
        response = self.client.get(url, follow=True)

        self.assertEquals(len(mail.outbox), 4)

    def testCreateReportAsProMail(self):
        #creata a report
        self.client.login(username='manager@a.com', password='test')
        response = self.client.post(reverse('report_new_pro') + '?x=150056.538&y=170907.56', self.sample_post_pro)
        self.assertEquals(response.status_code, 200)
        #Should send mail only to responsible
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertTrue(self.group.email in mail.outbox[0].to or self.group.email in mail.outbox[1].to)

    def testReportResolvedAsProMail(self):
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post)
        self.assertEquals(response.status_code, 200)
        self.assertIn('report', response.context)
        report_id = response.context['report'].id
        self.assertEquals(len(mail.outbox), 2)  # one for creator subscription, one for manager

        #Login to access the pro page
        self.client.login(username='manager@a.com', password='test')
        #Publish the created report
        response = self.client.post(reverse('report_accept_pro', args=[report_id]), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(mail.outbox), 3)

        response = self.client.post(reverse('report_fix_pro', args=[report_id]), {'is_fixed': 'True'}, follow=True)
        self.assertEquals(response.status_code, 200)
        #4 mails send 2 for creation, 1 for acceptance and 1 for resolving the issue. The last one should go to the responsible
        self.assertEquals(Report.objects.get(id=report_id).status, Report.SOLVED)
        self.assertEquals(len(mail.outbox), 4)
        self.assertTrue(self.manager.email in mail.outbox[3].to)

    def testAssignToOtherMemberOfSameEntityMail(self):
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post)
        self.assertEquals(response.status_code, 200)
        self.assertIn('report', response.context)
        report_id = response.context['report'].id
        self.assertEquals(len(mail.outbox), 2)  # one for creator subscription, one for manager

        #Login to access the pro page
        self.client.login(username='manager@a.com', password='test')
        #Publish the created report
        response = self.client.post(reverse('report_accept_pro', args=[report_id]), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(mail.outbox), 3)

        response = self.client.get(reverse('report_change_manager_pro',args=[report_id]) + '?manId=manager_' + str(self.manager2.id), {}, follow=True)

        self.assertEquals(response.status_code, 200)
        #Should be 4 mails: 2 for creation, 1 for acceptance and 1 for resolving assigning the issue to other person
        self.assertEquals(len(mail.outbox), 4)
        self.assertTrue(self.manager2.email in mail.outbox[3].to)

    def testAssignToMemberOfOtherEntityMail(self):
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post)
        self.assertEquals(response.status_code, 200)
        self.assertIn('report', response.context)
        report_id = response.context['report'].id
        self.assertEquals(len(mail.outbox), 2)  # one for creator subscription, one for manager

        #Login to access the pro page
        self.client.login(username='manager@a.com', password='test')
        #Publish the created report
        response = self.client.post(reverse('report_accept_pro', args=[report_id]), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(mail.outbox), 3)
        response = self.client.get(reverse('report_change_manager_pro',args=[report_id]) + '?manId=entity_21', {}, follow=True)

        self.assertEquals(response.status_code, 200)
        #Should be 6 mails: 2 for creation, 1 for acceptance and 1 for resolving assigning the issue to other entity, 2 to subcribers (manager, user)
        self.assertEquals(len(mail.outbox), 6)
        self.assertTrue(self.manager3.email in mail.outbox[3].to)
        self.assertIn(self.citizen.email, mail.outbox[4].to + mail.outbox[5].to)
        self.assertIn(self.manager.email, mail.outbox[4].to + mail.outbox[5].to)

    def testAssignToImpetrantMail(self):
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post)
        self.assertEquals(response.status_code, 200)
        self.assertIn('report', response.context)
        report_id = response.context['report'].id
        self.assertEquals(len(mail.outbox), 2)  # one for creator subscription, one for manager

        # Add a worker for this entity
        worker = FMSUser(email="worker@impetrant.be", telephone="0123456789")
        worker.save()
        worker.work_for.add(self.impetrant)

        #Login to access the pro page
        self.client.login(username='manager@a.com', password='test')
        #Publish the created report
        response = self.client.post(reverse('report_accept_pro', args=[report_id]), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(mail.outbox), 3)
        response = self.client.get(reverse('report_change_contractor_pro',args=[report_id]) + '?contractorId=' + str(self.impetrant.id), {}, follow=True)

        self.assertEquals(response.status_code, 200)
        #Should be 6 mails: 2 for creation, 1 for acceptance and 1 for assigning the issue to impetrant, 2 to subcribers (manager, user)
        self.assertEquals(len(mail.outbox), 6)
        self.assertTrue(worker.email in mail.outbox[3].to)
        self.assertIn(self.citizen.email, mail.outbox[4].to + mail.outbox[5].to)
        self.assertIn(self.manager.email, mail.outbox[4].to + mail.outbox[5].to)
        #if the gestionnaire updates the report the impetrant should be informed by mail
        response = self.client.post(reverse('report_show_pro', kwargs={'report_id': report_id, 'slug': 'hello'}), {
            'comment-text': 'new created comment',
            'files-TOTAL_FORMS': 0,
            'files-INITIAL_FORMS': 0,
            'files-MAX_NUM_FORMS': 0
        }, follow=True)
        #One notification should be sent to impetrant to inform him of new comment
        self.assertEquals(len(mail.outbox), 7)
        self.assertTrue(self.impetrant.workers.all()[0].email in mail.outbox[6].to)



    def testAssignToContractorMail(self):
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post)
        self.assertEquals(response.status_code, 200)
        self.assertIn('report', response.context)
        report_id = response.context['report'].id
        self.assertEquals(len(mail.outbox), 2)  # one for creator subscription, one for manager

        # Add a worker for this entity
        worker = FMSUser(email="worker@contractor.be", telephone="0123456789")
        worker.save()
        worker.work_for.add(self.contractor)

        #Login to access the pro page
        self.client.login(username='manager@a.com', password='test')
        #Publish the created report
        response = self.client.post(reverse('report_accept_pro', args=[report_id]), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(mail.outbox), 3)
        response = self.client.get(reverse('report_change_contractor_pro',args=[report_id]) + '?contractorId=' + str(self.contractor.id), {}, follow=True)

        self.assertEquals(response.status_code, 200)
        #Should be 4 mails: 2 for creation, 1 for acceptance and 1 for assigning the issue to contractor
        self.assertEquals(len(mail.outbox), 4)
        self.assertTrue(worker.email in mail.outbox[3].to)
        #If gestionaire adds comment the contractor should be notified
        response = self.client.post(reverse('report_show_pro', kwargs={'report_id': report_id, 'slug': 'hello'}), {
            'comment-text': 'new created comment',
            'files-TOTAL_FORMS': 0,
            'files-INITIAL_FORMS': 0,
            'files-MAX_NUM_FORMS': 0
        }, follow=True)
        #One notification should be sent to contractor to inform him of new comment
        self.assertEquals(len(mail.outbox), 5)
        self.assertTrue(self.contractor.workers.all()[0].email in mail.outbox[4].to)


    def testCitizenUpdatesReportMail(self):
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post)
        self.assertEquals(response.status_code, 200)
        self.assertIn('report', response.context)
        report_id = response.context['report'].id
        self.assertEquals(len(mail.outbox), 2)  # one for creator subscription, one for manager

        #Login to access the pro page
        self.client.login(username='manager@a.com', password='test')
        #Publish the created report
        response = self.client.post(reverse('report_accept_pro', args=[report_id]), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(mail.outbox), 3)
        self.client.logout()
        response = self.client.post(reverse('report_show', kwargs={'report_id': report_id, 'slug': 'hello'}), {
            'comment-text': 'new created comment',
            'citizen-email'   : self.citizen.email,
            'citizen-quality' : 1,
            'files-TOTAL_FORMS': 0,
            'files-INITIAL_FORMS': 0,
            'files-MAX_NUM_FORMS': 0
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        #Should be 4 mails: 2 for creation, 1 for acceptance and 1 for informing responsible about update
        self.assertEquals(len(mail.outbox), 4)
        self.assertTrue(self.manager.email in mail.outbox[3].to)

    def testProUpdatesReportMail(self):
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post)
        self.assertEquals(response.status_code, 200)
        self.assertIn('report', response.context)
        report_id = response.context['report'].id
        self.assertEquals(len(mail.outbox), 2)  # one for creator subscription, one for manager

        #Login to access the pro page
        self.client.login(username='manager@a.com', password='test')
        #Publish the created report
        response = self.client.post(reverse('report_accept_pro', args=[report_id]), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(mail.outbox), 3)
        response = self.client.post(reverse('report_show_pro', kwargs={'report_id': report_id, 'slug': 'hello'}), {
            'comment-text': 'new created comment',
            'files-TOTAL_FORMS': 0,
            'files-INITIAL_FORMS': 0,
            'files-MAX_NUM_FORMS': 0
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        #Should be 3 mails: 2 for creation, 1 for acceptance when the responsible updates no mail is sent
        self.assertEquals(len(mail.outbox), 3)
        self.client.logout()
        self.client.login(username='manager2@a.com', password='test2')
        response = self.client.post(reverse('report_show_pro', kwargs={'report_id': report_id, 'slug': 'hello'}), {
            'comment-text': 'new created comment',
            'files-TOTAL_FORMS': 0,
            'files-INITIAL_FORMS': 0,
            'files-MAX_NUM_FORMS': 0
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        #Should be 4 mails: 2 for creation, 1 for acceptance, 1 to responsable to notify change
        self.assertEquals(len(mail.outbox), 4)
        self.assertTrue(self.manager.email in mail.outbox[3].to)

    def testPublishCommentMail(self):
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post)
        self.assertEquals(response.status_code, 200)
        self.assertIn('report', response.context)
        report_id = response.context['report'].id
        self.assertEquals(len(mail.outbox), 2)  # one for creator subscription, one for manager

        #Login to access the pro page
        self.client.login(username='manager@a.com', password='test')
        #Publish the created report
        response = self.client.post(reverse('report_accept_pro', args=[report_id]), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(mail.outbox), 3)
        response = self.client.post(reverse('report_show_pro', kwargs={'report_id': report_id, 'slug': 'hello'}), {
            'comment-text': 'new created comment',
            'files-TOTAL_FORMS': 0,
            'files-INITIAL_FORMS': 0,
            'files-MAX_NUM_FORMS': 0
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEquals(len(mail.outbox), 3)
        report = Report.objects.get(id=report_id)
        #Now make the comment public
        response = self.client.get(reverse('report_update_attachment', args=[report_id]) + '?updateType=1&attachmentId=' + str(report.comments()[1].id), {}, follow=True)
        self.assertEqual(response.status_code, 200)
        #Now there should be 5 mails: 2 for creation, 1 for acceptance, 1 to subscribers to inform about publish (citizen), Manager who did the update does not get an email
        self.assertEquals(len(mail.outbox), 4)
        self.assertTrue(self.citizen.email in mail.outbox[3].to)

    def testSubscriptionForProMail(self):
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post)
        self.assertEquals(response.status_code, 200)
        self.assertIn('report', response.context)
        report_id = response.context['report'].id
        self.assertEquals(len(mail.outbox), 2)  # one for creator subscription, one for manager

        #Login to access the pro page
        self.client.login(username='manager@a.com', password='test')
        #Publish the created report
        response = self.client.post(reverse('report_accept_pro', args=[report_id]), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(mail.outbox), 3)

        self.client.logout()
        self.client.login(username='manager2@a.com', password='test2')
        response = self.client.get(reverse('subscribe_pro', args=[report_id]), {}, follow=True)
        #Now there should be 4 mails: 2 for creation, 1 for acceptance, 1 to subscriber
        self.assertEquals(len(mail.outbox), 4)
        self.assertTrue(self.manager2.email in mail.outbox[3].to)


    def testMakeReportPrivate(self):
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post)
        self.assertEquals(response.status_code, 200)
        self.assertIn('report', response.context)
        report_id = response.context['report'].id
        self.assertEquals(len(mail.outbox), 2)  # one for creator subscription, one for manager
        #Login to access the pro page
        self.client.login(username='manager@a.com', password='test')
        #Publish the created report
        response = self.client.post(reverse('report_accept_pro', args=[report_id]), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(mail.outbox), 3)
        #Now make the report private
        response = self.client.get(reverse('report_change_switch_privacy', args=[report_id]) + '?privacy=true', follow=True)
        self.assertEquals(response.status_code, 200)
        #one more mail added to subcribers to show that issue became private
        self.assertEquals(len(mail.outbox), 4)
        self.assertTrue(self.citizen.email in mail.outbox[3].to)

    def testMergeReportMail(self):
        #Send a post request filling in the form to create a report
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post)
        self.assertEquals(response.status_code, 200)
        self.assertIn('report', response.context)

        report_id = response.context['report'].id

        self.assertEquals(len(mail.outbox),  2)  # one for creator subscription, one for manager

        #Login to access the pro page
        self.client.login(username='manager@a.com', password='test')

        response2 = self.client.post(reverse('report_new_pro') + '?x=150056.538&y=170907.56', self.sample_post_pro)
        self.assertEquals(response.status_code, 200)
        #Should send mail only to responsible
        self.assertEquals(len(mail.outbox), 3)

        report2_id = response2.context['report'].id

        #Publish the created report
        response3 = self.client.post(reverse('report_accept_pro', args=[report2_id]), follow=True)
        self.assertEquals(response3.status_code, 200)
        self.assertEquals(len(mail.outbox), 4)

        #Merge reports
        url2 = reverse('report_merge_pro',args=[report_id])
        response4 = self.client.get(url2,{"mergeId":report2_id})

        #Reference from merged to kept report
        self.assertEqual(report2_id,Report.objects.get(id=report_id).merged_with.id)
        #A mail has been sent to the creator of the first report to notify him that his report has been merged
        self.assertEquals(len(mail.outbox),5)

    def testSendPDFProMail(self):
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post)
        self.assertEquals(response.status_code, 200)
        self.assertIn('report', response.context)
        report_id = response.context['report'].id
        self.assertEquals(len(mail.outbox), 2)  # one for creator subscription, one for manager

        #Login to access the pro page
        self.client.login(username='manager@a.com', password='test')
        #Publish the created report
        response = self.client.post(reverse('report_accept_pro', args=[report_id]), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(mail.outbox), 3)
        #Now send Pro PDF
        response = self.client.post(reverse('send_pdf', args=[report_id]), self.sample_post_mail_pdf_pro)
        #Now 3 additional mails should be sent
        self.assertEquals(len(mail.outbox), 6)

    def testSendPDFCitizenMail(self):
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post)
        self.assertEquals(response.status_code, 200)
        self.assertIn('report', response.context)
        report_id = response.context['report'].id
        self.assertEquals(len(mail.outbox), 2)  # one for creator subscription, one for manager

        #Login to access the pro page
        self.client.login(username='manager@a.com', password='test')
        #Publish the created report
        response = self.client.post(reverse('report_accept_pro', args=[report_id]), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(mail.outbox), 3)
        #Now send Pro PDF
        response = self.client.post(reverse('send_pdf', args=[report_id]), self.sample_post_mail_pdf_citzen)
        #Now 3 additional mails should be sent
        self.assertEquals(len(mail.outbox), 6)

