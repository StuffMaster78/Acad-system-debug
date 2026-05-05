from __future__ import annotations

from urllib.parse import urlparse

from django.db import transaction
from django.utils import timezone

from communications.constants import CommunicationMessageStatus
from communications.models.audit import CommunicationAuditAction
from communications.models.link_review import (
    CommunicationLinkReview,
    CommunicationLinkReviewStatus,
)

from communications.services.audit_service import CommunicationAuditService


class CommunicationLinkReviewService:
    """
    Manage links extracted from communication messages.
    """

    @staticmethod
    def extract_domain(*, url: str) -> str:
        """
        Extract the domain from a URL.
        """
        normalized_url = url

        if normalized_url.startswith("www."):
            normalized_url = f"https://{normalized_url}"

        parsed = urlparse(normalized_url)
        return parsed.netloc.lower()

    @staticmethod
    @transaction.atomic
    def create_review(
        *,
        message,
        url: str,
        submitted_by=None,
        metadata: dict | None = None,
    ) -> CommunicationLinkReview:
        """
        Create a pending link review record.
        """
        review = CommunicationLinkReview.objects.create(
            website=message.website,
            thread=message.thread,
            message=message,
            url=url,
            domain=CommunicationLinkReviewService.extract_domain(url=url),
            submitted_by=submitted_by,
            metadata=metadata or {},
        )

        CommunicationAuditService.log(
            website=message.website,
            thread=message.thread,
            message=message,
            actor=submitted_by,
            action=CommunicationAuditAction.LINK_REVIEW_CREATED,
            details={
                "link_review_id": review.pk,
                "url": url,
                "domain": review.domain,
                "status": review.status,
            },
        )

        return review

    @staticmethod
    @transaction.atomic
    def approve(
        *,
        review,
        reviewed_by,
        decision_note: str = "",
    ) -> CommunicationLinkReview:
        """
        Approve a link review.
        """
        review.status = CommunicationLinkReviewStatus.APPROVED
        review.reviewed_by = reviewed_by
        review.reviewed_at = timezone.now()
        review.decision_note = decision_note
        review.save(
            update_fields=[
                "status",
                "reviewed_by",
                "reviewed_at",
                "decision_note",
                "updated_at",
            ],
        )

        message = review.message

        if message.status == CommunicationMessageStatus.HELD_FOR_REVIEW:
            message.status = CommunicationMessageStatus.ACTIVE
            message.save(update_fields=["status", "updated_at"])

        CommunicationAuditService.log(
            website=review.website,
            thread=review.thread,
            message=message,
            actor=reviewed_by,
            action=CommunicationAuditAction.LINK_REVIEW_APPROVED,
            details={
                "link_review_id": review.id,
                "status": review.status,
                "decision_note": decision_note,
            },
        )

        return review

    @staticmethod
    @transaction.atomic
    def reject(
        *,
        review,
        reviewed_by,
        decision_note: str = "",
    ) -> CommunicationLinkReview:
        """
        Reject a link review and hide the message.
        """
        review.status = CommunicationLinkReviewStatus.REJECTED
        review.reviewed_by = reviewed_by
        review.reviewed_at = timezone.now()
        review.decision_note = decision_note
        review.save(
            update_fields=[
                "status",
                "reviewed_by",
                "reviewed_at",
                "decision_note",
                "updated_at",
            ],
        )

        message = review.message
        message.status = CommunicationMessageStatus.HIDDEN
        message.hidden_at = timezone.now()
        message.save(update_fields=["status", "hidden_at", "updated_at"])

        CommunicationAuditService.log(
            website=review.website,
            thread=review.thread,
            message=message,
            actor=reviewed_by,
            action=CommunicationAuditAction.LINK_REVIEW_REJECTED,
            details={
                "link_review_id": review.id,
                "status": review.status,
                "decision_note": decision_note,
            },
        )

        return review

    @staticmethod
    @transaction.atomic
    def block(
        *,
        review,
        reviewed_by,
        decision_note: str = "",
    ) -> CommunicationLinkReview:
        """
        Block a link review and hold the message from normal visibility.
        """
        review.status = CommunicationLinkReviewStatus.BLOCKED
        review.reviewed_by = reviewed_by
        review.reviewed_at = timezone.now()
        review.decision_note = decision_note
        review.save(
            update_fields=[
                "status",
                "reviewed_by",
                "reviewed_at",
                "decision_note",
                "updated_at",
            ],
        )

        message = review.message
        message.status = CommunicationMessageStatus.WITHDRAWN
        message.withdrawn_at = timezone.now()
        message.metadata = {
            **message.metadata,
            "blocked_link_review_id": review.id,
        }
        message.save(
            update_fields=[
                "status",
                "withdrawn_at",
                "metadata",
                "updated_at",
            ],
        )

        CommunicationAuditService.log(
            website=review.website,
            thread=review.thread,
            message=message,
            actor=reviewed_by,
            action=CommunicationAuditAction.LINK_REVIEW_BLOCKED,
            details={
                "link_review_id": review.id,
                "status": review.status,
                "decision_note": decision_note,
            },
        )

        return review