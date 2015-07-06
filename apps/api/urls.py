# -*- coding: utf-8 -*-
# pylint: disable=C0330
from django.conf.urls import url, patterns, include

from .hooks.views import HooksView


urlpatterns = patterns("",
    url(r"^hooks$", HooksView.as_view(), name="hooks"),
)
