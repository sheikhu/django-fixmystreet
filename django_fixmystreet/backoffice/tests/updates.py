from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from django_fixmystreet.fixmystreet.models import Report, ReportCategory, OrganisationEntity, FMSUser
from django_fixmystreet.fixmystreet.utils import dict_to_point

class UpdatesTest(TestCase):

    def setUp(self):
        self.client = Client()

        self.secondary_category = ReportCategory.objects.all()[0]
        self.category = self.secondary_category.category_class

        self.organisation = OrganisationEntity.objects.get(pk=14)

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
        self.manager.organisation = self.organisation
        self.manager.save()
        self.manager.categories.add(self.secondary_category)

        self.report = Report(
            status=Report.CREATED,
            secondary_category=self.secondary_category,
            category=self.category,
            description='Just a test',
            postalcode = 1000,
            address='my address',
            point=dict_to_point({"x":'149776', "y":'170005'}),
            address_number='6h',
            created_by=self.manager
        )
        self.report.save()

    def test_update_planned(self):
        self.client.login(username='manager@a.com', password='test')

        url = reverse('report_planned_pro', args=[self.report.id])

        # Set as planned
        response = self.client.get(url, follow=True)
        report = response.context['report']
        self.assertTrue(report.planned)

        # Set as unplanned
        response = self.client.get(url, follow=True)
        report = response.context['report']
        self.assertFalse(report.planned)

    def test_update_planned_unauth(self):
        url = reverse('report_planned_pro', args=[self.report.id])

        # Set as planned without auth raise an error by accessing report in context
        response = self.client.get(url, follow=True)
        self.assertRaises(KeyError, lambda: response.context['report'])
