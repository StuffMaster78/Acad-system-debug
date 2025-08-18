from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CommunicationMessageViewSet, CommunicationThreadViewSet, 
    OrderMessageNotificationViewSet, ScreenedWordViewSet,
    FlaggedMessageViewSet, DisputeMessageViewSet
)

router = DefaultRouter()
router.register(r"communication-messages", CommunicationMessageViewSet, basename="communication-message")
router.register(r"communication-threads", CommunicationThreadViewSet, basename="communication-thread")
router.register(r"communication-notifications", OrderMessageNotificationViewSet, basename="communication-notification")
router.register(r"screened-words", ScreenedWordViewSet, basename="screened-word")
router.register(r"flagged-messages", FlaggedMessageViewSet, basename="flagged-message")
router.register(r"dispute-messages", DisputeMessageViewSet, basename="dispute-message")


urlpatterns = [
    path("", include(router.urls)),
]