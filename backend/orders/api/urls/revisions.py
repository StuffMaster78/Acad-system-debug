from __future__ import annotations

from django.urls import path

from orders.api.views.revisions.revision_views import (
    RevisionRequestView,
    RevisionApproveView,
    RevisionRejectView,
    RevisionCompleteView,
    RevisionAcceptView,
)

urlpatterns = [
    path(
        "orders/<int:order_id>/revisions/",
        RevisionRequestView.as_view(),
        name="revision-list-create",
    ),
    path(
        "orders/<int:order_id>/revisions/<int:rev_id>/approve/",
        RevisionApproveView.as_view(),
        name="revision-approve",
    ),
    path(
        "orders/<int:order_id>/revisions/<int:rev_id>/reject/",
        RevisionRejectView.as_view(),
        name="revision-reject",
    ),
    path(
        "orders/<int:order_id>/revisions/<int:rev_id>/complete/",
        RevisionCompleteView.as_view(),
        name="revision-complete",
    ),
    path(
        "orders/<int:order_id>/revisions/<int:rev_id>/accept/",
        RevisionAcceptView.as_view(),
        name="revision-accept",
    ),
]
