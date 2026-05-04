from __future__ import annotations

from rest_framework import serializers

from class_management.models import (
    ClassScopeAssessment,
    ClassScopeItem,
    ClassTask,
)


class ClassScopeAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassScopeAssessment
        fields = "__all__"
        read_only_fields = [
            "class_order",
            "assessed_by",
            "assessed_at",
            "created_at",
            "updated_at",
        ]


class ClassScopeItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassScopeItem
        fields = "__all__"
        read_only_fields = [
            "class_order",
            "created_by",
            "created_at",
            "updated_at",
        ]


class CreateClassTaskSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    assigned_writer_id = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    due_at = serializers.DateTimeField(required=False, allow_null=True)

    client_visible_notes = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    writer_notes = serializers.CharField(required=False, allow_blank=True)
    admin_internal_notes = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    requires_portal_work = serializers.BooleanField(default=False)
    writer_may_upload_to_portal = serializers.BooleanField(default=True)
    writer_may_download_files = serializers.BooleanField(default=True)
    portal_submission_required = serializers.BooleanField(default=False)
    portal_submission_notes = serializers.CharField(
        required=False,
        allow_blank=True,
    )


class ClassTaskSerializer(serializers.ModelSerializer):
    assigned_writer_name = serializers.CharField(
        source="assigned_writer.get_full_name",
        read_only=True,
    )

    class Meta:
        model = ClassTask
        fields = "__all__"
        read_only_fields = [
            "class_order",
            "scope_item",
            "status",
            "started_at",
            "submitted_at",
            "completed_at",
            "portal_submitted_at",
            "created_by",
            "created_at",
            "updated_at",
        ]


class ClassTaskActionSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True)
    portal_submitted = serializers.BooleanField(required=False, default=False)