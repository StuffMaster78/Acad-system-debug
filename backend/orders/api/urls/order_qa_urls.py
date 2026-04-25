from __future__ import annotations

from django.urls import path

from orders.api.views.qa.order_qa_views import (
    ApproveOrderForClientDeliveryView,
    ReturnOrderToWriterView,
    SubmitOrderForQAView,
)

urlpatterns = [
    path(
        "orders/<int:order_id>/qa/submit/",
        SubmitOrderForQAView.as_view(),
        name="order-submit-for-qa",
    ),
    path(
        "orders/<int:order_id>/qa/approve/",
        ApproveOrderForClientDeliveryView.as_view(),
        name="order-qa-approve",
    ),
    path(
        "orders/<int:order_id>/qa/return/",
        ReturnOrderToWriterView.as_view(),
        name="order-qa-return",
    ),
]