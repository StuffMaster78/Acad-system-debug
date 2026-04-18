from __future__ import annotations

from django.urls import path

from orders.api.views.disputes.dispute_views import (
    DisputeCloseView,
    DisputeEscalateView,
    DisputeOpenView,
    DisputeResolveView,
)

urlpatterns = [
    path(
        "orders/<int:order_id>/disputes/",
        DisputeOpenView.as_view(),
        name="dispute-open",
    ),
    path(
        "disputes/<int:dispute_id>/escalate/",
        DisputeEscalateView.as_view(),
        name="dispute-escalate",
    ),
    path(
        "disputes/<int:dispute_id>/resolve/",
        DisputeResolveView.as_view(),
        name="dispute-resolve",
    ),
    path(
        "disputes/<int:dispute_id>/close/",
        DisputeCloseView.as_view(),
        name="dispute-close",
    ),
]