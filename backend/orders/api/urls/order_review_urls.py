from django.urls import path
from reviews_system.api.views.typed_review_views import OrderReviewView

urlpatterns = [
    path(
        "orders/<int:order_id>/review/",
        OrderReviewView.as_view(),
        name="order-review",
    ),
]
