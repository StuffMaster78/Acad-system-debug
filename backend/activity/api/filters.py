from __future__ import annotations

from datetime import timedelta

import django_filters
from django.utils.timezone import now

from activity.models import ActivityEvent


TIME_RANGE_CHOICES = [
    ("today", "Today"),
    ("yesterday", "Yesterday"),
    ("last_24h", "Last 24 Hours"),
    ("this_week", "This Week"),
    ("last_7d", "Last 7 Days"),
    ("this_month", "This Month"),
]


class ActivityEventFilter(django_filters.FilterSet):
    """
    Filter set for activity events.

    Supports direct filtering by verb, severity, actor type, and date ranges.
    Supports predefined time range keywords such as today, yesterday,
    last_24h, this_week, last_7d, and this_month.
    """

    occurred_after = django_filters.IsoDateTimeFilter(
        field_name="occurred_at",
        lookup_expr="gte",
    )
    occurred_before = django_filters.IsoDateTimeFilter(
        field_name="occurred_at",
        lookup_expr="lte",
    )
    time_range = django_filters.ChoiceFilter(
        choices=TIME_RANGE_CHOICES,
        method="filter_by_time_range",
        label="Time Range",
    )
    is_unread = django_filters.BooleanFilter(
        method="filter_is_unread",
    )
    is_pinned = django_filters.BooleanFilter(
        method="filter_is_pinned",
    )
    is_dismissed = django_filters.BooleanFilter(
        method="filter_is_dismissed",
    )

    class Meta:
        model = ActivityEvent
        fields = (
            "verb",
            "severity",
            "actor_type",
            "occurred_after",
            "occurred_before",
            "time_range",
            "is_unread",
            "is_pinned",
            "is_dismissed",
        )

    def filter_by_time_range(self, queryset, name, value):
        """
        Filter queryset by a predefined time range.
        """
        current_time = now()

        if value == "today":
            start = current_time.replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )
            return queryset.filter(occurred_at__gte=start)

        if value == "yesterday":
            start = (current_time - timedelta(days=1)).replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )
            end = start + timedelta(days=1)
            return queryset.filter(
                occurred_at__gte=start,
                occurred_at__lt=end,
            )

        if value == "last_24h":
            return queryset.filter(
                occurred_at__gte=current_time - timedelta(hours=24),
            )

        if value == "this_week":
            start = current_time - timedelta(days=current_time.weekday())
            start = start.replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )
            return queryset.filter(occurred_at__gte=start)

        if value == "last_7d":
            return queryset.filter(
                occurred_at__gte=current_time - timedelta(days=7),
            )

        if value == "this_month":
            start = current_time.replace(
                day=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )
            return queryset.filter(occurred_at__gte=start)

        return queryset

    def filter_is_unread(self, queryset, name, value):
        """
        Filter events by unread state for the current user.
        """
        user = self._get_request_user()

        if user is None:
            return queryset.none()

        return queryset.filter(
            feed_states__user=user,
            feed_states__is_read=not value,
        )

    def filter_is_pinned(self, queryset, name, value):
        """
        Filter events by pinned state for the current user.
        """
        user = self._get_request_user()

        if user is None:
            return queryset.none()

        return queryset.filter(
            feed_states__user=user,
            feed_states__is_pinned=value,
        )

    def filter_is_dismissed(self, queryset, name, value):
        """
        Filter events by dismissed state for the current user.
        """
        user = self._get_request_user()

        if user is None:
            return queryset.none()

        return queryset.filter(
            feed_states__user=user,
            feed_states__is_dismissed=value,
        )


    def _get_request_user(self):
        """
        Return the current request user if available.
        """
        request = self.request

        if request is None:
            return None

        return request.user