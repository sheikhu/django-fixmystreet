from django.contrib.gis.geos import Polygon

from django_fixmystreet.fixmystreet.models import (
    OrganisationEntity, StreetSurface, GroupMailConfig,
    OrganisationEntitySurface, ReportCategory, Report
)
from django_fixmystreet.fixmystreet.tests import FMSTestCase
from django_fixmystreet.fixmystreet.utils import dict_to_point


class GeographicDispatchingTest(FMSTestCase):

    def setUp(self):
        '''
        Create organisations and surfaces
        '''

        self.secondary_category = ReportCategory.objects.all()[0]
        self.category = self.secondary_category.category_class

        self.region = OrganisationEntity(
            type=OrganisationEntity.REGION,
            name_nl="Region",
            name_fr="Region"
        )
        self.region.save()
        self.region_group = OrganisationEntity(
            type=OrganisationEntity.DEPARTMENT,
            name_nl="Werken",
            name_fr="Travaux",
            phone="090987",
            dependency=self.region,
            email="test@email.com"
        )
        self.region_group.save()

        self.region_group_mail_config       = GroupMailConfig()
        self.region_group_mail_config.group = self.region_group
        self.region_group_mail_config.save()

        self.commune = OrganisationEntity(
            name_nl="Commune",
            name_fr="Commune",
        )
        self.commune.save()
        self.commune_group = OrganisationEntity(
            type=OrganisationEntity.DEPARTMENT,
            name_nl="Werken",
            name_fr="Travaux",
            phone="090987",
            dependency=self.commune,
            email="test@email.com"
        )
        self.commune_group.save()
        self.commune_group.dispatch_categories.add(self.secondary_category)

        self.commune_group_mail_config       = GroupMailConfig()
        self.commune_group_mail_config.group = self.commune_group
        self.commune_group_mail_config.save()

        p1 = (148776, 171005)
        p2 = (150776, 171005)
        p3 = (150776, 169005)
        p4 = (148776, 169005)

        self.surface = OrganisationEntitySurface(
            geom=Polygon([p1, p2, p3, p4, p1]),
            owner=self.commune,
        )
        self.surface.save()

        p1 = (149756, 169985)
        p2 = (149796, 169985)
        p3 = (149796, 170025)
        p4 = (149756, 170025)

        self.street_surface = StreetSurface(
            geom=Polygon([p1, p2, p3, p4, p1]),
            administrator=StreetSurface.REGION,
        )
        self.street_surface.save()

    def test_entity_surface_owner_is_responsible(self):
        report = Report(
            point=dict_to_point({"x": '149776', "y": '170005'}),
            postalcode=1000,
            address='my address',
            address_number='6h',
            secondary_category=self.secondary_category,
            category=self.category,
        )
        report.save()

        self.assertEqual(report.responsible_entity, self.commune)

    def test_regional_road_is_detected(self):
        report = Report(
            point=dict_to_point({"x": '149776', "y": '170005'}),
            postalcode=1000,
            address='my address',
            address_number='1',
            secondary_category=self.secondary_category,
            category=self.category,
        )
        report.save()

        self.assertTrue(report.address_regional)

        report = Report(
            point=dict_to_point({"x": '149776', "y": '170805'}),
            postalcode=1000,
            address='my address',
            address_number='1',
            secondary_category=self.secondary_category,
            category=self.category,
        )
        report.save()

        self.assertFalse(report.address_regional)


    def test_regional_road_is_detected_on_border(self):
        report = Report(
            # this point is outside the polygon of 1m
            point=dict_to_point({"x": '149776', "y": '170026'}),
            postalcode=1000,
            address='my address',
            address_number='1',
            secondary_category=self.secondary_category,
            category=self.category,
        )
        report.save()

        self.assertTrue(report.address_regional)


    def test_entity_surface_raise_exception_when_outside(self):
        report = Report(
            point=dict_to_point({"x": '0', "y": '0'}),
            postalcode=1000,
            address='my address',
            address_number='6h',
            secondary_category=self.secondary_category,
            category=self.category,
        )
        with self.assertRaises(Exception):
            report.save()
