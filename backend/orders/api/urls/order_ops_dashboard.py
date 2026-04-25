from __future__ import annotations

from django.urls import path

from orders.api.views.dashboard.order_ops_dashboard_views import (
    OrderOpsDashboardSummaryView,
    OrderOpsQueueView,
)

urlpatterns = [
    path(
        "orders/ops/summary/",
        OrderOpsDashboardSummaryView.as_view(),
        name="order-ops-summary",
    ),
    path(
        "orders/ops/queues/<str:queue_key>/",
        OrderOpsQueueView.as_view(),
        name="order-ops-queue",
    ),
]