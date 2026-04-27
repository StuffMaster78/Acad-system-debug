from __future__ import annotations

from django.urls import include, path

urlpatterns = [
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
]