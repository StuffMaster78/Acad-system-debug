from django_filters import (
    rest_framework as filters
)
from notifications_system.models.notifications import Notification

class NotificationFilter(filters.FilterSet):
    # booleans on notifications themselves
    is_critical = filters.BooleanFilter(
        field_name="is_critical"
    )
    is_digest = filters.BooleanFilter(
        field_name="is_digest"
    )

    # booleans via NotificationsUserStatus relation
    is_read = filters.BooleanFilter(
        field_name="user_statuses__is_read"
    )
    is_acknowledged = filters.BooleanFilter(
        field_name="user_statuses__is_acknowledged"
    )
    pinned = filters.BooleanFilter(
        field_name="user_statuses__pinned"
    )

    # strings / ids on notifications themselves
    event = filters.CharFilter(
        field_name="event",
        lookup_expr="icontains"
    )
    category = filters.CharFilter(
        field_name="category",
        lookup_expr="iexact"
    )
    digest_group = filters.CharFilter(
        field_name="digest_group",
        lookup_expr="iexact"
    )
    channel = filters.CharFilter(
        field_name="type",
        lookup_expr="exact"
    )  # alias if you prefer "channel"
    user_id = filters.NumberFilter(
        field_name="user_statuses__user_id"
    )  # optional

    # priority (int)
    priority = filters.NumberFilter(
        field_name="priority"
    )

    # user lookups
    user_id = filters.NumberFilter(
        field_name="user__id"
    )
    user_email = filters.CharFilter(
        field_name="user__email",
        lookup_expr="icontains"
    )
    user_username = filters.CharFilter(
        field_name="user__username",
        lookup_expr="icontains"
    )

    # date ranges (ISO8601)
    sent_at = filters.IsoDateTimeFromToRangeFilter(
        field_name="sent_at"
    )
    created_at = filters.IsoDateTimeFromToRangeFilter(
        field_name="created_at"
    )

    # ordering (use ?ordering=sent_at or -priority)
    ordering = filters.OrderingFilter(
        fields=(
            ("sent_at", "sent_at"),
            ("created_at", "created_at"),
            ("priority", "priority"),
        )
    )

    class Meta:
        model = Notification
        fields = [
            "event",
            "category",
            "is_critical",
            "is_digest",
            "priority",
            "digest_group",
            "type",
            "user_id",  # admin-only; omit for user endpoints
            "user_email",
            "user_username",
            "sent_at",
            "created_at",
        ]