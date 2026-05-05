from __future__ import annotations

from typing import Any
from typing import cast

from rest_framework import serializers

from communications.models.escalation import CommunicationEscalation
from communications.services.escalation_service import (
    CommunicationEscalationService,
)


class CommunicationEscalationSerializer(serializers.ModelSerializer):
    """
    Read serializer for thread escalations.
    """

    escalated_by_display = serializers.SerializerMethodField()
    resolved_by_display = serializers.SerializerMethodField()

    class Meta:
        model = CommunicationEscalation
        fields = [
            "id",
            "website",
            "thread",
            "status",
            "reason",
            "resolution_note",
            "escalated_by",
            "escalated_by_display",
            "resolved_by",
            "resolved_by_display",
            "escalated_at",
            "resolved_at",
            "metadata",
        ]
        read_only_fields = fields

    def get_escalated_by_display(
        self,
        obj: CommunicationEscalation,
    ) -> str:
        """
        Return escalation creator display label.
        """
        if obj.escalated_by is None:
            return ""

        return self._get_user_display(user=obj.escalated_by)

    def get_resolved_by_display(
        self,
        obj: CommunicationEscalation,
    ) -> str:
        """
        Return resolver display label.
        """
        if obj.resolved_by is None:
            return ""

        return self._get_user_display(user=obj.resolved_by)

    def _get_user_display(self, *, user) -> str:
        """
        Return safe user display label.
        """
        if hasattr(user, "get_full_name"):
            full_name = user.get_full_name()
            if full_name:
                return full_name

        return getattr(user, "email", str(user))


class CommunicationEscalationCreateSerializer(serializers.Serializer):
    """
    Create a thread escalation.
    """

    reason = serializers.CharField()
    metadata = serializers.DictField(required=False)

    def create(self, validated_data: dict[str, Any]) -> CommunicationEscalation:
        """
        Create escalation through service.
        """
        request = self.context["request"]
        thread = self.context["thread"]

        return CommunicationEscalationService.create(
            thread=thread,
            reason=validated_data["reason"],
            escalated_by=request.user,
            metadata=validated_data.get("metadata"),
        )


class CommunicationEscalationResolveSerializer(serializers.Serializer):
    """
    Resolve a thread escalation.
    """

    resolution_note = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    def save(self, **kwargs: Any) -> CommunicationEscalation:
        """
        Resolve escalation through service.
        """
        request = self.context["request"]
        escalation = self.context["escalation"]
        data = cast(dict[str, Any], self.validated_data)

        return CommunicationEscalationService.resolve(
            escalation=escalation,
            resolved_by=request.user,
            resolution_note=str(data.get("resolution_note", "")),
        )