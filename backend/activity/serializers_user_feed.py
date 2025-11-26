from rest_framework import serializers

from activity.models import ActivityLog
from activity.serializers import ActivityLogSerializer


class UserActivityFeedSerializer(ActivityLogSerializer):
    """
    User-facing serializer exposing a safe subset of fields for the activity feed.
    Hides raw metadata and low-level details while reusing display_description.
    """

    class Meta(ActivityLogSerializer.Meta):
        model = ActivityLog
        fields = [
            "id",
            "display_description",
            "formatted_timestamp",
            "action_type",
            "actor_type",
        ]
        read_only_fields = fields


