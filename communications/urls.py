from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrderMessageViewSet, OrderMessageThreadViewSet, 
    OrderMessageNotificationViewSet, ScreenedWordViewSet,
    FlaggedMessageViewSet, DisputeMessageViewSet
)
from communications.views import WebSocketAuditLogViewSet

router = DefaultRouter()
router.register(r"order-messages", OrderMessageViewSet, basename="order-message")
router.register(r"order-message-threads", OrderMessageThreadViewSet, basename="order-message-thread")
router.register(r"order-message-notifications", OrderMessageNotificationViewSet, basename="order-message-notification")
router.register(r"screened-words", ScreenedWordViewSet, basename="screened-word")
router.register(r"flagged-messages", FlaggedMessageViewSet, basename="flagged-message")
router.register(r"dispute-messages", DisputeMessageViewSet, basename="dispute-message")
router.register(r"websocket-audit-logs", WebSocketAuditLogViewSet, basename="ws-audit")

urlpatterns = [
    path("", include(router.urls)),
]