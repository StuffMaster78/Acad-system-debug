from __future__ import annotations

from django.urls import path

from writer_compensation.api.views.exposure_actions_views import (
    ExposureLedgerDetailView,
    ExposureLedgerListView,
    ExposureRecomputeView,
)

urlpatterns = [
    path(
        "",
        ExposureLedgerListView.as_view(),
        name="exposure-list",
    ),
    path(
        "<int:pk>/",
        ExposureLedgerDetailView.as_view(),
        name="exposure-detail",
    ),
    path(
        "<int:pk>/recompute/",
        ExposureRecomputeView.as_view(),
        name="exposure-recompute",
    ),
]