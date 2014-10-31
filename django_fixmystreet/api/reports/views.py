# -*- coding: utf-8 -*-
# pylint: disable=C0103,W0613,W0622
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from . import serializers
from ..views import FmsPrivateViewMixin


class AbstractReportAssignmentView(FmsPrivateViewMixin, APIView):

    def _get_bad_request(self, serializer):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReportAssignmentAcceptView(AbstractReportAssignmentView):

    def post(self, request, pk=None, format=None):
        serializer = serializers.ReportAssignmentAcceptSerializer(data=request.DATA)  # pylint: disable=C0103,E1120,E1123
        if serializer.is_valid():
            response_data = {
                "message": "Request successfully processed.",
            }
            return Response(response_data)

        return self._get_bad_request(serializer)


class ReportAssignmentRejectView(AbstractReportAssignmentView):

    def post(self, request, pk=None, format=None):
        serializer = serializers.ReportAssignmentRejectSerializer(data=request.DATA)  # pylint: disable=C0103,E1120,E1123
        if serializer.is_valid():
            response_data = {
                "message": "Request successfully processed.",
            }
            return Response(response_data)

        return self._get_bad_request(serializer)


class ReportAssignmentCloseView(AbstractReportAssignmentView):

    def post(self, request, pk=None, format=None):
        serializer = serializers.ReportAssignmentCloseSerializer(data=request.DATA)  # pylint: disable=C0103,E1120,E1123
        if serializer.is_valid():
            response_data = {
                "message": "Request successfully processed.",
            }
            return Response(response_data)

        return self._get_bad_request(serializer)
