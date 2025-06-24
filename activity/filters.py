import django_filters
from django.utils.timezone import now, timedelta
from activity.models import ActivityLog


TIME_RANGE_CHOICES = [
    ("today", "Today"),
    ("yesterday", "Yesterday"),
    ("last_24h", "Last 24 Hours"),
    ("this_week", "This Week"),
    ("last_7d", "Last 7 Days"),
    ("this_month", "This Month"),
]

class ActivityLogFilter(django_filters.FilterSet):
    """
    Filter set for activity logs.

    GET /api/activity-logs/?time_range=last_24h
    GET /api/activity-logs/?time_range=this_week
    GET /api/activity-logs/?time_range=last_7d
    Supports filtering by action type, user, triggered_by, website,
    and timestamp range.
    Supports time range filtering with predefined choices.
    Supports searching by description and metadata.
    Supports ordering by timestamp and action type.
    Supports filtering by timestamp before and after a specific date.
    Supports filtering by time range keywords like "last_24h", "this_week", etc 
    
    """
    timestamp_after = django_filters.IsoDateTimeFilter(
        field_name="timestamp",
        lookup_expr="gte"
    )
    timestamp_before = django_filters.IsoDateTimeFilter(
        field_name="timestamp",
        lookup_expr="lte"
    )
    time_range = django_filters.ChoiceFilter(
        choices=TIME_RANGE_CHOICES,
        method="filter_by_time_range",
        label="Time Range"
    )

    class Meta:
        model = ActivityLog
        fields = {
            "action_type": ["exact"],
            "user": ["exact"],
            "triggered_by": ["exact"],
            "website": ["exact"],
        }
        order_by = ["-timestamp"]
        search_fields = ["description", "metadata"]
        ordering_fields = ["timestamp", "action_type"]


    def filter_by_time_range(self, queryset, name, value):
        """ Filter queryset by predefined time ranges.
            Supports: today, yesterday, last_24h,
            this_week, last_7d, this_month
        """
        current_time = now()

        if value == "today":
            start = current_time.replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            return queryset.filter(timestamp__gte=start)

        elif value == "yesterday":
            start = (current_time - timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            end = start + timedelta(days=1)
            return queryset.filter(
                timestamp__gte=start,
                timestamp__lt=end
            )

        elif value == "last_24h":
            return queryset.filter(
                timestamp__gte=current_time - timedelta(hours=24)
            )

        elif value == "this_week":
            start = current_time - timedelta(days=current_time.weekday())
            start = start.replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            return queryset.filter(timestamp__gte=start)

        elif value == "last_7d":
            return queryset.filter(
                timestamp__gte=current_time - timedelta(days=7)
            )

        elif value == "this_month":
            start = current_time.replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            return queryset.filter(timestamp__gte=start)

        return queryset