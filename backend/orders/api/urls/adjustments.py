from __future__ import annotations

from django.urls import path

from orders.api.views.adjustments.adjustment_negotiation_views import (
    AdjustmentAcceptView,
    AdjustmentCancelView,
    AdjustmentCounterView,
    AdjustmentCreateView,
    AdjustmentDeclineView,
    AdjustmentStaffOverrideView,
)

urlpatterns = [
    path(
        "orders/<int:order_id>/adjustments/",
        AdjustmentCreateView.as_view(),
        name="adjustment-create",
    ),
    path(
        "adjustments/<int:adjustment_id>/counter/",
        AdjustmentCounterView.as_view(),
        name="adjustment-counter",
    ),
    path(
        "adjustments/<int:adjustment_id>/accept/",
        AdjustmentAcceptView.as_view(),
        name="adjustment-accept",
    ),
    path(
        "adjustments/<int:adjustment_id>/decline/",
        AdjustmentDeclineView.as_view(),
        name="adjustment-decline",
    ),
    path(
        "adjustments/<int:adjustment_id>/cancel/",
        AdjustmentCancelView.as_view(),
        name="adjustment-cancel",
    ),
    path(
        "adjustments/<int:adjustment_id>/staff-override/",
        AdjustmentStaffOverrideView.as_view(),
        name="adjustment-staff-override",
    ),
]