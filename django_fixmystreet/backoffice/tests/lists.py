from django.test import TestCase
from django.contrib.auth.models import User

from django_fixmystreet.fixmystreet.models import Report, ReportCategory, ReportMainCategoryClass, OrganisationEntity, FMSUser, ReportFile, UserOrganisationMembership
from django_fixmystreet.fixmystreet.utils import dict_to_point

class ListTest(TestCase):

    fixtures = ["bootstrap", "list_items"]

    def setUp(self):
        self.secondary_category = ReportCategory.objects.all()[0]
        self.category = self.secondary_category.category_class

        self.bxl = OrganisationEntity.objects.get(id=4) # postal code = 1000 Bxl
        self.bxl.save()

        self.group = OrganisationEntity(
            type="D",
            name_nl="Werken",
            name_fr="Travaux",
            phone="090987",
            dependency = self.bxl,
            email="test@email.com"
            )
        self.group.save()

        self.agent = FMSUser(email="agent@bxl.be", telephone="0123456789", last_used_language="fr", agent=True, organisation=self.bxl)
        self.agent.save()
        
        self.stib = OrganisationEntity.objects.get(id=21)
        self.stib.dependency = self.bxl
        self.stib.save()
        
        self.contractor = FMSUser(email="contractor@bxl.be", telephone="0123456789", last_used_language="fr", contractor=True, organisation=self.stib)
        self.contractor.save()
        
        self.contractor_manager = FMSUser(email="conman@bxl.be",telephone="90870870",last_used_language="fr",contractor=True,organisation=self.stib,manager=True)
        self.contractor_manager.save()
        uom = UserOrganisationMembership(user=self.contractor_manager, organisation=self.group)
        uom.save()
        
        self.entity_manager = FMSUser(email="entman@bxl.be",telephone="90870870",last_used_language="fr",leader=True,organisation=self.group,manager=True)
        self.entity_manager.save()
        self.usergroupmembership = UserOrganisationMembership(user_id = self.entity_manager.id, organisation_id = self.group.id)
        self.usergroupmembership.save()

        self.manager = FMSUser(email="manager@bxl.be", telephone="0123456789", last_used_language="fr", manager=True, organisation=self.bxl)
        self.manager.save()
        self.usergroupmembership2 = UserOrganisationMembership(user_id = self.manager.id, organisation_id = self.group.id)
        self.usergroupmembership2.save()

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

    def test_list_contractor_manager_reports(self):
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

        new_report.contractor = self.stib
        new_report.responsible_manager = self.manager
        new_report.responsible_department = self.group
        new_report.save()
        
        new_report2 = Report(
            status=Report.CREATED,
            secondary_category=self.secondary_category,
            category=self.category,
            description='Just a test',
            postalcode = 1000,
            address='my address',
            point=dict_to_point({"x":'149776', "y":'170005.2'}),
            address_number='6',
            citizen=self.citizen
        )
        new_report2.responsible_manager = self.contractor_manager
        new_report2.responsible_department = self.group
        new_report2.save()

        reports = Report.objects.all()
        # Entity of contractor has 2 reports
        self.assertEquals(2,len(reports.entity_responsible(self.contractor_manager)))
        #contractor is responsible for 2 reports (1 as manager, 1 as contractor)
        self.assertEquals(2,len(reports.responsible(self.contractor_manager)))

    def test_list_entity_manager_reports(self):
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
        new_report.responsible_manager = self.manager
        new_report.responsible_department = self.group
        new_report.save()

        reports = Report.objects.all()
        self.assertEquals(1,len(reports.entity_responsible(self.entity_manager)))
        self.assertEquals(1,len(reports.responsible(self.entity_manager)))

        new_report.responsible_manager = self.entity_manager
        new_report.responsible_department = self.group
        new_report.save()

        reports = Report.objects.all()
        self.assertEquals(1,len(reports.responsible(self.entity_manager)))