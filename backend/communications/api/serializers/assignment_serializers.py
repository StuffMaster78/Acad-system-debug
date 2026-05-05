from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers

from communications.models.assignment import CommunicationThreadAssignment
from communications.services.assignment_service import (
    CommunicationThreadAssignmentService,
)


class CommunicationThreadAssignmentSerializer(serializers.ModelSerializer):
    """
    Read serializer for thread assignments.
    """

    assigned_to_display = serializers.SerializerMethodField()
    assigned_by_display = serializers.SerializerMethodField()

    class Meta:
        model = CommunicationThreadAssignment
        fields = [
            "id",
            "website",
            "thread",
            "assigned_to",
            "assigned_to_display",
            "assigned_by",
            "assigned_by_display",
            "is_active",
            "assigned_at",
            "unassigned_at",
            "metadata",
        ]
        read_only_fields = fields

    def get_assigned_to_display(
        self,
        obj: CommunicationThreadAssignment,
    ) -> str:
        """
        Return assigned user display label.
        """
        return self._get_user_display(user=obj.assigned_to)

    def get_assigned_by_display(
        self,
        obj: CommunicationThreadAssignment,
    ) -> str:
        """
        Return assigning user display label.
        """
        if obj.assigned_by is None:
            return ""

        return self._get_user_display(user=obj.assigned_by)

    def _get_user_display(self, *, user) -> str:
        """
        Return safe user display label.
        """
        if hasattr(user, "get_full_name"):
            full_name = user.get_full_name()
            if full_name:
                return full_name

        return getattr(user, "email", str(user))


class CommunicationThreadAssignmentCreateSerializer(serializers.Serializer):
    """
    Assign a thread to a staff user.
    """

    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(),
    )

    def create(
        self,
        validated_data: dict[str, Any],
    ) -> CommunicationThreadAssignment:
        """
        Create assignment through service.
        """
        request = self.context["request"]
        thread = self.context["thread"]

        return CommunicationThreadAssignmentService.assign(
            thread=thread,
            assigned_to=validated_data["assigned_to"],
            assigned_by=request.user,
        )