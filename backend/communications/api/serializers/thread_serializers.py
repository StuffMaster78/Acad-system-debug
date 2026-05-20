from __future__ import annotations

from typing import Any

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from communications.models.thread import CommunicationThread


class CommunicationThreadSerializer(serializers.ModelSerializer):
    """
    Read serializer for communication threads.
    """

    target_type = serializers.SerializerMethodField()
    target_id = serializers.IntegerField(source="target_object_id")

    class Meta:
        model = CommunicationThread
        fields = [
            "id",
            "website",
            "target_type",
            "target_id",
            "kind",
            "status",
            "subject",
            "reference",
            "last_message_at",
            "locked_at",
            "closed_at",
            "archived_at",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_target_type(self, obj: CommunicationThread) -> str:
        """
        Return target model label.
        """
        return obj.target_content_type.model


class CommunicationThreadCreateSerializer(serializers.Serializer):
    """
    Validate thread creation input.
    """

    target_app_label = serializers.CharField(max_length=100)
    target_model = serializers.CharField(max_length=100)
    target_object_id = serializers.IntegerField()
    kind = serializers.CharField(max_length=40)
    subject = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
    )
    reference = serializers.CharField(
        max_length=80,
        required=False,
        allow_blank=True,
    )
    metadata = serializers.DictField(required=False)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """
        Resolve and attach content type.
        """
        try:
            content_type = ContentType.objects.get(
                app_label=attrs["target_app_label"],
                model=attrs["target_model"],
            )
        except ContentType.DoesNotExist as exc:
            raise serializers.ValidationError(
                {"target_model": "Invalid target model."},
            ) from exc

        try:
            target = content_type.get_object_for_this_type(
                pk=attrs["target_object_id"],
            )
        except ObjectDoesNotExist as exc:
            raise serializers.ValidationError(
                {"target_object_id": "Target object was not found."},
            ) from exc

        attrs["target_content_type"] = content_type
        attrs["target"] = target
        return attrs
