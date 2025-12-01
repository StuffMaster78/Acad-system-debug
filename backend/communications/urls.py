from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CommunicationMessageViewSet, CommunicationThreadViewSet, 
    OrderMessageNotificationViewSet, ScreenedWordViewSet,
    FlaggedMessageViewSet, DisputeMessageViewSet,
    MessageAttachmentUploadView
)

router = DefaultRouter()
# Register threads first
router.register(r"communication-threads", CommunicationThreadViewSet, basename="communication-thread")
# Messages are nested under threads, so register them separately with nested URLs
router.register(r"communication-notifications", OrderMessageNotificationViewSet, basename="communication-notification")
router.register(r"screened-words", ScreenedWordViewSet, basename="screened-word")
router.register(r"flagged-messages", FlaggedMessageViewSet, basename="flagged-message")
router.register(r"dispute-messages", DisputeMessageViewSet, basename="dispute-message")


urlpatterns = [
    path("", include(router.urls)),
    # Nested routes for messages under threads
    path(
        "communication-threads/<int:thread_pk>/communication-messages/",
        CommunicationMessageViewSet.as_view({'get': 'list', 'post': 'create'}),
        name="communication-message-list"
    ),
    path(
        "communication-threads/<int:thread_pk>/communication-messages/<int:pk>/",
        CommunicationMessageViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
        name="communication-message-detail"
    ),
    path(
        "communication-threads/<int:thread_pk>/communication-messages/<int:pk>/download_attachment/",
        CommunicationMessageViewSet.as_view({'get': 'download_attachment'}),
        name="communication-message-download-attachment"
    ),
    path(
        "communication-threads/<int:thread_pk>/communication-messages/available_recipients/",
        CommunicationMessageViewSet.as_view({'get': 'available_recipients'}),
        name="communication-message-available-recipients"
    ),
    path(
        "communication-threads/<int:thread_pk>/communication-messages/<int:pk>/mark_as_read/",
        CommunicationMessageViewSet.as_view({'post': 'mark_as_read'}),
        name="communication-message-mark-as-read"
    ),
    path(
        "communication-threads/<int:thread_pk>/communication-messages/<int:pk>/react/",
        CommunicationMessageViewSet.as_view({'post': 'react', 'delete': 'react'}),
        name="communication-message-react"
    ),
    path(
        "communication-threads/<int:pk>/typing/",
        CommunicationThreadViewSet.as_view({'post': 'typing'}),
        name="communication-thread-typing"
    ),
    path(
        "communication-threads/<int:pk>/typing_status/",
        CommunicationThreadViewSet.as_view({'get': 'typing_status'}),
        name="communication-thread-typing-status"
    ),
    path("message-attachments/", MessageAttachmentUploadView.as_view(), name="message-attachment-upload"),
]