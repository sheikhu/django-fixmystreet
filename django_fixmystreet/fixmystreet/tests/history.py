from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.html import escape

from django_fixmystreet.fixmystreet.models import Report, ReportCategory, OrganisationEntity, FMSUser

class HistoryTest(TestCase):
    fixtures = ["list_items"]

    def setUp(self):
        self.citizen = FMSUser(
            telephone="0123456789",
            last_used_language="fr",
            first_name="Fake first name",
            last_name="Fake last name",
            email="citizen@a.com"
        )
        self.citizen.save()
        self.citizen2 = FMSUser(
            telephone="9876543210",
            last_used_language="nl",
            first_name="Fake first name2",
            last_name="Fake last name2",
            email="citizen2@a.com"
        )
        self.citizen2.save()
        self.citizen3 = FMSUser(
            telephone="5649783210",
            last_used_language="nl",
            first_name="Fake first name3",
            last_name="Fake last name3",
            email="citizen3@a.com"
        )
        self.citizen3.save()
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
        self.manager2.categories.add(ReportCategory.objects.get(pk=1))

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

        self.impetrant = OrganisationEntity(
            name_nl="MIVB",
            name_fr="STIB",
            commune=False,
            region=False,
            subcontractor=False,
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

        self.client = Client()

        self.sample_post_citizen = {
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
            'report-terms_of_use_validated': True
        }

        self.sample_post_pro = {
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
            'report-terms_of_use_validated': True
        }

    def testCreateReportHistoryCitizen(self):
        #Send a post request filling in the form to create a report
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post_citizen)
        self.assertEquals(response.status_code, 200)
        # self.assertIn('/en/report/trou-en-revetements-en-trottoir-en-saint-josse-ten-noode/1', response['Location'])
        # check the history if it contains 1 line and that the content is correct
        report_id = response.context['report'].id
        report = Report.objects.get(id=report_id)
        activities = report.activities.all()
        self.assertEquals(activities.all().count(), 1)
        
        url = '%s?report_id=%s' % (reverse('search_ticket'), report.id)
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, self.calculatePrint(activities[0]))
        self.assertNotContains(response, self.calculatePrintPro(activities[0]))
       
        #Now redo the test with a manager user
        self.client.login(username='manager@a.com', password='test')
        url = '%s?report_id=%s' % (reverse('search_ticket_pro'), report.id)
        response = self.client.get(url, follow=True)
        report = Report.objects.get(id=report_id)
        activities = report.activities.all()
        self.assertEquals(activities.all().count(), 1)
        #check if the page contains the exact string as it should be generated
        self.assertEquals(response.status_code, 200)        
        self.assertContains(response, self.calculatePrintPro(activities[0]))

    def testCreateReportHistoryPro(self):
        self.client.login(username='manager@a.com', password='test')
        response = self.client.post(reverse('report_new_pro') + '?x=150056.538&y=170907.56', self.sample_post_pro)
        self.assertEquals(response.status_code, 200)
        report_id = response.context['report'].id
        report = Report.objects.get(id=report_id)
        activities = report.activities.all()
        self.assertEquals(activities.all().count(), 1)
        url = '%s?report_id=%s' % (reverse('search_ticket_pro'), report.id)
        self.client.login(username='manager@a.com', password='test')
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, self.calculatePrintPro(activities[0]))
        self.client.logout()
        #now test as citizen
        url = '%s?report_id=%s' % (reverse('search_ticket'), report.id)
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, self.calculatePrint(activities[0]))
        self.assertNotContains(response, self.calculatePrintPro(activities[0]))

    def testValidateReport(self):
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post_citizen)
        self.assertEquals(response.status_code, 200)
        report_id = response.context['report'].id

        self.client.login(username='manager@a.com', password='test')
        url = reverse('report_accept_pro', args=[report_id])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        report = response.context['report']
        self.assertTrue(report.accepted_at is not None)

        self.client.logout();
        #check if the status is updated
        url = '%s?report_id=%s' % (reverse('search_ticket'), report_id)
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        report = Report.objects.get(id=report_id)
        activities = report.activities.all()
        self.assertEquals(activities.all().count(), 2)
        self.assertContains(response, self.calculatePrint(activities[1]))
        self.assertNotContains(response, self.calculatePrintPro(activities[1]))

        #now check status as pro
        self.client.login(username='manager@a.com', password='test')
        url = '%s?report_id=%s' % (reverse('search_ticket_pro'), report_id)
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        report = Report.objects.get(id=report_id)
        activities = report.activities.all()
        self.assertEquals(activities.all().count(), 2)
        self.assertContains(response, self.calculatePrintPro(activities[1]))
        
    def testInvalidateReport(self):
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post_citizen)
        self.assertEquals(response.status_code, 200)
        report_id = response.context['report'].id

        self.client.login(username='manager@a.com', password='test')
        url = reverse('report_refuse_pro', args=[report_id])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

        self.client.logout();
        #check if the status is updated
        url = '%s?report_id=%s' % (reverse('search_ticket'), report_id)
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        report = Report.objects.get(id=report_id)
        activities = report.activities.all()
        self.assertEquals(activities.all().count(), 2)
        self.assertContains(response, self.calculatePrint(activities[1]))
        self.assertNotContains(response, self.calculatePrintPro(activities[1]))

        #now check status as pro
        self.client.login(username='manager@a.com', password='test')
        url = '%s?report_id=%s' % (reverse('search_ticket_pro'), report_id)
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        report = Report.objects.get(id=report_id)
        activities = report.activities.all()
        self.assertEquals(activities.all().count(), 2)
        self.assertContains(response, self.calculatePrintPro(activities[1]))

    def testClosureReport(self):
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post_citizen)
        self.assertEquals(response.status_code, 200)
        report_id = response.context['report'].id
        self.client.login(username='manager@a.com', password='test')
        url = reverse('report_close_pro', args=[report_id])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        report = response.context['report']
        self.assertTrue(report.close_date is not None)
        self.client.logout();

        #check if the status is updated
        url = '%s?report_id=%s' % (reverse('search_ticket'), report_id)
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        report = Report.objects.get(id=report_id)
        activities = report.activities.all()
        self.assertEquals(activities.all().count(), 2)
        self.assertContains(response, self.calculatePrint(activities[1]))
        self.assertNotContains(response, self.calculatePrintPro(activities[1]))

        #now check status as pro
        self.client.login(username='manager@a.com', password='test')
        url = '%s?report_id=%s' % (reverse('search_ticket_pro'), report_id)
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        report = Report.objects.get(id=report_id)
        activities = report.activities.all()
        self.assertEquals(activities.all().count(), 2)
        self.assertContains(response, self.calculatePrintPro(activities[1]))

    def testResolvedByCitizenReport(self):
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post_citizen)
        self.assertEquals(response.status_code, 200)
        report_id = response.context['report'].id

        #first accept the report before citizen can update
        self.client.login(username='manager@a.com', password='test')
        url = reverse('report_accept_pro', args=[report_id])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        report = response.context['report']
        self.assertTrue(report.accepted_at is not None)

        self.client.logout()

        response = self.client.post(reverse('report_update', args=[report_id]), {'is_fixed':'True'}, follow=True)
        self.assertEqual(response.status_code, 200)

        #check that activity is not visible to citizen
        url = '%s?report_id=%s' % (reverse('search_ticket'), report_id)
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        report = Report.objects.get(id=report_id)
        activities = report.activities.all()
        self.assertEquals(activities.all().count(), 3)
        self.assertNotContains(response, self.calculatePrint(activities[2]))
        self.assertNotContains(response, self.calculatePrintPro(activities[2]))

        #check that activity is visible to pro
        self.client.login(username='manager@a.com', password='test')
        url = '%s?report_id=%s' % (reverse('search_ticket_pro'), report_id)
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        report = Report.objects.get(id=report_id)
        activities = report.activities.all()
        self.assertEquals(activities.all().count(), 3)
        self.assertContains(response, self.calculatePrintPro(activities[2]))


    def testResolvedByProReport(self):
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post_citizen)
        self.assertEquals(response.status_code, 200)
        report_id = response.context['report'].id

        #first accept the report before citizen can update
        self.client.login(username='manager@a.com', password='test')
        url = reverse('report_accept_pro', args=[report_id])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        report = response.context['report']
        self.assertTrue(report.accepted_at is not None)

        response = self.client.post(reverse('report_fix_pro', args=[report_id]), {'is_fixed':'True'}, follow=True)
        self.assertEqual(response.status_code, 200)

        #first check that pro has right status
        url = '%s?report_id=%s' % (reverse('search_ticket_pro'), report_id)
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        report = Report.objects.get(id=report_id)
        activities = report.activities.all()
        self.assertEquals(activities.all().count(), 3)
        self.assertContains(response, self.calculatePrintPro(activities[2]))
        self.client.logout()

        #Now check for citizen
        url = '%s?report_id=%s' % (reverse('search_ticket'), report_id)
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        report = Report.objects.get(id=report_id)
        activities = report.activities.all()
        self.assertEquals(activities.all().count(), 3)
        self.assertNotContains(response, self.calculatePrint(activities[2]))
        self.assertNotContains(response, self.calculatePrintPro(activities[2]))

    def testCitizenUpdatesReport(self):
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post_citizen)
        self.assertEquals(response.status_code, 200)
        report_id = response.context['report'].id

        #first accept the report before citizen can update
        self.client.login(username='manager@a.com', password='test')
        url = reverse('report_accept_pro', args=[report_id])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        report = response.context['report']
        self.assertTrue(report.accepted_at is not None)

        self.client.logout()
        response = self.client.post(reverse('report_show', kwargs={'report_id': report_id, 'slug':'hello'}), {
            'comment-text': 'new created comment',
            'files-TOTAL_FORMS': 0,
            'files-INITIAL_FORMS': 0,
            'files-MAX_NUM_FORMS': 0
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        report = Report.objects.get(id=report_id)
        activities = report.activities.all()
        self.assertEqual(report.comments().count(), 2)
         #check that there is no message
        url = '%s?report_id=%s' % (reverse('search_ticket'), report_id)
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEqual(activities.all().count(), 3)
        self.assertNotContains(response, self.calculatePrint(activities[2]))
        self.assertNotContains(response, self.calculatePrintPro(activities[2]))

        #Now check the message for pro users
        self.client.login(username='manager@a.com', password='test')
        url = '%s?report_id=%s' % (reverse('search_ticket_pro'), report_id)
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        report = Report.objects.get(id=report_id)
        activities = report.activities.all()
        self.assertEquals(activities.all().count(), 3)
        self.assertContains(response, self.calculatePrintPro(activities[2]))
        self.client.logout()
       
    def testProUpdatesReport(self):
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post_citizen)
        self.assertEquals(response.status_code, 200)
        report_id = response.context['report'].id

        #first accept the report before citizen can update
        self.client.login(username='manager@a.com', password='test')
        url = reverse('report_accept_pro', args=[report_id])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        report = response.context['report']
        self.assertTrue(report.accepted_at is not None)

        response = self.client.post(reverse('report_show_pro', kwargs={'report_id': report_id, 'slug':'hello'}), {
            'comment-text': 'new created comment',
            'files-TOTAL_FORMS': 0,
            'files-INITIAL_FORMS': 0,
            'files-MAX_NUM_FORMS': 0
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        report = Report.objects.get(id=report_id)
        activities = report.activities.all()
        self.assertEqual(report.comments().count(), 2)

        #Check for pro user first
        url = '%s?report_id=%s' % (reverse('search_ticket_pro'), report_id)
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        report = Report.objects.get(id=report_id)
        activities = report.activities.all()
        self.assertEquals(activities.all().count(), 3)
        self.assertContains(response, self.calculatePrintPro(activities[2]))

        self.client.logout()
        #Check for citizen user
        url = '%s?report_id=%s' % (reverse('search_ticket'), report_id)
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEqual(activities.all().count(), 3)
        self.assertNotContains(response, self.calculatePrint(activities[2]))
        self.assertNotContains(response, self.calculatePrintPro(activities[2]))

    def testCitizenSubscribesToReport(self):
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post_citizen)
        self.assertEquals(response.status_code, 200)
        report_id = response.context['report'].id

        response = self.client.get(reverse('subscribe',args=[report_id]) + '?citizen_email=' + self.citizen2.email, {}, follow=True)
        report = Report.objects.get(id=report_id)
        activities = report.activities.all()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(report.subscriptions.filter(subscriber=self.citizen2).exists())
        self.assertFalse(report.subscriptions.filter(subscriber=self.citizen3).exists())
        self.assertFalse(report.subscriptions.filter(subscriber=self.manager2).exists())
        self.assertEquals(activities.all().count(), 1)
        

    def testProSubscribesToReport(self):
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post_citizen)
        self.assertEquals(response.status_code, 200)
        report_id = response.context['report'].id

        self.client.login(username='manager2@a.com', password='test2')
        response = self.client.get(reverse('subscribe_pro',args=[report_id]), {}, follow=True)
        report = Report.objects.get(id=report_id)
        activities = report.activities.all()
        self.assertTrue(report.subscriptions.filter(subscriber=self.citizen).exists())
        self.assertFalse(report.subscriptions.filter(subscriber=self.citizen2).exists())
        self.assertFalse(report.subscriptions.filter(subscriber=self.citizen3).exists())
        self.assertTrue(report.subscriptions.filter(subscriber=self.manager2).exists())
        self.assertEquals(activities.all().count(), 1)


    def testAssignToOtherMemberOfSameEntity(self):
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post_citizen)
        self.assertEquals(response.status_code, 200)
        report_id = response.context['report'].id

         #first accept the report before citizen can update
        self.client.login(username='manager@a.com', password='test')
        url = reverse('report_accept_pro', args=[report_id])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        report = response.context['report']
        self.assertTrue(report.accepted_at is not None)

        response = self.client.get(reverse('report_change_manager_pro',args=[report_id]) + '?manId=manager_' + str(self.manager2.id), {}, follow=True)      
        self.assertEquals(response.status_code, 200)
        report = Report.objects.get(id=report_id)
        activities = report.activities.all()
        self.assertEquals(activities.all().count(), 3)

        url = '%s?report_id=%s' % (reverse('search_ticket_pro'), report_id)
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        report = Report.objects.get(id=report_id)
        activities = report.activities.all()
        self.assertEquals(activities.all().count(), 3)
        self.assertContains(response, self.calculatePrintPro(activities[2]))

        #now check as citizen no status update should be visible
        self.client.logout()
        #Check for citizen user
        url = '%s?report_id=%s' % (reverse('search_ticket'), report_id)
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        report = Report.objects.get(id=report_id)
        activities = report.activities.all()
        self.assertEqual(activities.all().count(), 3)
        self.assertNotContains(response, self.calculatePrint(activities[2]))
        self.assertNotContains(response, self.calculatePrintPro(activities[2]))

    def testAssignToOtherEntity(self):
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post_citizen)
        self.assertEquals(response.status_code, 200)
        report_id = response.context['report'].id
         #first accept the report before citizen can update
        self.client.login(username='manager@a.com', password='test')
        url = reverse('report_accept_pro', args=[report_id])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        report = response.context['report']
        self.assertTrue(report.accepted_at is not None)
        self.client.login(username='manager@a.com', password='test')
        response = self.client.get(reverse('report_change_manager_pro',args=[report_id]) + '?manId=entity_21', {}, follow=True)      
        self.assertEquals(response.status_code, 200)
        report = Report.objects.get(id=report_id)
        activities = report.activities.all()
        self.assertEquals(activities.all().count(), 3)
        url = '%s?report_id=%s' % (reverse('search_ticket_pro'), report_id)
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, self.calculatePrintPro(activities[2]))

        #Now test to see that citizen sees the correct information
        self.client.logout()
        url = '%s?report_id=%s' % (reverse('search_ticket'), report_id)
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        report = Report.objects.get(id=report_id)
        activities = report.activities.all()
        self.assertEqual(activities.all().count(), 3)
        self.assertContains(response, self.calculatePrint(activities[2]))
        self.assertNotContains(response, self.calculatePrintPro(activities[2]))

   
    def testAssignToContractor(self):
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post_citizen)
        self.assertEquals(response.status_code, 200)
        report_id = response.context['report'].id
         #first accept the report before citizen can update
        self.client.login(username='manager@a.com', password='test')
        url = reverse('report_accept_pro', args=[report_id])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        report = response.context['report']
        self.assertTrue(report.accepted_at is not None)
        self.client.login(username='manager@a.com', password='test')
        response = self.client.get(reverse('report_change_contractor_pro',args=[report_id]) + '?contractorId=' + str(self.contractor.id), {}, follow=True)      
        self.assertEquals(response.status_code, 200)
        report = Report.objects.get(id=report_id)
        activities = report.activities.all()
        self.assertEquals(activities.all().count(), 3)
        url = '%s?report_id=%s' % (reverse('search_ticket_pro'), report_id)
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, escape(self.calculatePrintPro(activities[2])))

        #Now see if the information for the citizen is ok
        self.client.logout()
        url = '%s?report_id=%s' % (reverse('search_ticket'), report_id)
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        report = Report.objects.get(id=report_id)
        activities = report.activities.all()
        self.assertEqual(activities.all().count(), 3)
        self.assertNotContains(response, self.calculatePrint(activities[2]))
        self.assertNotContains(response, self.calculatePrintPro(activities[2]))
        

    def testAssignToImpetrant(self):
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post_citizen)
        self.assertEquals(response.status_code, 200)
        report_id = response.context['report'].id
         #first accept the report before citizen can update
        self.client.login(username='manager@a.com', password='test')
        url = reverse('report_accept_pro', args=[report_id])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        report = response.context['report']
        self.assertTrue(report.accepted_at is not None)
        self.client.login(username='manager@a.com', password='test')
        response = self.client.get(reverse('report_change_contractor_pro',args=[report_id]) + '?contractorId=' + str(self.impetrant.id), {}, follow=True)      
        self.assertEquals(response.status_code, 200)
        report = Report.objects.get(id=report_id)
        activities = report.activities.all()
        self.assertEquals(activities.all().count(), 3)
        url = '%s?report_id=%s' % (reverse('search_ticket_pro'), report_id)
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, self.calculatePrintPro(activities[2]))
        #Now see if the information for the citizen is ok
        self.client.logout()
        url = '%s?report_id=%s' % (reverse('search_ticket'), report_id)
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        report = Report.objects.get(id=report_id)
        activities = report.activities.all()
        self.assertEqual(activities.all().count(), 3)
        self.assertContains(response, self.calculatePrint(activities[2]))

    def testMakeCommentPublic(self):
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post_citizen)
        self.assertEquals(response.status_code, 200)
        report_id = response.context['report'].id
         #first accept the report before citizen can update
        self.client.login(username='manager@a.com', password='test')
        url = reverse('report_accept_pro', args=[report_id])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        report = response.context['report']
        self.assertTrue(report.accepted_at is not None)
        #now add comment
        response = self.client.post(reverse('report_show_pro', kwargs={'report_id': report_id, 'slug':'hello'}), {
            'comment-text': 'new created comment',
            'files-TOTAL_FORMS': 0,
            'files-INITIAL_FORMS': 0,
            'files-MAX_NUM_FORMS': 0
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        report = Report.objects.get(id=report_id)
        self.assertEqual(report.comments().count(), 2)
        #Now make the comment public
        response = self.client.get(reverse('report_update_attachment', args=[report_id]) + '?updateType=1&attachmentId=' + str(report.comments()[1].id), {}, follow=True )
        self.assertEqual(response.status_code, 200)
        report = Report.objects.get(id=report_id)
        activities = report.activities.all()
        self.assertEqual(activities.all().count(), 4) #still does not work as the message is not shown yet
        url = '%s?report_id=%s' % (reverse('search_ticket_pro'), report_id)
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, self.calculatePrintPro(activities[3]))

        #now test for citizen
        self.client.logout()
        url = '%s?report_id=%s' % (reverse('search_ticket'), report_id)
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        report = Report.objects.get(id=report_id)
        activities = report.activities.all()
        self.assertEqual(activities.all().count(), 4)
        self.assertContains(response, self.calculatePrint(activities[3]))
        self.assertNotContains(response, self.calculatePrintPro(activities[3]))
        
    def testPublish(self):
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post_citizen)
        self.assertEquals(response.status_code, 200)
        report_id = response.context['report'].id
         #first accept the report before citizen can update
        self.client.login(username='manager@a.com', password='test')
        url = reverse('report_accept_pro', args=[report_id])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        report = response.context['report']
        self.assertTrue(report.accepted_at is not None)
        response = self.client.get(reverse('report_publish_pro', args=[report_id]), {}, follow=True )
        self.assertEqual(response.status_code, 200)
        url = '%s?report_id=%s' % (reverse('search_ticket_pro'), report_id)
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def calculatePrint(self, activity):
        user_to_display = _("a citizen")

        if activity.user:
            if activity.user.fmsuser.is_citizen():
                user_to_display = _("a citizen")

            if activity.user.fmsuser.is_pro():
                user_to_display = activity.user.fmsuser.get_organisation()

        return activity.EVENT_TYPE_TEXT[activity.event_type].format(
            user=user_to_display,
            organisation=activity.organisation,
            related_new=activity.related_new
        )

    def calculatePrintPro(self, activity):
        user_to_display = _("a citizen")

        if activity.user:
            if activity.user.fmsuser.is_citizen():
                user_to_display = activity.user.get_full_name() or activity.user

            if activity.user.fmsuser.is_pro():
                user_to_display = u'%s %s' %(activity.user.fmsuser.get_organisation(), activity.user.get_full_name() or activity.user)

        return activity.EVENT_TYPE_TEXT[activity.event_type].format(
            user=user_to_display,
            organisation=activity.organisation,
            related_new=activity.related_new
        )
    
        


        #Mail to creator and manager must be sent
        #self.assertTrue(self.citizen.email in mail.outbox[0].to or self.citizen.email in mail.outbox[1].to)
        #self.assertTrue(self.manager.email in mail.outbox[0].to or self.manager.email in mail.outbox[1].to)