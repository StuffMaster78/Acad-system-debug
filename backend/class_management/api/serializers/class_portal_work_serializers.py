from __future__ import annotations

from rest_framework import serializers

from class_management.models import ClassPortalWorkLog


class ClassPortalWorkLogSerializer(serializers.ModelSerializer):
    writer_name = serializers.CharField(
        source="writer.get_full_name",
        read_only=True,
    )
    task_title = serializers.CharField(
        source="task.title",
        read_only=True,
    )
    activity_type_display = serializers.CharField(
        source="get_activity_type_display",
        read_only=True,
    )

    class Meta:
        model = ClassPortalWorkLog
        fields = [
            "id",
            "class_order",
            "task",
            "task_title",
            "writer",
            "writer_name",
            "activity_type",
            "activity_type_display",
            "title",
            "description",
            "portal_reference",
            "occurred_at",
            "logged_at",
            "visible_to_client",
            "verification_status",
            "verified_by",
            "verified_at",
            "verification_notes",
            "metadata",
        ]
        read_only_fields = [
            "class_order",
            "writer",
            "logged_at",
            "verification_status",
            "verified_by",
            "verified_at",
            "verification_notes",
            "metadata",
        ]


class CreateClassPortalWorkLogSerializer(serializers.Serializer):
    task_id = serializers.IntegerField(required=False, allow_null=True)
    activity_type = serializers.CharField(max_length=80)
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    portal_reference = serializers.CharField(required=False, allow_blank=True)
    occurred_at = serializers.DateTimeField()
    visible_to_client = serializers.BooleanField(default=True)
    post_to_thread = serializers.BooleanField(default=True)


class ReviewClassPortalWorkLogSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True)