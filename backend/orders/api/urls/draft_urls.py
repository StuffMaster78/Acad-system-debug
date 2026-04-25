from django.urls import path

from orders.api.views.drafts.draft_views import (
    ReviewDraftView,
    SubmitDraftView,
)

urlpatterns = [
    path(
        "orders/<int:order_id>/drafts/submit/",
        SubmitDraftView.as_view(),
    ),
    path(
        "drafts/<int:draft_id>/review/",
        ReviewDraftView.as_view(),
    ),
]