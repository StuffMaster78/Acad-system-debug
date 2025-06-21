# reviews_system/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from reviews_system.views import (
    WebsiteReviewViewSet,
    WriterReviewViewSet,
    OrderReviewViewSet,
)

router = DefaultRouter()
router.register(r"website-reviews", WebsiteReviewViewSet, basename="website-review")
router.register(r"writer-reviews", WriterReviewViewSet, basename="writer-review")
router.register(r"order-reviews", OrderReviewViewSet, basename="order-review")

urlpatterns = [
    path("", include(router.urls)),
]