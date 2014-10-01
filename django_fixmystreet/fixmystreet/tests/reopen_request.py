from django.test import TestCase
from django.test.client import Client
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import mail

from django_fixmystreet.fixmystreet.models import (
    Report, ReportCategory, OrganisationEntity, ReportAttachment,
    FMSUser, OrganisationEntitySurface
)
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
        self.manager.memberships.create(organisation=self.group, contact_user=True)

        self.client = Client()

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

    # def testReopenRequestMail(self):
    #     #Send a post request filling in the form to create a report
    #     response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post, follow=True)
    #
    #     self.assertIn('report', response.context)
    #
    #     report_id = response.context['report'].id
    #     report = Report.objects.get(id=report_id)
    #     self.assertEquals(report.subscriptions.all().count(), 2)
    #     self.assertEquals(len(mail.outbox), 2)
    #
    #     #Login to access the pro page to create a user
    #     self.client.login(username='manager@a.com', password='test')
    #
    #     #Accept the created report
    #     response = self.client.get(reverse('report_accept_pro', args=[report.id]), follow=True)
    #     #The status of the report must now be MANAGER_ASSIGNED
    #     self.assertEquals(response.status_code, 200)
    #
    #     report = Report.objects.get(id=report.id)
    #     self.assertEquals(report.status, Report.MANAGER_ASSIGNED)
    #     #3 mails have been sent, 2 for the report creation + 1 notification to author for the report publishing
    #     self.assertEquals(len(mail.outbox), 3)
    #     #Close the report
    #     response = self.client.get(reverse('report_close_pro', args=[report.id]), follow=True)
    #     self.assertEquals(response.status_code, 200)
    #
    #     report = Report.objects.get(id=report.id)
    #     self.assertEquals(report.status, Report.PROCESSED)
    #     #4 mails have been sent, 2 for the report creation, 1 for the report publishing and 1 for closing the report
    #     self.assertEquals(len(mail.outbox), 4)
    #     #The last one must be sent to the citizen (= the closing report mail)
    #     self.assertIn(self.citizen.email, mail.outbox[3].to)