from __future__ import annotations

from django.urls import path

from writer_compensation.api.views.writer_payout_views import (
    WriterCurrentWindowView,
    WriterCycleChangeRequestView,
    WriterEventListView,
    WriterLifetimeSummaryView,
    WriterPayoutHistoryView,
    WriterPayoutPreferenceView,
)

urlpatterns = [
    path(
        "compensation/current-window/",
        WriterCurrentWindowView.as_view(),
        name="writer-current-window",
    ),
    path(
        "compensation/events/",
        WriterEventListView.as_view(),
        name="writer-event-list",
    ),
    path(
        "compensation/payouts/",
        WriterPayoutHistoryView.as_view(),
        name="writer-payout-history",
    ),
    path(
        "compensation/summary/",
        WriterLifetimeSummaryView.as_view(),
        name="writer-lifetime-summary",
    ),
    path(
        "compensation/preference/",
        WriterPayoutPreferenceView.as_view(),
        name="writer-payout-preference",
    ),
    path(
        "compensation/cycle-change/",
        WriterCycleChangeRequestView.as_view(),
        name="writer-cycle-change-request",
    ),
]