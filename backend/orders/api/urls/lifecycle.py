from __future__ import annotations

from django.urls import path

from orders.api.views.lifecycle.order_lifecycle_views import (
    OrderLifecycleView,
)

urlpatterns = [
    path(
        "orders/<int:order_id>/lifecycle/",
        OrderLifecycleView.as_view(),
        name="order-lifecycle",
    ),
]