# -*- coding: utf-8 -*-
from rest_framework.permissions import IsAuthenticated


class FmsPrivateViewMixin(object):

    permission_classes = (IsAuthenticated,)
