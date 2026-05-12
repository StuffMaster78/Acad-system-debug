from __future__ import annotations

from django.urls import path

from writer_compensation.api.views.exposure_views import (
    ExposureLedgerDetailView,
    ExposureLedgerListView,
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
]