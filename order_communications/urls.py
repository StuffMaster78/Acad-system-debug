from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrderMessageViewSet, OrderMessageThreadViewSet, 
    OrderMessageNotificationViewSet, ScreenedWordViewSet,
    FlaggedMessageViewSet, DisputeMessageViewSet
)

router = DefaultRouter()
router.register(r"order-messages", OrderMessageViewSet, basename="order-message")
router.register(r"order-message-threads", OrderMessageThreadViewSet, basename="order-message-thread")
router.register(r"order-message-notifications", OrderMessageNotificationViewSet, basename="order-message-notification")
router.register(r"screened-words", ScreenedWordViewSet, basename="screened-word")
router.register(r"flagged-messages", FlaggedMessageViewSet, basename="flagged-message")
router.register(r"dispute-messages", DisputeMessageViewSet, basename="dispute-message")

urlpatterns = [
    path("", include(router.urls)),
]