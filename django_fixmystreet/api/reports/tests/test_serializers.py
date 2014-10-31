# -*- coding: utf-8 -*-
# pylint: disable=E1103
from copy import deepcopy
from datetime import datetime

from django.test import TestCase

from .. import serializers


class AbstractSerializerTestCase(TestCase):

    def _common_assert(self, serializer, expected_data):
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.data, expected_data)

    def _common_assert_fail(self, serializer, expected_data):
        self.assertFalse(serializer.is_valid())
        self.assertNotEqual(serializer.data, expected_data)


class AbstractReportAssignmentSerializerTestCase(AbstractSerializerTestCase):

    def _get_default_data(self):
        return {
            "reference_id": "ABC/123",
            "comment": "Lorem ipsum dolor sit amet.",
            "created_at": datetime.now(),
        }

    def _get_default_expected_data(self, data):
        expected_data = deepcopy(data)
        expected_data["created_at"] = expected_data["created_at"].isoformat()
        return expected_data


class ReportAssignmentAcceptSerializerTestCase(AbstractReportAssignmentSerializerTestCase):

    def test_normal(self):
        data = self._get_default_data()
        expected_data = self._get_default_expected_data(data)

        serializer = serializers.ReportAssignmentAcceptSerializer(data=data)  # pylint: disable=C0103,E1120,E1123
        self._common_assert(serializer, expected_data)

    def test_extra_field(self):
        data = self._get_default_data()
        expected_data = self._get_default_expected_data(data)
        data["extra_field"] = 123

        serializer = serializers.ReportAssignmentAcceptSerializer(data=data)  # pylint: disable=C0103,E1120,E1123
        self._common_assert(serializer, expected_data)

    def test_missing_field(self):
        data = self._get_default_data()
        expected_data = self._get_default_expected_data(data)
        data.pop("reference_id", None)

        serializer = serializers.ReportAssignmentAcceptSerializer(data=data)  # pylint: disable=C0103,E1120,E1123
        self._common_assert_fail(serializer, expected_data)


class ReportAssignmentRejectSerializerTestCase(AbstractReportAssignmentSerializerTestCase):

    def test_normal(self):
        data = self._get_default_data()
        expected_data = self._get_default_expected_data(data)

        serializer = serializers.ReportAssignmentRejectSerializer(data=data)  # pylint: disable=C0103,E1120,E1123
        self._common_assert(serializer, expected_data)

    def test_extra_field(self):
        data = self._get_default_data()
        expected_data = self._get_default_expected_data(data)
        data["extra_field"] = 123

        serializer = serializers.ReportAssignmentRejectSerializer(data=data)  # pylint: disable=C0103,E1120,E1123
        self._common_assert(serializer, expected_data)

    def test_missing_field(self):
        data = self._get_default_data()
        expected_data = self._get_default_expected_data(data)
        data.pop("comment", None)

        serializer = serializers.ReportAssignmentAcceptSerializer(data=data)  # pylint: disable=C0103,E1120,E1123
        self._common_assert_fail(serializer, expected_data)

    def _get_default_data(self):
        data = super(ReportAssignmentRejectSerializerTestCase, self)._get_default_data()
        data.pop("reference_id", None)
        return data


class ReportAssignmentCloseSerializerTestCase(AbstractReportAssignmentSerializerTestCase):

    def test_normal(self):
        data = self._get_default_data()
        expected_data = self._get_default_expected_data(data)

        serializer = serializers.ReportAssignmentCloseSerializer(data=data)  # pylint: disable=C0103,E1120,E1123
        self._common_assert(serializer, expected_data)

    def test_extra_field(self):
        data = self._get_default_data()
        expected_data = self._get_default_expected_data(data)
        data["extra_field"] = 123

        serializer = serializers.ReportAssignmentCloseSerializer(data=data)  # pylint: disable=C0103,E1120,E1123
        self._common_assert(serializer, expected_data)

    def test_missing_field(self):
        data = self._get_default_data()
        expected_data = self._get_default_expected_data(data)
        data.pop("reference_id", None)

        serializer = serializers.ReportAssignmentAcceptSerializer(data=data)  # pylint: disable=C0103,E1120,E1123
        self._common_assert_fail(serializer, expected_data)
