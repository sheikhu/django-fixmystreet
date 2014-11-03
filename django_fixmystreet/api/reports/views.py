# -*- coding: utf-8 -*-
# pylint: disable=C0103,W0613,W0622
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from django_fixmystreet.fmsproxy.models import AssignmentHandler, \
    NotWaitingForThirdPartyError, NotAssignedToThirdPartyError, NotAuthorizedToThirdPartyError
from . import serializers
from ..views import FmsPrivateViewMixin


class AbstractReportAssignmentView(FmsPrivateViewMixin, APIView):

    def _get_assignment_handler(self, report_id, user):
        try:
            return AssignmentHandler(report_id, user)
        except (NotWaitingForThirdPartyError, NotAssignedToThirdPartyError, NotAuthorizedToThirdPartyError):
            return self._get_response_403()

    def _get_response_200(self, context=None):
        if not context:
            context = {"message": "Request successfully processed."}
        return Response(context)

    def _get_response_400(self, errors):
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    def _get_response_403(self, context=None):
        if not context:
            context = {"detail": "Access or action forbidden."}
        return Response(context, status=status.HTTP_403_FORBIDDEN)


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
