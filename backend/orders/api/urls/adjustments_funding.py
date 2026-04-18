from __future__ import annotations

from django.urls import path

from orders.api.views.adjustments.adjustment_funding_views import (
    AdjustmentApplyPaymentView,
    AdjustmentAttachPaymentIntentView,
    AdjustmentFundingCreateView,
    AdjustmentMarkPaymentRequestView,
)

urlpatterns = [
    path(
        "adjustments/<int:adjustment_id>/funding/create/",
        AdjustmentFundingCreateView.as_view(),
        name="adjustment-funding-create",
    ),
    path(
        "funding/<int:funding_id>/attach-payment-intent/",
        AdjustmentAttachPaymentIntentView.as_view(),
        name="adjustment-attach-payment-intent",
    ),
    path(
        "funding/<int:funding_id>/mark-payment-request-created/",
        AdjustmentMarkPaymentRequestView.as_view(),
        name="adjustment-mark-payment-request-created",
    ),
    path(
        "funding/<int:funding_id>/apply-payment/",
        AdjustmentApplyPaymentView.as_view(),
        name="adjustment-apply-payment",
    ),
]