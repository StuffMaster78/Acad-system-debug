from __future__ import annotations

from django.urls import path

from writer_compensation.api.views.settlement_actions_views import (
    RunSettlementView,
)
from writer_compensation.api.views.settlement_views import (
    SettlementDetailView,
    SettlementListView,
)

urlpatterns = [
    path(
        "",
        SettlementListView.as_view(),
        name="settlement-list",
    ),
    path(
        "<int:pk>/",
        SettlementDetailView.as_view(),
        name="settlement-detail",
    ),
    path(
        "run/",
        RunSettlementView.as_view(),
        name="run-settlement",
    ),
]