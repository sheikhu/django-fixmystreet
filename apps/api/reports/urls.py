# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0330
from django.conf.urls import url, patterns

from rest_framework.urlpatterns import format_suffix_patterns

from . import views


urlpatterns = format_suffix_patterns(patterns("",
    url(r"^(?P<pk>[0-9]+)/assignment/accept$", views.ReportAssignmentAcceptView.as_view(), name="assignment_accept"),
    url(r"^(?P<pk>[0-9]+)/assignment/reject$", views.ReportAssignmentRejectView.as_view(), name="assignment_reject"),
    url(r"^(?P<pk>[0-9]+)/assignment/close$", views.ReportAssignmentCloseView.as_view(), name="assignment_close"),
))
