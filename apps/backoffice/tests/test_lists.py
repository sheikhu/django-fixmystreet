from django.contrib.gis.geos import Polygon

from apps.fixmystreet.models import (
    Report, ReportCategory, ReportMainCategoryClass, OrganisationEntity,
    FMSUser, ReportFile, UserOrganisationMembership,
    OrganisationEntitySurface, GroupMailConfig
)
from apps.fixmystreet.tests import FMSTestCase
from apps.fixmystreet.utils import dict_to_point


class ListTest(FMSTestCase):

    def setUp(self):
        self.secondary_category = ReportCategory.objects.all()[0]
        self.category = self.secondary_category.category_class

        self.bxl = OrganisationEntity.objects.get(id=4)  # postal code = 1000 Bxl
        self.bxl.save()

        p1 = (148776, 171005)
        p2 = (150776, 171005)
        p3 = (150776, 169005)
        p4 = (148776, 169005)

        surface = OrganisationEntitySurface(
            geom=Polygon([p1, p2, p3, p4, p1]),
            owner=self.bxl,
        )
        surface.save()

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

        self.agent = FMSUser(
            is_active=True,
            email="agent@bxl.be",
            telephone="0123456789",
            last_used_language="fr",
            agent=True,
            organisation=self.bxl)
        self.agent.save()

        self.stib = OrganisationEntity.objects.get(id=21)
        self.stib.dependency = self.bxl
        self.stib.save()

        self.contractor = FMSUser(
            is_active=True,
            email="contractor@bxl.be",
            telephone="0123456789",
            last_used_language="fr",
            contractor=True,
            organisation=self.bxl)
        self.contractor.save()

        self.contractor_manager = FMSUser(
            is_active=True,
            email="conman@bxl.be",
            telephone="90870870",
            last_used_language="fr",
            contractor=True,
            organisation=self.bxl,
            manager=True
        )
        self.contractor_manager.save()
        uom = UserOrganisationMembership(user=self.contractor_manager, organisation=self.group)
        uom.save()

        self.entity_manager = FMSUser(
            is_active=True,
            email="entman@bxl.be",
            telephone="90870870",
            last_used_language="fr",
            leader=True,
            organisation=self.bxl,
            manager=True
        )
        self.entity_manager.save()
        self.usergroupmembership = UserOrganisationMembership(user_id = self.entity_manager.id, organisation_id = self.group.id)
        self.usergroupmembership.save()

        self.manager = FMSUser(
            is_active=True,
            email="manager@bxl.be",
            telephone="0123456789",
            last_used_language="fr",
            manager=True,
            organisation=self.bxl
        )
        self.manager.save()
        self.usergroupmembership2 = UserOrganisationMembership(user_id = self.manager.id, organisation_id = self.group.id, contact_user = True)
        self.usergroupmembership2.save()

        self.citizen = FMSUser(
            email="citizen@fms.be",
            telephone="0123456789",
            last_used_language="fr"
        )
        self.citizen.save()

    def test_list_agent_reports(self):
        new_report = Report(
            status=Report.CREATED,
            secondary_category=self.secondary_category,
            category=self.category,
            description='Just a test',
            postalcode=1000,
            address='my address',
            point=dict_to_point({"x": '149776', "y": '170005'}),
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
            postalcode=1000,
            address='my address',
            point=dict_to_point({"x": '149776', "y": '170005'}),
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
            postalcode=1000,
            address='my address',
            point=dict_to_point({"x": '149776', "y": '170005'}),
            address_number='6h',
            citizen=self.citizen
        )

        new_report.contractor = self.stib
        new_report.responsible_department = self.group
        new_report.save()

        new_report2 = Report(
            status=Report.CREATED,
            secondary_category=self.secondary_category,
            category=self.category,
            description='Just a test',
            postalcode=1000,
            address='my address',
            point=dict_to_point({"x": '149776', "y": '170005.2'}),
            address_number='6',
            citizen=self.citizen
        )
        new_report2.responsible_department = self.group
        new_report2.save()

        reports = Report.objects.all()
        # Entity of contractor has 2 reports
        self.assertEquals(2, len(reports.entity_responsible(self.contractor_manager)))
        #contractor is responsible for 2 reports (1 as manager, 1 as contractor)
        self.assertEquals(2, len(reports.responsible(self.contractor_manager)))

    def test_list_entity_manager_reports(self):
        new_report = Report(
            status=Report.CREATED,
            secondary_category=self.secondary_category,
            category=self.category,
            description='Just a test',
            postalcode=1000,
            address='my address',
            point=dict_to_point({"x": '149776', "y": '170005'}),
            address_number='6h',
            citizen=self.citizen
        )
        new_report.responsible_department = self.group
        new_report.save()

        reports = Report.objects.all()
        self.assertEquals(1, len(reports.entity_responsible(self.entity_manager)))
        self.assertEquals(1, len(reports.responsible(self.entity_manager)))

        new_report.responsible_department = self.group
        new_report.save()

        reports = Report.objects.all()
        self.assertEquals(1, len(reports.responsible(self.entity_manager)))
