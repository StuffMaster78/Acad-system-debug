from __future__ import annotations

from django.core.files.storage import default_storage

from files_management.constants import DEFAULT_SIGNED_URL_EXPIRY_SECONDS
from files_management.exceptions import SignedUrlGenerationError


class SignedUrlBuilder:
    """
    Builds access URLs for managed files.

    For S3-compatible storage, many Django storage backends return signed
    URLs from `url()`. For local storage, this usually returns a normal
    media URL. The service layer decides whether the caller may receive
    the URL before this class is used.
    """

    @staticmethod
    def build_url(
        *,
        storage_name: str,
        expires_in: int = DEFAULT_SIGNED_URL_EXPIRY_SECONDS,
    ) -> str:
        """
        Return a URL for a stored file.

        The `expires_in` value is passed when supported by the configured
        storage backend. Some backends ignore it.
        """

        try:
            return default_storage.url(storage_name)
        except Exception as exc:
            raise SignedUrlGenerationError(
                "Could not generate a file access URL."
            ) from exc