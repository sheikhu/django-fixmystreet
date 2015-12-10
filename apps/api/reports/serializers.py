# -*- coding: utf-8 -*-
from rest_framework import serializers

from . import models


class ReportAssignmentAcceptSerializer(serializers.Serializer):

    reference_id = serializers.CharField()
    comment = serializers.CharField(required=False)
    created_at = serializers.DateTimeField()

    def restore_object(self, attrs, instance=None):
        # Update existing instance.
        if instance:
            instance.reference_id = attrs.get("reference_id", instance.reference_id)
            instance.comment = attrs.get("comment", instance.comment)
            instance.created_at = attrs.get("created_at", instance.created_at)
            return instance

        # Create new instance.
        return models.ReportAssignmentAccept(**attrs)


class ReportAssignmentRejectSerializer(serializers.Serializer):

    comment = serializers.CharField()
    created_at = serializers.DateTimeField()

    def restore_object(self, attrs, instance=None):
        # Update existing instance.
        if instance:
            instance.comment = attrs.get("comment", instance.comment)
            instance.created_at = attrs.get("created_at", instance.created_at)
            return instance

        # Create new instance.
        return models.ReportAssignmentReject(**attrs)


class ReportAssignmentCloseSerializer(serializers.Serializer):

    reference_id = serializers.CharField()
    comment = serializers.CharField(required=False)
    created_at = serializers.DateTimeField()

    def restore_object(self, attrs, instance=None):
        # Update existing instance.
        if instance:
            instance.reference_id = attrs.get("reference_id", instance.reference_id)
            instance.comment = attrs.get("comment", instance.comment)
            instance.created_at = attrs.get("created_at", instance.created_at)
            return instance

        # Create new instance.
        return models.ReportAssignmentClose(**attrs)
