from __future__ import annotations

from django.urls import path

from orders.api.views.submissions.submission_views import (
    CompleteOrderView,
    ReopenOrderView,
    SubmitOrderView,
)

urlpatterns = [
    path(
        "orders/<int:order_id>/submit/",
        SubmitOrderView.as_view(),
        name="submit-order",
    ),
    path(
        "orders/<int:order_id>/complete/",
        CompleteOrderView.as_view(),
        name="complete-order",
    ),
    path(
        "orders/<int:order_id>/reopen/",
        ReopenOrderView.as_view(),
        name="reopen-order",
    ),
]