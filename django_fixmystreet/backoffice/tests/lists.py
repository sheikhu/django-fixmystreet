from django.test import TestCase
from django.contrib.auth.models import User

from django_fixmystreet.fixmystreet.models import Report, ReportCategory, ReportMainCategoryClass, OrganisationEntity, FMSUser, ReportFile
from django_fixmystreet.fixmystreet.utils import dict_to_point

class ListTest(TestCase):

    fixtures = ["bootstrap", "list_items"]

    def setUp(self):
        self.secondary_category = ReportCategory.objects.all()[0]
        self.category = self.secondary_category.category_class

        self.bxl = OrganisationEntity.objects.get(id=4) # postal code = 1000 Bxl
        self.bxl.save()

        self.agent = FMSUser(email="agent@bxl.be", telephone="0123456789", last_used_language="fr", agent=True, organisation=self.bxl)
        self.agent.save()

        self.contractor = FMSUser(email="contractor@bxl.be", telephone="0123456789", last_used_language="fr", contractor=True, organisation=self.bxl)
        self.contractor.save()
        self.contractor.work_for.add(self.bxl)

        self.manager = FMSUser(email="manager@bxl.be", telephone="0123456789", last_used_language="fr", manager=True, organisation=self.bxl)
        self.manager.save()

        self.citizen = FMSUser(email="citizen@fms.be", telephone="0123456789", last_used_language="fr")
        self.citizen.save()

    def test_list_agent_reports(self):
        new_report = Report(
            status=Report.CREATED,
            secondary_category=self.secondary_category,
            category=self.category,
            description='Just a test',
            postalcode = 1000,
            address='my address',
            point=dict_to_point({"x":'149776', "y":'170005'}),
            address_number='6h',
            citizen=self.citizen
        )
        new_report.save()

        reports = Report.objects.all()

        # Agent has no report
        self.assertFalse(reports.responsible(self.agent))

    def test_list_contractor_reports(self):
        new_report = Report(
            status=Report.CREATED,
            secondary_category=self.secondary_category,
            category=self.category,
            description='Just a test',
            postalcode = 1000,
            address='my address',
            point=dict_to_point({"x":'149776', "y":'170005'}),
            address_number='6h',
            citizen=self.citizen
        )
        new_report.contractor = self.bxl
        new_report.save()

        reports = Report.objects.all()

        # Contractor has reports
        self.assertTrue(reports.entity_responsible(self.contractor))
