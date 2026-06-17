from __future__ import annotations

from django.urls import path

from orders.api.views.cancellation.cancellation_request_views import (
    CancellationRequestApproveView,
    CancellationRequestCreateView,
    CancellationRequestRejectView,
)

urlpatterns = [
    path(
        "orders/<int:order_id>/cancellation-request/",
        CancellationRequestCreateView.as_view(),
        name="cancellation-request-create",
    ),
    path(
        "orders/<int:order_id>/cancellation-request/<int:req_id>/approve/",
        CancellationRequestApproveView.as_view(),
        name="cancellation-request-approve",
    ),
    path(
        "orders/<int:order_id>/cancellation-request/<int:req_id>/reject/",
        CancellationRequestRejectView.as_view(),
        name="cancellation-request-reject",
    ),
]
