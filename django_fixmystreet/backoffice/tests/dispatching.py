from django.test import TestCase
from django.test.client import Client
from django.contrib.gis.geos import Polygon

from django_fixmystreet.fixmystreet.models import (
    Report, ReportCategory, OrganisationEntity, FMSUser,
    UserOrganisationMembership, OrganisationEntitySurface
)
from django_fixmystreet.fixmystreet.utils import dict_to_point

from datetime import datetime


class DispatchingTest(TestCase):

    fixtures = ["bootstrap", "list_items"]

    def setUp(self):
        self.client = Client()

        self.secondary_category = ReportCategory.objects.all()[0]
        self.category = self.secondary_category.category_class

        self.organisation = OrganisationEntity.objects.get(pk=4)
        self.department = OrganisationEntity(
            type="D",
            name_nl="Werken",
            name_fr="Travaux",
            phone="090987",
            dependency=self.organisation,
            email="test@email.com"
        )
        self.department.save()

        p1 = (148776, 171005)
        p2 = (150776, 171005)
        p3 = (150776, 169005)
        p4 = (148776, 169005)

        surface = OrganisationEntitySurface(
            geom=Polygon([p1, p2, p3, p4, p1]),
            owner=self.organisation,
        )
        surface.save()

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
        self.manager.organisation = self.organisation
        self.manager.save()
        self.department.dispatch_categories.add(self.secondary_category)

        self.usergroupmembership = UserOrganisationMembership(user=self.manager, organisation=self.department, contact_user=True)
        self.usergroupmembership.save()

        self.applicant_group = OrganisationEntity(
            type="A",
            name_nl="Belgacom",
            name_fr="Belgacom",
            phone="090987",
            email="test@belgacom.com"
        )
        self.applicant_group.save()

        self.applicant = FMSUser(
            is_active=True,
            telephone="0123456789",
            last_used_language="fr",
            password='test',
            first_name="manager",
            last_name="manager",
            email="applicant@a.com",
            manager=True
        )
        self.applicant.set_password('test')
        self.applicant.save()

        self.applicantmembership = UserOrganisationMembership(user=self.applicant, organisation=self.applicant_group, contact_user=True)
        self.applicantmembership.save()

    def test_dispatch_pro(self):
        """
        when a report is created by a agent / manager / entity
        responsible entity is computed based on responsible entity from creator
        """
        self.client.login(username='manager@a.com', password='test')
        self.report = Report(
            status=Report.CREATED,
            secondary_category=self.secondary_category,
            category=self.category,
            description='Just a test',
            postalcode=1090,
            address='my address',
            point=dict_to_point({"x": '149776', "y": '170005'}),
            address_number='6h',
            created_by=self.manager,
            accepted_at=datetime.now()
        )
        self.report.save()
        self.assertEquals(self.report.responsible_entity, self.organisation)
        self.assertEquals(self.report.responsible_department, self.department)

    def test_dispatch_applicant(self):
        """
        when a report is created by a applicant / contractor
        responsible entity is computed based on geography
        """
        self.client.login(username='applicant@a.com', password='test')
        self.report = Report(
            status=Report.CREATED,
            secondary_category=self.secondary_category,
            category=self.category,
            description='Just a test',
            postalcode=1000,
            address='my address',
            point=dict_to_point({"x": '149776', "y": '170005'}),
            address_number='6h',
            created_by=self.applicant,
            accepted_at=datetime.now()
        )
        self.report.save()
        self.assertEquals(self.report.responsible_entity, self.organisation)
        self.assertEquals(self.report.responsible_department, self.department)

    def test_dispatch_citizen(self):
        self.report = Report(
            status=Report.CREATED,
            secondary_category=self.secondary_category,
            category=self.category,
            description='Just a test',
            postalcode=1000,
            address='my address',
            point=dict_to_point({"x": '149776', "y": '170005'}),
            address_number='6h',
            accepted_at=datetime.now()
        )
        self.report.save()
        self.assertEquals(self.report.responsible_entity, self.organisation)
        self.assertEquals(self.report.responsible_department, self.department)
