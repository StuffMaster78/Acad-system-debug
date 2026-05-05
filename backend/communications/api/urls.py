from __future__ import annotations

from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from communications.api.views.audit_log_views import CommunicationAuditLogViewSet
from communications.api.views.escalation_views import CommunicationEscalationViewSet
from communications.api.views.link_review_views import CommunicationLinkReviewViewSet
from communications.api.views.message_views import CommunicationMessageViewSet
from communications.api.views.moderation_flag_views import CommunicationModerationFlagViewSet
from communications.api.views.participant_views import CommunicationParticipantViewSet
from communications.api.views.saved_reply_views import CommunicationSavedReplyViewSet
from communications.api.views.screening_rule_views import CommunicationScreeningRuleViewSet
from communications.api.views.assignment_views import CommunicationThreadAssignmentViewSet
from communications.api.views.sla_views import CommunicationThreadSLAViewSet
from communications.api.views.tag_views import CommunicationThreadTagAssignmentViewSet
from communications.api.views.tag_views import CommunicationThreadTagViewSet
from communications.api.views.thread_views import CommunicationThreadViewSet
from communications.api.views.sse_views import CommunicationSSEView
from communications.api.views.read_receipt_views import CommunicationReadReceiptViewSet
from communications.api.views.attachment_views import CommunicationAttachmentViewSet

app_name = "communications_api"

router = DefaultRouter()

router.register(
    r"threads",
    CommunicationThreadViewSet,
    basename="communication-thread",
)
router.register(
    r"messages",
    CommunicationMessageViewSet,
    basename="communication-message",
)
router.register(
    r"participants",
    CommunicationParticipantViewSet,
    basename="communication-participant",
)
router.register(
    r"assignments",
    CommunicationThreadAssignmentViewSet,
    basename="communication-assignment",
)
router.register(
    r"tags",
    CommunicationThreadTagViewSet,
    basename="communication-tag",
)
router.register(
    r"tag-assignments",
    CommunicationThreadTagAssignmentViewSet,
    basename="communication-tag-assignment",
)
router.register(
    r"saved-replies",
    CommunicationSavedReplyViewSet,
    basename="communication-saved-reply",
)
router.register(
    r"escalations",
    CommunicationEscalationViewSet,
    basename="communication-escalation",
)
router.register(
    r"moderation-flags",
    CommunicationModerationFlagViewSet,
    basename="communication-moderation-flag",
)
router.register(
    r"screening-rules",
    CommunicationScreeningRuleViewSet,
    basename="communication-screening-rule",
)
router.register(
    r"link-reviews",
    CommunicationLinkReviewViewSet,
    basename="communication-link-review",
)
router.register(
    r"audit-logs",
    CommunicationAuditLogViewSet,
    basename="communication-audit-log",
)
router.register(
    r"slas",
    CommunicationThreadSLAViewSet,
    basename="communication-sla",
)
router.register(
    r"read-receipts",
    CommunicationReadReceiptViewSet,
    basename="communication-read-receipt",
)
router.register(
    r"attachments",
    CommunicationAttachmentViewSet,
    basename="communication-attachment",
)

urlpatterns = [
    path("events/", CommunicationSSEView.as_view(), name="events"),
    path("", include(router.urls)),
]