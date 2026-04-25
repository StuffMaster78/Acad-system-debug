from __future__ import annotations

from django.urls import path

from orders.api.views.archival.order_archival_views import (
    OrderArchivalView,
)
from orders.api.views.cancellation.order_cancellation_views import (
    OrderCancellationView,
)

urlpatterns = [
    path(
        "orders/<int:order_id>/cancel/",
        OrderCancellationView.as_view(),
        name="order-cancel",
    ),
    path(
        "orders/<int:order_id>/archive/",
        OrderArchivalView.as_view(),
        name="order-archive",
    ),
]