from django.urls import path

from reviews_system.api.views.review_create_view import ReviewCreateView
from reviews_system.api.views.review_list_view import ReviewListView
from reviews_system.api.views.review_moderation_view import ReviewModerationView
from reviews_system.api.views.typed_review_views import WebsiteReviewSubmitView

urlpatterns = [
    # Legacy unified-Review endpoints
    path("reviews/", ReviewCreateView.as_view(), name="review-create"),
    path("reviews/list/", ReviewListView.as_view(), name="review-list"),
    path("reviews/moderate/", ReviewModerationView.as_view(), name="review-moderation"),
    # Typed review endpoints
    path("reviews/website-review/", WebsiteReviewSubmitView.as_view(), name="website-review-submit"),
]