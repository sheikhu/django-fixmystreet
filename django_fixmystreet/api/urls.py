# -*- coding: utf-8 -*-
# pylint: disable=C0330
from django.conf.urls import url, patterns, include


urlpatterns = patterns("",
    url(r"^reports/", include("django_fixmystreet.api.reports.urls", namespace="reports"))
)
