from __future__ import annotations

from django.urls import path

from orders.api.views.staffing.staffing_views import (
    ExpressInterestView,
    RouteOrderToStaffingView,
    TakeOrderView,
)
from orders.api.views.staffing.staffing_views import (
    AssignDirectView,
    AssignFromInterestView,
    WithdrawInterestView,
)
from orders.api.views.staffing.staffing_views import (
    PreferredWriterAcceptView,
    PreferredWriterDeclineView,
    ReleaseToPoolView,
)

urlpatterns = [
    path(
        "orders/<int:order_id>/staffing/route/",
        RouteOrderToStaffingView.as_view(),
        name="route-order-to-staffing",
    ),
    path(
        "orders/<int:order_id>/staffing/interests/",
        ExpressInterestView.as_view(),
        name="express-interest",
    ),
    path(
        "orders/<int:order_id>/staffing/take/",
        TakeOrderView.as_view(),
        name="take-order",
    ),
        path(
        "staffing/interests/<int:interest_id>/withdraw/",
        WithdrawInterestView.as_view(),
        name="withdraw-interest",
    ),
    path(
        "staffing/interests/<int:interest_id>/assign/",
        AssignFromInterestView.as_view(),
        name="assign-from-interest",
    ),
    path(
        "orders/<int:order_id>/staffing/assign-direct/",
        AssignDirectView.as_view(),
        name="assign-direct",
    ),
        path(
        "staffing/interests/<int:interest_id>/preferred-accept/",
        PreferredWriterAcceptView.as_view(),
        name="preferred-writer-accept",
    ),
    path(
        "staffing/interests/<int:interest_id>/preferred-decline/",
        PreferredWriterDeclineView.as_view(),
        name="preferred-writer-decline",
    ),
    path(
        "orders/<int:order_id>/staffing/release-to-pool/",
        ReleaseToPoolView.as_view(),
        name="release-to-pool",
    ),
]