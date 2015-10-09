from django.test.client import Client
from django.core.urlresolvers import reverse

from apps.fixmystreet.models import FMSUser, OrganisationEntity, Report, ReportComment, ReportCategory, UserOrganisationMembership, GroupMailConfig
from apps.fixmystreet.tests import FMSTestCase
from apps.fixmystreet.utils import dict_to_point


class ExportPDFTest(FMSTestCase):

    def setUp(self):
        self.bxl = OrganisationEntity.objects.get(id=4)
        self.manager_bxl = FMSUser(
            is_active=True,
            email="manager@bxl.be",
            telephone="0123456789",
            last_used_language="fr",
            manager=True,
            organisation=self.bxl)
        self.manager_bxl.set_password('test')
        self.manager_bxl.save()

        self.group = OrganisationEntity(
            type="D",
            name_nl="Werken",
            name_fr="Travaux",
            phone="090987",
            dependency=self.bxl,
            email="test@email.com"
            )
        self.group.save()

        self.group_mail_config       = GroupMailConfig()
        self.group_mail_config.group = self.group
        self.group_mail_config.save()

        self.usergroupmembership = UserOrganisationMembership(user_id=self.manager_bxl.id, organisation_id=self.group.id, contact_user=True)
        self.usergroupmembership.save()
        self.citizen = FMSUser(email="citizen@fms.be", telephone="0123456789", last_used_language="fr")
        self.citizen.save()

        self.secondary_category = ReportCategory.objects.all()[0]
        self.category = self.secondary_category.category_class

        self.client.login(username=self.manager_bxl.email, password='test')
        self.report = Report(
            status=Report.CREATED,
            secondary_category=self.secondary_category,
            category=self.category,
            description='Just a test',
            postalcode=1000,
            address='my address',
            point=dict_to_point({"x": '149776', "y": '170005'}),
            address_number='6h',
            created_by=self.manager_bxl
        )
        self.report.save()

        self.report.attachments.add(ReportComment(
            text='test comment 1',
            security_level=ReportComment.PRIVATE
        ))

        self.client.logout()

        self.report.attachments.add(ReportComment(
            text='test comment 2',
            security_level=ReportComment.PUBLIC
        ))
        self.report.attachments.add(ReportComment(
            text='test comment 3',
            logical_deleted=True,
            security_level=ReportComment.PUBLIC
        ))

        self.client = Client()

    def test_pdf_attachment(self):
        response = self.client.get(reverse('report_pdf', args=[self.report.id]) + '?output=html', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('comments', response.context)

        self.assertEqual(len(response.context['comments']), 1)
        self.assertEqual(response.context['comments'][0].text, 'test comment 2')
        self.assertEqual(response.context['visibility'], 'public')

    def test_attachment_private(self):
        self.assertTrue(self.client.login(username=self.manager_bxl.email, password='test'))

        response = self.client.get(reverse('report_pdf_pro', args=[self.report.id]) + '?output=html', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(hasattr(response.context['request'], 'fmsuser'))
        self.assertIn('comments', response.context)

        self.assertEqual(len(response.context['comments']), 2)
        self.assertEqual(response.context['comments'][0].text, 'test comment 1')
        self.assertEqual(response.context['comments'][1].text, 'test comment 2')
        self.assertEqual(response.context['visibility'], 'private')

    def test_show_attachment(self):
        response = self.client.get(reverse('report_show', kwargs={'report_id': self.report.id, 'slug': ''}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'test comment 1')
        self.assertContains(response, 'test comment 2')
        self.assertNotContains(response, 'test comment 3')

    def test_show_attachment_private(self):
        self.assertTrue(self.client.login(username=self.manager_bxl.email, password='test'))

        response = self.client.get(reverse('report_show_pro', kwargs={'report_id': self.report.id, 'slug': ''}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test comment 1')
        self.assertContains(response, 'test comment 2')
        self.assertNotContains(response, 'test comment 3')



