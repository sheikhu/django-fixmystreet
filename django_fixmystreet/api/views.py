# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class PublicApiView(APIView):

    def _get_response_200(self, context=None):
        context = context or {}
        if "detail" not in context:
            context["detail"] = u"Request successfully processed."
        return Response(context)

    def _get_response_400(self, errors, context=None):
        context = context or {}
        if "detail" not in context:
            context["detail"] = u"Request is malformed."
        context["errors"] = errors
        return Response(context, status=status.HTTP_400_BAD_REQUEST)

    def _get_response_403(self, context=None):
        context = context or {}
        if "detail" not in context:
            context["detail"] = u"Access or action forbidden."
        return Response(context, status=status.HTTP_403_FORBIDDEN)


class PrivateApiView(PublicApiView):

    permission_classes = (IsAuthenticated,)
