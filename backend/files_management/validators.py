"""
Validation utilities for files_management.

Validators in this module stay framework friendly and side effect free.
They should not create database records, call external services, or make
access control decisions.
"""

from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Iterable

from django.core.files.uploadedfile import UploadedFile
from django.utils.text import get_valid_filename

from files_management.constants import (
    ALLOWED_FILE_MIME_TYPES,
    DEFAULT_MAX_FILE_SIZE_BYTES,
)
from files_management.exceptions import FileValidationError


def normalize_filename(filename: str) -> str:
    """
    Return a safe filename suitable for storage metadata.

    The returned value is not intended to be the final storage key. It is
    only a cleaned display filename that preserves a human readable name.
    """

    cleaned = get_valid_filename(filename.strip())

    if not cleaned:
        raise FileValidationError("Filename cannot be empty.")

    return cleaned


def get_file_extension(filename: str) -> str:
    """
    Return the lowercase extension for a filename.

    The returned value includes the leading dot, for example `.pdf`.
    """

    return Path(filename).suffix.lower()


def guess_mime_type(filename: str) -> str:
    """
    Guess the MIME type for a filename.

    This helper is intentionally conservative. Actual uploaded file
    content should still be inspected by a storage or scanning layer in
    production when stricter verification is required.
    """

    mime_type, _encoding = mimetypes.guess_type(filename)

    if not mime_type:
        return "application/octet-stream"

    return mime_type


def validate_file_size(
    uploaded_file: UploadedFile,
    *,
    max_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES,
) -> None:
    """
    Validate that an uploaded file does not exceed the configured limit.
    """

    if uploaded_file.size > max_size_bytes:
        raise FileValidationError(
            "Uploaded file exceeds the maximum allowed size."
        )


def validate_mime_type(
    mime_type: str,
    *,
    allowed_mime_types: Iterable[str] = ALLOWED_FILE_MIME_TYPES,
) -> None:
    """
    Validate that a MIME type is allowed by platform policy.
    """

    allowed_values = set(allowed_mime_types)

    if mime_type not in allowed_values:
        raise FileValidationError("Uploaded file type is not allowed.")


def validate_uploaded_file(
    uploaded_file: UploadedFile,
    *,
    max_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES,
    allowed_mime_types: Iterable[str] = ALLOWED_FILE_MIME_TYPES,
) -> str:
    """
    Validate an uploaded file and return its normalized filename.

    This function performs the common validation path used by upload
    services. It validates filename, size, and MIME type using the best
    information available from Django's UploadedFile object.
    """

    normalized_name = normalize_filename(uploaded_file.name)
    detected_mime_type = uploaded_file.content_type

    if not detected_mime_type:
        detected_mime_type = guess_mime_type(normalized_name)

    validate_file_size(uploaded_file, max_size_bytes=max_size_bytes)
    validate_mime_type(
        detected_mime_type,
        allowed_mime_types=allowed_mime_types,
    )

    return normalized_name