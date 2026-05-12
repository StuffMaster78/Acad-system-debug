from __future__ import annotations

from django.urls import path

from writer_compensation.api.views.financial_event_views import (
    FinancialEventDetailView,
    FinancialEventListView,
)

urlpatterns = [
    path(
        "",
        FinancialEventListView.as_view(),
        name="financial-event-list",
    ),
    path(
        "<int:pk>/",
        FinancialEventDetailView.as_view(),
        name="financial-event-detail",
    ),
]