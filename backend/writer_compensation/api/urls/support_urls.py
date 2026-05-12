from __future__ import annotations

from django.urls import path

from writer_compensation.api.views.support_views import (
    SupportHeldRecordsView,
    SupportWriterEventsView,
    SupportWriterPayoutsView,
)

urlpatterns = [
    path(
        "writers/<int:writer_id>/events/",
        SupportWriterEventsView.as_view(),
        name="support-writer-events",
    ),
    path(
        "writers/<int:writer_id>/payouts/",
        SupportWriterPayoutsView.as_view(),
        name="support-writer-payouts",
    ),
    path(
        "held-items/",
        SupportHeldRecordsView.as_view(),
        name="support-held-items",
    ),
]