from django.test import TestCase
from django.test.client import Client
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import mail
from django.utils.translation import ugettext_lazy as _
from django_fixmystreet.backoffice.views.reports.main import ERROR_MSG_REOPEN_REQUEST_ONLY_CLOSED, \
    ERROR_MSG_REOPEN_REQUEST_90_DAYS, SUCCESS_MSG_REOPEN_REQUEST_CONFIRM

from django_fixmystreet.fixmystreet.models import (
    Report, ReportCategory, OrganisationEntity, ReportAttachment,
    FMSUser, OrganisationEntitySurface,
    GroupMailConfig, ReportComment, ReportEventLog)
from django.contrib.gis.geos import Polygon

from datetime import datetime, timedelta


class ReopenRequestTest(TestCase):

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

        self.group = OrganisationEntity(
            type="D",
            name_nl="Werken",
            name_fr="Travaux",
            phone="090987",
            dependency=OrganisationEntity.objects.get(pk=14),
            email="test1@email.com"
            )
        self.group.save()
        self.group.dispatch_categories.add(ReportCategory.objects.get(pk=1))

        self.group_mail_config = GroupMailConfig()
        self.group_mail_config.group = self.group
        self.group_mail_config.save()

        self.manager.memberships.create(organisation=self.group, contact_user=True)

        self.client = Client()

        self.manager2 = FMSUser(
            is_active=True,
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

        self.group2 = OrganisationEntity(
            type="D",
            name_nl="Werken",
            name_fr="Travaux",
            phone="090987",
            dependency=OrganisationEntity.objects.get(pk=21),
            email="test2@email.com"
        )
        self.group2.save()
        self.group2.dispatch_categories.add(ReportCategory.objects.get(pk=2))
        self.group2.dispatch_categories.add(ReportCategory.objects.get(pk=1))

        p1 = (148776, 171005)
        p2 = (150776, 171005)
        p3 = (150776, 169005)
        p4 = (148776, 169005)

        surface = OrganisationEntitySurface(
            geom=Polygon([p1, p2, p3, p4, p1]),
            owner=OrganisationEntity.objects.get(pk=14),
        )
        surface.save()

        self.manager2.memberships.create(organisation=self.group2)

        self.manager3 = FMSUser(
            is_active=True,
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

        self.manager3.memberships.create(organisation=self.group2)

        self.impetrant = OrganisationEntity(
            name_nl="MIVB",
            name_fr="STIB",
            email="stib@mivb.be")

        self.impetrant.save()

        self.contractor = OrganisationEntity(
            name_nl="Fabricom GDF",
            name_fr="Fabricom GDF",
            email="contractor@email.com")
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

        ##### Following data was created specifically for the reopen_request tests #######

        self.citizen_reopen_request = FMSUser(
            telephone="987654321",
            last_used_language="fr",
            first_name="citizen_reopen_request",
            last_name="citizen_reopen_request",
            email="citizen@reopenrequest.cirb"
        )
        self.citizen_reopen_request.save()

        self.sample_post_reopen_request_pro = {
            'reopen-text': 'this is the reopen request comment',
            'reopen-reason': 1
        }

        self.sample_post_reopen_request = {
            'reopen-text': 'this is the reopen request comment',
            'reopen-reason': 1,
            'citizen-quality': 2,
            'citizen-email': self.citizen_reopen_request.email,
            'citizen-telephone': self.citizen_reopen_request.telephone,
            'citizen-last_name': self.citizen_reopen_request.last_name,
        }

    def testReopenRequestMailByPro(self):
        # New report
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post, follow=True)
        report = response.context['report']

        # Set status to Processed
        report.status = Report.PROCESSED
        report.close_date = datetime.now()
        report.save()

        # Login to access the pro page
        self.client.login(username='manager@a.com', password='test')

        # Request reopen report
        response = self.client.post(reverse('report_reopen_request_pro', args=["hello", report.id]), self.sample_post_reopen_request_pro, follow=True)

        #check redirect
        url_redirect = reverse('report_show_pro', args=[report.get_slug(), report.id])
        self.assertRedirects(response, url_redirect, status_code=302, target_status_code=200)

        #test there is a message
        success_msg = _(str(list(response.context["messages"])[0]))
        self.assertEqual(success_msg, _(SUCCESS_MSG_REOPEN_REQUEST_CONFIRM))

        # Fetch activities
        activities = report.activities.all()

        # Assert
        self.assertEqual(activities.count(), 3)
        self.assertEquals(ReportEventLog.REOPEN_REQUEST, activities[2].event_type)


    def testReopenRequestMailByCitizen(self):
        # New report
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post, follow=True)
        report = response.context['report']

        # Set status to Processed
        report.status = Report.PROCESSED
        report.close_date = datetime.now()
        report.save()

        # Request reopen report
        response = self.client.post(reverse('report_reopen_request', args=["hello", report.id]), self.sample_post_reopen_request, follow=True)
        url = reverse('report_show', args=[report.get_slug(), report.id])
        self.assertRedirects(response, url, status_code=302, target_status_code=200)

        #test there is a message
        success_msg = _(str(list(response.context["messages"])[0]))
        self.assertEqual(success_msg, _(SUCCESS_MSG_REOPEN_REQUEST_CONFIRM))

        # Fetch activities
        activities = report.activities.all()

        # Assert
        self.assertEqual(activities.count(), 3)
        self.assertEquals(ReportEventLog.REOPEN_REQUEST, activities[2].event_type)


    #Test that you cannot access the page if you don't have status closed. (Should be tested with all status
    #except PROCESSED but let's test it with REFUSED)
    def testReopenRequestOnlyForProcessed(self):
        # New report
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post, follow=True)
        report = response.context['report']

        comment = ReportComment(report_id=report.id, text='test', type=3)
        comment.save()

        # Set status to REFUSED (we want a status different that
        report.status = Report.REFUSED
        report.close_date = datetime.now()
        report.save()

        # Request reopen report
        response = self.client.post(reverse('report_reopen_request', args=["hello", report.id]), self.sample_post_reopen_request, follow=True)
        url = reverse('report_show', args=[report.get_slug(), report.id])
        self.assertRedirects(response, url, status_code=302, target_status_code=200)

        error_msg = _(str(list(response.context["messages"])[0]))
        self.assertEqual(error_msg, _(ERROR_MSG_REOPEN_REQUEST_ONLY_CLOSED))

        # Fetch activities
        activities = report.activities.all()

        # Assert
        self.assertEqual(activities.count(), 2)
        self.assertEquals(ReportEventLog.REFUSE, activities[1].event_type) #this can't be ReportEventLog.REOPEN_REQUEST


    def testReopenRequestNotAfter90Days(self):
        # New report
        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post, follow=True)
        report = response.context['report']

        #limit date is 90 days. let's check a report closed 91 days ago
        report.status = Report.PROCESSED
        limit_date_plus_one = datetime.now() - timedelta(days=91)
        report.close_date = limit_date_plus_one
        report.save()

        # Request reopen report
        response = self.client.post(reverse('report_reopen_request', args=["hello", report.id]), self.sample_post_reopen_request, follow=True)
        url = reverse('report_show', args=[report.get_slug(), report.id])
        self.assertRedirects(response, url, status_code=302, target_status_code=200)

        error_msg = _(str(list(response.context["messages"])[0]))
        self.assertEqual(error_msg, _(ERROR_MSG_REOPEN_REQUEST_90_DAYS))

        # Fetch activities
        activities = report.activities.all()

        # Assert
        self.assertEqual(activities.count(), 2)
        self.assertEquals(ReportEventLog.CLOSE, activities[1].event_type)