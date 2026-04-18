from __future__ import annotations

from django.urls import path

from orders.api.views.holds.hold_views import (
    HoldActivateView,
    HoldCancelView,
    HoldReleaseView,
    HoldRequestView,
)

urlpatterns = [
    path(
        "orders/<int:order_id>/holds/",
        HoldRequestView.as_view(),
        name="hold-request",
    ),
    path(
        "holds/<int:hold_id>/activate/",
        HoldActivateView.as_view(),
        name="hold-activate",
    ),
    path(
        "holds/<int:hold_id>/release/",
        HoldReleaseView.as_view(),
        name="hold-release",
    ),
    path(
        "holds/<int:hold_id>/cancel/",
        HoldCancelView.as_view(),
        name="hold-cancel",
    ),
]