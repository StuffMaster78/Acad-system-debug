from __future__ import annotations

from django.urls import path

from orders.api.views.monitoring.order_monitoring_views import (
    OrderMonitoringView,
)

urlpatterns = [
    path(
        "orders/<int:order_id>/monitoring/",
        OrderMonitoringView.as_view(),
        name="order-monitoring",
    ),
]