from __future__ import annotations

from pathlib import Path

from django.core.files.uploadedfile import UploadedFile

from files_management.constants import (
    ALLOWED_FILE_EXTENSIONS,
    ALLOWED_FILE_MIME_TYPES,
    DEFAULT_MAX_FILE_SIZE_BYTES,
)
from files_management.exceptions import FileValidationError
from files_management.models import FilePolicy
from files_management.selectors import FilePolicySelector
from files_management.storage import MimeTypeDetector


class FilePolicyService:
    """
    Enforces tenant and purpose based file rules.

    This service keeps upload validation flexible. Platform defaults
    provide safe baseline rules, while FilePolicy records allow each
    website to override accepted MIME types, extensions, size limits,
    and external link behavior per file purpose.
    """

    @classmethod
    def get_policy(
        cls,
        *,
        website,
        purpose: str,
    ) -> FilePolicy | None:
        """
        Return the active policy for a website and file purpose.
        """

        return FilePolicySelector.by_purpose(
            website=website,
            purpose=purpose,
        )

    @classmethod
    def get_allowed_mime_types(
        cls,
        *,
        website,
        purpose: str,
    ) -> list[str]:
        """
        Return MIME types allowed for a website and purpose.
        """

        policy = cls.get_policy(
            website=website,
            purpose=purpose,
        )

        if policy:
            return policy.get_allowed_mime_types()

        return list(ALLOWED_FILE_MIME_TYPES)

    @classmethod
    def get_allowed_extensions(
        cls,
        *,
        website,
        purpose: str,
    ) -> list[str]:
        """
        Return file extensions allowed for a website and purpose.
        """

        policy = cls.get_policy(
            website=website,
            purpose=purpose,
        )

        if policy:
            return policy.get_allowed_extensions()

        return list(ALLOWED_FILE_EXTENSIONS)

    @classmethod
    def get_max_file_size_bytes(
        cls,
        *,
        website,
        purpose: str,
    ) -> int:
        """
        Return maximum file size allowed for a website and purpose.
        """

        policy = cls.get_policy(
            website=website,
            purpose=purpose,
        )

        if policy:
            return int(policy.max_file_size_bytes)

        return DEFAULT_MAX_FILE_SIZE_BYTES

    @classmethod
    def validate_uploaded_file(
        cls,
        *,
        website,
        purpose: str,
        uploaded_file: UploadedFile,
    ) -> str:
        """
        Validate an uploaded file against tenant policy.

        Returns the detected MIME type when validation passes.
        """

        mime_type = MimeTypeDetector.detect_mime_type(
            uploaded_file=uploaded_file,
        )
        extension = Path(uploaded_file.name).suffix.lower()

        cls.validate_size(
            uploaded_file=uploaded_file,
            max_size_bytes=cls.get_max_file_size_bytes(
                website=website,
                purpose=purpose,
            ),
        )
        cls.validate_extension(
            extension=extension,
            allowed_extensions=cls.get_allowed_extensions(
                website=website,
                purpose=purpose,
            ),
        )
        cls.validate_mime_type(
            mime_type=mime_type,
            allowed_mime_types=cls.get_allowed_mime_types(
                website=website,
                purpose=purpose,
            ),
        )

        return mime_type

    @staticmethod
    def validate_size(
        *,
        uploaded_file: UploadedFile,
        max_size_bytes: int,
    ) -> None:
        """
        Validate uploaded file size.
        """

        if uploaded_file.size > max_size_bytes:
            raise FileValidationError(
                "Uploaded file exceeds the allowed size limit."
            )

    @staticmethod
    def validate_extension(
        *,
        extension: str,
        allowed_extensions: list[str],
    ) -> None:
        """
        Validate uploaded file extension.
        """

        normalized = extension.lower()

        if normalized not in allowed_extensions:
            raise FileValidationError(
                "Uploaded file extension is not allowed."
            )

    @staticmethod
    def validate_mime_type(
        *,
        mime_type: str,
        allowed_mime_types: list[str],
    ) -> None:
        """
        Validate uploaded file MIME type.
        """

        if mime_type not in allowed_mime_types:
            raise FileValidationError(
                "Uploaded file MIME type is not allowed."
            )

    @classmethod
    def allows_external_links(
        cls,
        *,
        website,
        purpose: str,
    ) -> bool:
        """
        Return whether external links are allowed for a purpose.
        """

        policy = cls.get_policy(
            website=website,
            purpose=purpose,
        )

        if not policy:
            return False

        return bool(policy.allow_external_links)

    @classmethod
    def external_links_require_review(
        cls,
        *,
        website,
        purpose: str,
    ) -> bool:
        """
        Return whether external links require staff review.
        """

        policy = cls.get_policy(
            website=website,
            purpose=purpose,
        )

        if not policy:
            return True

        return bool(policy.external_links_require_review)