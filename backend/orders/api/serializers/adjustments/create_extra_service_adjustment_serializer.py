from __future__ import annotations

from rest_framework import serializers


class CreateExtraServiceAdjustmentSerializer(serializers.Serializer):
    """
    Validate extra service adjustment creation.
    """

    extra_service_code = serializers.CharField(max_length=100)
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )
    writer_justification = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )
    client_visible_note = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )
    milestones = serializers.CharField(
        child=serializers.DictField(),
        required=False,
        allow_empty=False,
    )

    def validate(self, attrs):
        """
        Require milestones when prohressive delivery is requested.
        """
        self.extra_service_code = attrs.get("extra_service_code")

        if self.extra_service_code == "progressive_delivery":
            if not attrs.get("milestones"):
                raise serializers.ValidationError(
                    {
                        "milestones": (
                            "Milestones are required for progressive delivery."
                        )
                    }
                )
            
        return attrs