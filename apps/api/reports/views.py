# -*- coding: utf-8 -*-
# pylint: disable=C0103,W0613,W0622
from rest_framework.views import APIView

from apps.fmsproxy.models import AssignmentHandler, \
    NotWaitingForThirdPartyError, NotAssignedToThirdPartyError, NotAuthorizedToThirdPartyError
from . import serializers
from ..views import FmsPrivateViewMixin


class AbstractReportAssignmentView(FmsPrivateViewMixin, APIView):

    def _get_assignment_handler(self, report_id, user):
        try:
            return AssignmentHandler(report_id, user)
        except (NotWaitingForThirdPartyError, NotAssignedToThirdPartyError, NotAuthorizedToThirdPartyError):
            return self._get_response_403()


class ReportAssignmentAcceptView(AbstractReportAssignmentView):

    def post(self, request, pk=None, format=None):
        serializer = serializers.ReportAssignmentAcceptSerializer(data=request.DATA)  # pylint: disable=E1120,E1123
        if not serializer.is_valid():
            return self._get_response_400(serializer.errors)

        assignment = self._get_assignment_handler(pk, request.user)
        assignment.accept(serializer.data)
        return self._get_response_200()


class ReportAssignmentRejectView(AbstractReportAssignmentView):

    def post(self, request, pk=None, format=None):
        serializer = serializers.ReportAssignmentRejectSerializer(data=request.DATA)  # pylint: disable=E1120,E1123
        if not serializer.is_valid():
            return self._get_response_400(serializer.errors)

        assignment = self._get_assignment_handler(pk, request.user)
        assignment.reject(serializer.data)
        return self._get_response_200()


class ReportAssignmentCloseView(AbstractReportAssignmentView):

    def post(self, request, pk=None, format=None):
        serializer = serializers.ReportAssignmentCloseSerializer(data=request.DATA)  # pylint: disable=E1120,E1123
        if not serializer.is_valid():
            return self._get_response_400(serializer.errors)

        assignment = self._get_assignment_handler(pk, request.user)
        assignment.close(serializer.data)
        return self._get_response_200()
