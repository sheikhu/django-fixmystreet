# -*- coding: utf-8 -*-
# pylint: disable=E1103
from datetime import datetime

from django.core.urlresolvers import reverse

from ...tests.utils import APIAuthTestCase


class ReportAssignmentAcceptViewTestCase(APIAuthTestCase):

    def setUp(self, *args, **kwargs):
        super(ReportAssignmentAcceptViewTestCase, self).setUp(*args, **kwargs)
        self._url = reverse("api:reports:assignment_accept", args=[123])

    def test_normal(self):
        self._authenticate()
        payload = {
            "referenceId": "ABC/123",
            "comment": "Lorem ipsum dolor sit amet.",
            "createdAt": datetime.now().isoformat(),
        }
        response = self.client.post(self._url, payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.data)

    def test_wrong_payload(self):
        self._authenticate()
        payload = {
            # Missing mandatory "referenceId"
            "comment": "Lorem ipsum dolor sit amet.",
            "createdAt": datetime.now().isoformat(),
        }
        response = self.client.post(self._url, payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("reference_id", response.data)
        self.assertNotIn("comment", response.data)
        self.assertNotIn("created_at", response.data)

    def test_not_authenticated(self):
        response = self.client.post(self._url)
        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.data)
        self.assertTrue(response.data["detail"])

    def test_no_payload(self):
        self._authenticate()
        response = self.client.post(self._url)
        self.assertEqual(response.status_code, 400)
        self.assertIn("reference_id", response.data)
        self.assertIn("created_at", response.data)

    def _authenticate(self):
        self.client.force_authenticate(user=self._user)


class ReportAssignmentRejectViewTestCase(APIAuthTestCase):

    def setUp(self, *args, **kwargs):
        super(ReportAssignmentRejectViewTestCase, self).setUp(*args, **kwargs)
        self._url = reverse("api:reports:assignment_reject", args=[123])

    def test_normal(self):
        self._authenticate()
        payload = {
            "comment": "Lorem ipsum dolor sit amet.",
            "createdAt": datetime.now().isoformat(),
        }
        response = self.client.post(self._url, payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.data)

    def test_wrong_payload(self):
        self._authenticate()
        payload = {
            # Missing mandatory "comment"
            "createdAt": datetime.now().isoformat(),
        }
        response = self.client.post(self._url, payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("comment", response.data)
        self.assertNotIn("created_at", response.data)

    def test_not_authenticated(self):
        response = self.client.post(self._url)
        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.data)
        self.assertTrue(response.data["detail"])

    def test_no_payload(self):
        self._authenticate()
        response = self.client.post(self._url)
        self.assertEqual(response.status_code, 400)
        self.assertIn("comment", response.data)
        self.assertIn("created_at", response.data)

    def _authenticate(self):
        self.client.force_authenticate(user=self._user)


class ReportAssignmentCloseViewTestCase(APIAuthTestCase):

    def setUp(self, *args, **kwargs):
        super(ReportAssignmentCloseViewTestCase, self).setUp(*args, **kwargs)
        self._url = reverse("api:reports:assignment_close", args=[123])

    def test_normal(self):
        self._authenticate()
        payload = {
            "referenceId": "ABC/123",
            "comment": "Lorem ipsum dolor sit amet.",
            "createdAt": datetime.now().isoformat(),
        }
        response = self.client.post(self._url, payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.data)

    def test_wrong_payload(self):
        self._authenticate()
        payload = {
            # Missing mandatory "referenceId"
            "comment": "Lorem ipsum dolor sit amet.",
            "createdAt": datetime.now().isoformat(),
        }
        response = self.client.post(self._url, payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("reference_id", response.data)
        self.assertNotIn("comment", response.data)
        self.assertNotIn("created_at", response.data)

    def test_not_authenticated(self):
        response = self.client.post(self._url)
        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.data)
        self.assertTrue(response.data["detail"])

    def test_no_payload(self):
        self._authenticate()
        response = self.client.post(self._url)
        self.assertEqual(response.status_code, 400)
        self.assertIn("reference_id", response.data)
        self.assertIn("created_at", response.data)

    def _authenticate(self):
        self.client.force_authenticate(user=self._user)
