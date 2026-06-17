from __future__ import annotations

from django.urls import path

from orders.api.views.assignment_acceptance.assignment_acceptance_views import (
    AssignmentAcceptView,
    AssignmentRejectView,
)

urlpatterns = [
    path(
        "orders/<int:order_id>/assignment/",
        AssignmentAcceptView.as_view(),
        name="assignment-acceptance-detail",
    ),
    path(
        "orders/<int:order_id>/assignment/accept/",
        AssignmentAcceptView.as_view(),
        name="assignment-accept",
    ),
    path(
        "orders/<int:order_id>/assignment/reject/",
        AssignmentRejectView.as_view(),
        name="assignment-reject",
    ),
]
