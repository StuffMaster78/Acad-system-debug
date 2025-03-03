from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DiscountViewSet, SeasonalEventViewSet

# Using a router for RESTful endpoints
router = DefaultRouter()
router.register(r"discounts", DiscountViewSet, basename="discount")
router.register(r"seasonal-events", SeasonalEventViewSet, basename="seasonal-event")

urlpatterns = [
    path("", include(router.urls)),  # Include all registered routes
]