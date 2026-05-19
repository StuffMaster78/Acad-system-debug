from communications.models.attachment import CommunicationAttachment
from communications.models.audit import CommunicationAuditLog
from communications.models.message import CommunicationMessage
from communications.models.moderation import CommunicationModerationFlag
from communications.models.participant import CommunicationParticipant
from communications.models.receipt import CommunicationReadReceipt
from communications.models.thread import CommunicationThread
from communications.models.edit import CommunicationMessageEdit
from communications.models.policy import CommunicationThreadPolicy
from communications.models.sla import CommunicationThreadSLA
from communications.models.assignment import CommunicationThreadAssignment

from communications.models.escalation import CommunicationEscalation
from communications.models.escalation import CommunicationEscalationStatus
from communications.models.audit import CommunicationAuditAction
from communications.models.moderation import CommunicationModerationSeverity
from communications.models.moderation import CommunicationModerationStatus
from communications.models.saved_reply import CommunicationSavedReply
from communications.models.tag import CommunicationThreadTag
from communications.models.tag import CommunicationThreadTagAssignment
from communications.models.link_review import CommunicationLinkReview
from communications.models.link_review import CommunicationLinkReviewStatus
from communications.models.screening_rule import CommunicationScreeningAction
from communications.models.screening_rule import CommunicationScreeningMatchType
from communications.models.screening_rule import CommunicationScreeningRule
from communications.models.screening_rule import CommunicationScreeningSeverity
from communications.constants import CommunicationMessageType
from communications.constants import CommunicationParticipantRole

CommRole = CommunicationParticipantRole
MessageType = CommunicationMessageType
MessageType.TEXT = CommunicationMessageType.USER

__all__ = [
    "CommRole",
    "CommunicationAttachment",
    "CommunicationAuditLog",
    "CommunicationMessage",
    "CommunicationModerationFlag",
    "CommunicationParticipant",
    "CommunicationReadReceipt",
    "CommunicationThread",
    "CommunicationMessageEdit",
    "CommunicationThreadPolicy",
    "CommunicationThreadSLA",
    "CommunicationThreadAssignment",
    "CommunicationAuditAction",
    "CommunicationEscalation",
    "CommunicationEscalationStatus",
    "CommunicationModerationSeverity",
    "CommunicationModerationStatus",
    "CommunicationSavedReply",
    "CommunicationThreadTag",
    "CommunicationThreadTagAssignment",
    "CommunicationLinkReview",
    "CommunicationLinkReviewStatus",
    "CommunicationScreeningAction",
    "CommunicationScreeningMatchType",
    "CommunicationScreeningRule",
    "CommunicationScreeningSeverity",
    "MessageType",
]
