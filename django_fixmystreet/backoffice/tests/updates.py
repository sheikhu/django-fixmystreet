
from unittest import skip
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from django_fixmystreet.fixmystreet.models import Report, ReportCategory, OrganisationEntity, FMSUser, UserOrganisationMembership
from django_fixmystreet.fixmystreet.utils import dict_to_point

from datetime import datetime, timedelta


class UpdatesTest(TestCase):

    fixtures = ["bootstrap", "list_items"]

    def setUp(self):
        self.client = Client()

        self.secondary_category = ReportCategory.objects.all()[0]
        self.category = self.secondary_category.category_class

        self.organisation = OrganisationEntity.objects.get(pk=14)
        self.organisation2 = OrganisationEntity.objects.get(pk=15)

        self.group = OrganisationEntity(
            type="D",
            name_nl="Werken",
            name_fr="Travaux",
            phone="090987",
            dependency=self.organisation,
            email="test@email.com"
            )
        self.group.save()

        self.group2 = OrganisationEntity(
            type="D",
            name_nl="Werken2",
            name_fr="Travaux2",
            phone="090987",
            dependency=self.organisation2,
            email="test2@email.com"
            )
        self.group2.save()

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

        self.manager2 = FMSUser(
            telephone="0123456789",
            last_used_language="fr",
            password='test',
            first_name="manager2",
            last_name="manager2",
            email="manager2@a.com",
            manager=True
        )
        self.manager2.set_password('test')
        self.manager2.organisation = self.organisation
        self.manager2.save()
        self.manager2.categories.add(self.secondary_category)

        self.usergroupmembership = UserOrganisationMembership(user_id=self.manager.id, organisation_id=self.group.id, contact_user=True)
        self.usergroupmembership.save()

        self.usergroupmembership = UserOrganisationMembership(user_id=self.manager2.id, organisation_id=self.group2.id, contact_user=True)
        self.usergroupmembership.save()

        self.report = Report(
            status=Report.CREATED,
            secondary_category=self.secondary_category,
            category=self.category,
            description='Just a test',
            postalcode=1000,
            address='my address',
            point=dict_to_point({"x": '149776', "y": '170005'}),
            address_number='6h',
            created_by=self.manager,
            accepted_at=datetime.now()
        )
        self.report.save()

    def test_change_manager(self):
        """Tests manager change assigned to a report and test the view of it."""

        report = self.report
        report.responsible_department = self.group
        report.save()

        self.client.login(username='manager@a.com', password='test')

        """Change manager department"""
        url = reverse('report_change_manager_pro', args=[report.id])
        response = self.client.get("{0}?manId=department_{1}".format(url, self.group2.id), follow=True)
        self.assertEqual(response.status_code, 200)

        self.assertIsNotNone(report.responsible_department)

        """Change manager entity"""
        url = reverse('report_change_manager_pro', args=[report.id])
        response = self.client.get(url+'?manId=entity_14', follow=True)
        self.assertEqual(response.status_code, 200)

        self.assertIsNotNone(report.responsible_department)

    def test_update_planned(self):
        self.client.login(username='manager@a.com', password='test')

        date_planned = (datetime.now() + timedelta(days=1)).strftime("%m/%Y")
        url = '%s?date_planned=%s' % (reverse('report_planned_pro', args=[self.report.id]), date_planned)

        # Set as planned
        self.client.login(username='manager@a.com', password='test')
        response = self.client.get(url, follow=True)
        report = response.context['report']

        self.assertTrue(report.planned)
        self.assertTrue(report.date_planned)

    def test_update_planned_max_date(self):
        self.client.login(username='manager@a.com', password='test')

        max_date_planned = self.report.accepted_at + timedelta(days=450)
        url = '%s?date_planned=%s' % (reverse('report_planned_pro', args=[self.report.id]), max_date_planned.strftime("%m/%Y"))

        # Set as planned
        self.client.login(username='manager@a.com', password='test')
        response = self.client.get(url, follow=True)
        report = response.context['report']

        self.assertFalse(report.planned)
        self.assertFalse(report.date_planned)

    def test_update_planned_min_date(self):
        self.client.login(username='manager@a.com', password='test')

        min_date_planned = self.report.accepted_at - timedelta(days=366)
        url = '%s?date_planned=%s' % (reverse('report_planned_pro', args=[self.report.id]), min_date_planned.strftime("%m/%Y"))

        # Set as planned
        self.client.login(username='manager@a.com', password='test')
        response = self.client.get(url, follow=True)
        report = response.context['report']

        self.assertFalse(report.planned)
        self.assertFalse(report.date_planned)

    def test_update_planned_not_accepted(self):
        self.client.login(username='manager@a.com', password='test')

        self.report.accepted_at = None
        self.report.save()

        date_planned = (datetime.now() + timedelta(days=1)).strftime("%m/%Y")
        url = '%s?date_planned=%s' % (reverse('report_planned_pro', args=[self.report.id]), date_planned)

        # Set as planned
        self.client.login(username='manager@a.com', password='test')
        response = self.client.get(url, follow=True)
        report = response.context['report']

        self.assertFalse(report.planned)
        self.assertFalse(report.date_planned)

    def test_update_planned_no_date_planned(self):
        self.client.login(username='manager@a.com', password='test')

        self.report.accepted_at = None
        self.report.save()

        url = reverse('report_planned_pro', args=[self.report.id])

        # Set as planned
        self.client.login(username='manager@a.com', password='test')
        response = self.client.get(url, follow=True)
        report = response.context['report']

        self.assertFalse(report.planned)
        self.assertFalse(report.date_planned)

    def test_update_planned_change(self):
        self.client.login(username='manager@a.com', password='test')

        first_date_planned = datetime.now()

        self.report.planned = True
        self.report.date_planned = first_date_planned
        self.report.save()

        date_planned = datetime.now() + timedelta(days=1)
        url = '%s?date_planned=%s' % (reverse('report_planned_pro', args=[self.report.id]), date_planned.strftime("%m/%Y"))

        # Set as planned
        self.client.login(username='manager@a.com', password='test')
        response = self.client.get(url, follow=True)
        report = response.context['report']

        self.assertTrue(report.planned)
        self.assertEqual(date_planned.strftime("%m/%Y"), report.date_planned.strftime("%m/%Y"))
        self.assertNotEqual(first_date_planned, report.date_planned)

    def test_update_planned_unauth(self):
        url = reverse('report_planned_pro', args=[self.report.id])

        # Set as planned without auth raise an error by accessing report in context
        response = self.client.get(url, follow=True)
        self.assertRaises(KeyError, lambda: response.context['report'])

    def test_update_priority(self):
        #Test default value of priority set to 1
        new_report = Report(
            status=Report.CREATED,
            secondary_category=self.secondary_category,
            category=self.category,
            description='Just a test',
            postalcode=1000,
            address='my address',
            point=dict_to_point({"x": '149776', "y": '170005'}),
            address_number='6h',
            created_by=self.manager
        )
        new_report.save()
        self.assertEquals(new_report.gravity, 0)
        self.assertEquals(new_report.probability, 0)
        self.assertEquals(new_report.get_priority(), 0)
        self.client.login(username='manager@a.com', password='test')

        #Test update report priority
        self.client.get(
            reverse("report_update_priority", args=[new_report.id]),
            {
                'gravity': '2',
                'probability': '4'
            })
        updated_report = Report.objects.get(id=new_report.id)
        self.assertEquals(updated_report.gravity, 2)
        self.assertEquals(updated_report.probability, 4)
        self.assertEquals(updated_report.get_priority(), 8)

    @skip("no more available")
    def test_previous_reports(self):
        self.client.login(username='manager@a.com', password='test')
        manager2 = FMSUser(
            telephone="0123456789",
            last_used_language="fr",
            password='test',
            first_name="manager2",
            last_name="manager2",
            email="manager2@a.com",
            manager=True
        )
        manager2.set_password('test')
        manager2.organisation = self.organisation
        manager2.save()
        managerId = "manager_%s" % (manager2.id)
        self.client.post(reverse("report_change_manager_pro", args=[self.report.id])+"?manId="+managerId)
        self.assertEquals(len(self.manager.previous_reports.all()), 1)
        self.assertEquals(self.manager.previous_reports.all()[0].id, self.report.id)
        self.assertEquals(len(self.manager.reports_in_charge.all()), 0)

    def test_update_visibility(self):
        #Test switch to public and back
        self.client.login(username='manager@a.com', password='test')
        self.client.get(
            reverse("report_change_switch_privacy", args=[self.report.id]),
            {"privacy": "true"})
        self.assertTrue(Report.objects.get(id=self.report.id).private)
        self.client.get(
            reverse("report_change_switch_privacy", args=[self.report.id]),
            {"privacy": "false"})
        self.assertFalse(self.report.private)

        #Test constraint: cannot turn report public if category is private

        #Turn report private
        self.client.get(reverse("report_change_switch_privacy", args=[self.report.id])+"?privacy=true")

        #Change category to private one
        report = Report.objects.get(id=self.report.id)
        report.secondary_category = ReportCategory.objects.get(id=4)
        report.save()
        #Try to set report to public
        self.client.get(reverse("report_change_switch_privacy", args=[self.report.id])+"?privacy=false")
        #Report not set to public because private category
        self.assertTrue(Report.objects.get(id=self.report.id).private)

    def test_false_address(self):
        self.client.login(username='manager@a.com', password='test')

        url = reverse("report_false_address", args=[self.report.id])
        post_data = {'false_address': 'This is a false address'}
        response = self.client.post(url, post_data, folow=True)

        report = Report.objects.get(id=self.report.id)
        self.assertContains(response, post_data['false_address'])
        self.assertEqual(report.false_address, post_data['false_address'])

        post_data = {'false_address': 'Another false address'}
        response = self.client.post(url, post_data, folow=True)

        report = Report.objects.get(id=self.report.id)
        self.assertContains(response, post_data['false_address'])
        self.assertEqual(report.false_address, post_data['false_address'])

