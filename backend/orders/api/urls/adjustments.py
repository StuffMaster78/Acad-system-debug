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

urlpatterns = [
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
    path(
        "orders/adjustments/<int:adjustment_id>/counter-scope/",
        ClientCounterScopeIncrementView.as_view(),
        name="order-adjustment-counter-scope",
    ),
    path(
        "orders/adjustments/<int:adjustment_id>/accept-extra-service/",
        ClientAcceptExtraServiceView.as_view(),
        name="order-adjustment-accept-extra-service",
    ),
]