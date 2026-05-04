from __future__ import annotations

from rest_framework import serializers

from class_management.models import ClassAssignment


class ClassAssignmentSerializer(serializers.ModelSerializer):
    writer_name = serializers.CharField(
        source="writer.get_full_name",
        read_only=True,
    )
    assigned_by_name = serializers.CharField(
        source="assigned_by.get_full_name",
        read_only=True,
    )

    class Meta:
        model = ClassAssignment
        fields = "__all__"
        read_only_fields = [
            "status",
            "assigned_by",
            "assigned_at",
            "removed_at",
        ]


class AssignWriterSerializer(serializers.Serializer):
    writer_id = serializers.IntegerField()
    assignment_notes = serializers.CharField(required=False, allow_blank=True)
    writer_visible_notes = serializers.CharField(
        required=False,
        allow_blank=True,
    )


class ReassignWriterSerializer(serializers.Serializer):
    writer_id = serializers.IntegerField()
    reason = serializers.CharField()
    assignment_notes = serializers.CharField(required=False, allow_blank=True)


class RemoveWriterSerializer(serializers.Serializer):
    reason = serializers.CharField()