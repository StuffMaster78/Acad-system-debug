from __future__ import annotations

from django.urls import include, path
from orders.api.views.staffing.bids_views import WriterBidSubmitView

urlpatterns = [
    path("orders/<int:order_id>/bids/", WriterBidSubmitView.as_view(), name="order-bid-submit"),
    path("", include("orders.api.urls.order_viewset_urls")),
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
    path("orders/", include("orders.api.urls.order_file_urls")),
    path("", include("orders.api.urls.notes")),
    path("", include("orders.api.urls.order_review_urls")),
    path("", include("orders.api.urls.writer_requests")),
]
