from __future__ import annotations

from django.urls import path

from orders.api.views.approval.order_approval_views import (
    ApproveOrderView,
)

urlpatterns = [
    path(
        "orders/<int:order_id>/approve/",
        ApproveOrderView.as_view(),
        name="approve-order",
    ),
]