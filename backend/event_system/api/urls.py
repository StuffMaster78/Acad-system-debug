from django.urls import path

from event_system.api.views.event_list_view import EventListAPIView
from event_system.api.views.event_detail_view import EventDetailAPIView
from event_system.api.views.event_replay_view import EventReplayAPIView
from event_system.api.views.event_failure_view import EventFailureAPIView
from event_system.api.views.event_metrics_view import EventMetricsAPIView
from event_system.api.views.event_timeline_view import EventTimelineAPIView


urlpatterns = [
    path("events/", EventListAPIView.as_view(), name="event-list"),

    path("events/<uuid:event_id>/", EventDetailAPIView.as_view(), name="event-detail"),

    path("events/<uuid:event_id>/replay/", EventReplayAPIView.as_view(), name="event-replay"),

    path("events/<uuid:event_id>/failures/", EventFailureAPIView.as_view(), name="event-failures"),

    path("events/metrics/", EventMetricsAPIView.as_view(), name="event-metrics"),

    path("events/timeline/", EventTimelineAPIView.as_view(), name="event-timeline"),
]