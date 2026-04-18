from __future__ import annotations

from django.urls import path

from orders.api.views.reassignments.reassignment_views import (
    ReassignmentApproveAssignWriterView,
    ReassignmentApproveReturnToPoolView,
    ReassignmentCancelView,
    ReassignmentRejectView,
    ReassignmentRequestView,
)

urlpatterns = [
    path(
        "orders/<int:order_id>/reassignments/",
        ReassignmentRequestView.as_view(),
        name="reassignment-request",
    ),
    path(
        "reassignments/<int:reassignment_id>/reject/",
        ReassignmentRejectView.as_view(),
        name="reassignment-reject",
    ),
    path(
        "reassignments/<int:reassignment_id>/cancel/",
        ReassignmentCancelView.as_view(),
        name="reassignment-cancel",
    ),
    path(
        "reassignments/<int:reassignment_id>/approve-return-to-pool/",
        ReassignmentApproveReturnToPoolView.as_view(),
        name="reassignment-approve-return-to-pool",
    ),
    path(
        "reassignments/<int:reassignment_id>/approve-assign-writer/",
        ReassignmentApproveAssignWriterView.as_view(),
        name="reassignment-approve-assign-writer",
    ),
]