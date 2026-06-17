from __future__ import annotations

from django.urls import path

from orders.api.views.adjustments.client_counter_scope_views import (
    ClientCounterScopeIncrementView,
)
from orders.api.views.adjustments.extra_service_adjustment_views import (
    ClientAcceptExtraServiceView,
    CreateExtraServiceAdjustmentView,
)
from orders.api.views.adjustments.scope_increment_adjustment_views import (
    CreateScopeIncrementAdjustmentView,
)
from orders.api.views.adjustments.adjustment_negotiation_views import (
    AdjustmentAcceptView,
    AdjustmentCancelView,
    AdjustmentCounterView,
    AdjustmentCreateView,
    AdjustmentDeclineView,
    AdjustmentStaffOverrideView,
    ClientAcceptScopeRequestView,
    StaffResolveAdjustmentEscalationView,
    WriterEscalateAdjustmentView,
)
from orders.api.views.adjustments.adjustment_detail_views import (
    AdjustmentDetailView,
    LatestOrderAdjustmentView,
)
from orders.api.views.adjustments.adjustment_inbox_views import StaffAdjustmentInboxView

urlpatterns = [
    # --- Staff inbox ---
    path(
        "orders/adjustments/inbox/",
        StaffAdjustmentInboxView.as_view(),
        name="order-adjustment-inbox",
    ),

    # --- Create ---
    path(
        "orders/<int:order_id>/adjustments/",
        AdjustmentCreateView.as_view(),
        name="order-adjustment-create",
    ),
    path(
        "orders/<int:order_id>/adjustments/scope-increment/",
        CreateScopeIncrementAdjustmentView.as_view(),
        name="order-adjustment-scope-increment-create",
    ),
    path(
        "orders/<int:order_id>/adjustments/extra-service/",
        CreateExtraServiceAdjustmentView.as_view(),
        name="order-adjustment-extra-service-create",
    ),

    # --- Client actions ---
    path(
        "orders/adjustments/<int:adjustment_id>/counter-scope/",
        ClientCounterScopeIncrementView.as_view(),
        name="order-adjustment-counter-scope",
    ),
    path(
        "orders/adjustments/<int:adjustment_id>/accept-scope/",
        ClientAcceptScopeRequestView.as_view(),
        name="order-adjustment-accept-scope",
    ),
    path(
        "orders/adjustments/<int:adjustment_id>/accept-extra-service/",
        ClientAcceptExtraServiceView.as_view(),
        name="order-adjustment-accept-extra-service",
    ),
    path(
        "orders/adjustments/<int:adjustment_id>/counter/",
        AdjustmentCounterView.as_view(),
        name="order-adjustment-counter",
    ),
    path(
        "orders/adjustments/<int:adjustment_id>/accept/",
        AdjustmentAcceptView.as_view(),
        name="order-adjustment-accept",
    ),
    path(
        "orders/adjustments/<int:adjustment_id>/decline/",
        AdjustmentDeclineView.as_view(),
        name="order-adjustment-decline",
    ),
    path(
        "orders/adjustments/<int:adjustment_id>/cancel/",
        AdjustmentCancelView.as_view(),
        name="order-adjustment-cancel",
    ),

    # --- Writer escalation ---
    path(
        "orders/adjustments/<int:adjustment_id>/escalate/",
        WriterEscalateAdjustmentView.as_view(),
        name="order-adjustment-escalate",
    ),

    # --- Read ---
    path(
        "orders/adjustments/<int:adjustment_id>/",
        AdjustmentDetailView.as_view(),
        name="order-adjustment-detail",
    ),
    path(
        "orders/<int:order_id>/adjustments/latest/",
        LatestOrderAdjustmentView.as_view(),
        name="order-adjustment-latest",
    ),

    # --- Staff actions ---
    path(
        "orders/adjustments/<int:adjustment_id>/staff-override/",
        AdjustmentStaffOverrideView.as_view(),
        name="order-adjustment-staff-override",
    ),
    path(
        "orders/adjustments/<int:adjustment_id>/resolve-escalation/",
        StaffResolveAdjustmentEscalationView.as_view(),
        name="order-adjustment-resolve-escalation",
    ),
]
