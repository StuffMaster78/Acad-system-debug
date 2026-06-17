from __future__ import annotations

from django.urls import include, path

from orders.api.views.order_number_views import (
    OrderNumberSequenceDetailView,
    OrderNumberSequenceListCreateView,
    WorkReferenceLookupView,
)

urlpatterns = [
    # Order number sequences (admin-configurable public numbering)
    path(
        "number-sequences/",
        OrderNumberSequenceListCreateView.as_view(),
        name="order-number-sequence-list-create",
    ),
    path(
        "number-sequences/<int:pk>/",
        OrderNumberSequenceDetailView.as_view(),
        name="order-number-sequence-detail",
    ),
    path(
        "number-sequences/<int:pk>/deactivate/",
        OrderNumberSequenceDetailView.as_view(),
        name="order-number-sequence-deactivate",
    ),
    path(
        "reference-lookup/<str:reference>/",
        WorkReferenceLookupView.as_view(),
        name="work-reference-lookup",
    ),
    path("", include("orders.api.urls.staffing")),
    path("", include("orders.api.urls.reassignments")),
    path("", include("orders.api.urls.submissions")),
    path("", include("orders.api.urls.holds")),
    path("", include("orders.api.urls.revisions")),
    path("", include("orders.api.urls.adjustments")),
    path("", include("orders.api.urls.adjustments_funding")),
    path("", include("orders.api.urls.disputes")),
    path("", include("orders.api.urls.lifecycle")),
    path("", include("orders.api.urls.approval")),
    path("", include("orders.api.urls.monitoring")),
    path("", include("orders.api.urls.order_action_urls")),
    path("", include("orders.api.urls.order_creation_urls")),
    path("", include("orders.api.urls.order_ops_dashboard")),
    path("", include("orders.api.urls.order_qa_urls")),
    path("", include("orders.api.urls.draft_urls")),
    path("", include("orders.api.urls.progressive_delivery_urls")),
    path("", include("orders.api.urls.order_file_urls")),
    path("", include("orders.api.urls.assignment_acceptance")),
    path("", include("orders.api.urls.cancellation_requests")),
]
