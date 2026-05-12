from __future__ import annotations

from typing import Any

from rest_framework import serializers

from activity.models import ActivityEvent
from activity.models import ActivityFeedState
from activity.renderers.activity_card_renderer import ActivityCardRenderer


class ActivityEventSerializer(serializers.ModelSerializer):
    """
    Serializes activity events for API responses.
    """

    card = serializers.SerializerMethodField()

    class Meta:
        model = ActivityEvent
        fields = (
            "id",
            "verb",
            "actor_type",
            "severity",
            "audiences",
            "title",
            "summary",
            "metadata",
            "occurred_at",
            "created_at",
            "card",
        )
        read_only_fields = fields

    def get_card(self, obj: ActivityEvent) -> dict[str, Any]:
        """
        Return rendered card data for the activity event.
        """
        return ActivityCardRenderer.render(event=obj)


class ActivityFeedStateSerializer(serializers.ModelSerializer):
    """
    Serializes feed state rows.
    """

    event = ActivityEventSerializer(read_only=True)

    class Meta:
        model = ActivityFeedState
        fields = (
            "id",
            "event",
            "is_read",
            "is_dismissed",
            "is_pinned",
            "read_at",
            "dismissed_at",
            "created_at",
        )
        read_only_fields = fields