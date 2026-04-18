from __future__ import annotations

from django.urls import path

from orders.api.views.revisions.revision_views import (
    RevisionRequestView,
)

urlpatterns = [
    path(
        "orders/<int:order_id>/revisions/",
        RevisionRequestView.as_view(),
        name="revision-request",
    ),
]