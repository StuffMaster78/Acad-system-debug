from __future__ import annotations

from urllib.parse import urlparse

from django.db import transaction
from django.utils import timezone

from files_management.enums import (
    ExternalFileProvider,
    ExternalFileReviewStatus,
)
from files_management.exceptions import ExternalFileLinkError
from files_management.models import ExternalFileLink
from files_management.services.file_policy_service import FilePolicyService


class ExternalFileLinkService:
    """
    Handles external file link submission and staff review.

    External links are useful for Google Docs, Google Slides, Google
    Sheets, Drive folders, Dropbox folders, Loom videos, and other large
    files that should not be uploaded directly.

    Because links can be unsafe, broken, private, or misleading, normal
    user submitted links should usually require staff review before
    other users can rely on them.
    """

    @classmethod
    @transaction.atomic
    def submit_link(
        cls,
        *,
        website,
        submitted_by,
        url: str,
        purpose: str,
        title: str = "",
        provider: str = "",
        metadata: dict | None = None,
    ) -> ExternalFileLink:
        """
        Submit an external link for a given file purpose.
        """

        if not FilePolicyService.allows_external_links(
            website=website,
            purpose=purpose,
        ):
            raise ExternalFileLinkError(
                "External links are not allowed for this file purpose."
            )

        normalized_url = cls.validate_url(url=url)
        detected_provider = provider or cls.detect_provider(
            url=normalized_url,
        )

        review_status = ExternalFileReviewStatus.PENDING

        if not FilePolicyService.external_links_require_review(
            website=website,
            purpose=purpose,
        ):
            review_status = ExternalFileReviewStatus.APPROVED

        return ExternalFileLink.objects.create(
            website=website,
            submitted_by=submitted_by,
            provider=detected_provider,
            title=title,
            url=normalized_url,
            review_status=review_status,
            metadata=metadata or {},
        )

    @classmethod
    @transaction.atomic
    def approve_link(
        cls,
        *,
        external_link: ExternalFileLink,
        reviewed_by,
        review_note: str = "",
    ) -> ExternalFileLink:
        """
        Approve an external link after staff review.
        """

        external_link.review_status = ExternalFileReviewStatus.APPROVED
        external_link.reviewed_by = reviewed_by
        external_link.reviewed_at = timezone.now()
        external_link.review_note = review_note
        external_link.is_active = True
        external_link.full_clean()
        external_link.save(
            update_fields=[
                "review_status",
                "reviewed_by",
                "reviewed_at",
                "review_note",
                "is_active",
                "updated_at",
            ]
        )

        return external_link

    @classmethod
    @transaction.atomic
    def reject_link(
        cls,
        *,
        external_link: ExternalFileLink,
        reviewed_by,
        review_note: str,
    ) -> ExternalFileLink:
        """
        Reject an external link after staff review.
        """

        external_link.review_status = ExternalFileReviewStatus.REJECTED
        external_link.reviewed_by = reviewed_by
        external_link.reviewed_at = timezone.now()
        external_link.review_note = review_note
        external_link.is_active = False
        external_link.full_clean()
        external_link.save(
            update_fields=[
                "review_status",
                "reviewed_by",
                "reviewed_at",
                "review_note",
                "is_active",
                "updated_at",
            ]
        )

        return external_link

    @classmethod
    @transaction.atomic
    def expire_link(
        cls,
        *,
        external_link: ExternalFileLink,
        reviewed_by=None,
        review_note: str = "",
    ) -> ExternalFileLink:
        """
        Mark an external link as expired or no longer usable.
        """

        external_link.review_status = ExternalFileReviewStatus.EXPIRED
        external_link.reviewed_by = reviewed_by
        external_link.reviewed_at = timezone.now()
        external_link.review_note = review_note
        external_link.is_active = False
        external_link.full_clean()
        external_link.save(
            update_fields=[
                "review_status",
                "reviewed_by",
                "reviewed_at",
                "review_note",
                "is_active",
                "updated_at",
            ]
        )

        return external_link

    @staticmethod
    def validate_url(*, url: str) -> str:
        """
        Validate and normalize a URL string.
        """

        normalized_url = url.strip()

        if not normalized_url:
            raise ExternalFileLinkError("External link URL is required.")

        parsed = urlparse(normalized_url)

        if parsed.scheme not in {"http", "https"}:
            raise ExternalFileLinkError(
                "External link must use HTTP or HTTPS."
            )

        if not parsed.netloc:
            raise ExternalFileLinkError("External link host is required.")

        return normalized_url

    @staticmethod
    def detect_provider(*, url: str) -> str:
        """
        Detect the likely external provider from a URL.
        """

        host = urlparse(url).netloc.lower()

        if "docs.google.com" in host:
            if "/presentation/" in url:
                return ExternalFileProvider.GOOGLE_SLIDES
            if "/spreadsheets/" in url:
                return ExternalFileProvider.GOOGLE_SHEETS
            if "/document/" in url:
                return ExternalFileProvider.GOOGLE_DOCS

            return ExternalFileProvider.GOOGLE_DRIVE

        if "drive.google.com" in host:
            return ExternalFileProvider.GOOGLE_DRIVE

        if "dropbox.com" in host:
            return ExternalFileProvider.DROPBOX

        if "onedrive.live.com" in host or "1drv.ms" in host:
            return ExternalFileProvider.ONE_DRIVE

        if "youtube.com" in host or "youtu.be" in host:
            return ExternalFileProvider.YOUTUBE

        if "vimeo.com" in host:
            return ExternalFileProvider.VIMEO

        if "loom.com" in host:
            return ExternalFileProvider.LOOM

        return ExternalFileProvider.OTHER