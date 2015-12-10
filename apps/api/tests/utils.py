# -*- coding: utf-8 -*-
# pylint: disable=C0103,W0201
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token


User = get_user_model()


class APIAuthTestCase(APITestCase):

    def setUp(self, *args, **kwargs):
        super(APIAuthTestCase, self).setUp(*args, **kwargs)
        self._init_auth()

    def _init_auth(self):
        self._user = User.objects.get_or_create(username="test@cirb.irisnet.be")[0]
        self._token = Token.objects.get_or_create(user=self._user)[0]
