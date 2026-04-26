from __future__ import annotations

import mimetypes
from pathlib import Path

from django.core.files.uploadedfile import UploadedFile

from files_management.enums import FileKind


class MimeTypeDetector:
    """
    Detects MIME type and broad file kind.

    This detector uses Django upload metadata and Python's MIME guesses.
    In production, deeper content inspection can be added through scan
    services without changing upload service contracts.
    """

    IMAGE_PREFIX = "image/"
    VIDEO_PREFIX = "video/"
    AUDIO_PREFIX = "audio/"

    DOCUMENT_MIME_TYPES = {
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml."
        "document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml."
        "sheet",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml."
        "presentation",
        "text/plain",
        "text/csv",
    }

    ARCHIVE_MIME_TYPES = {
        "application/zip",
        "application/x-zip-compressed",
        "application/x-rar-compressed",
        "application/x-7z-compressed",
    }

    @classmethod
    def detect_mime_type(cls, *, uploaded_file: UploadedFile) -> str:
        """
        Return the best available MIME type for an uploaded file.
        """

        if uploaded_file.content_type:
            return uploaded_file.content_type

        guessed_type, _encoding = mimetypes.guess_type(uploaded_file.name)

        if guessed_type:
            return guessed_type

        return "application/octet-stream"

    @classmethod
    def detect_extension(cls, *, filename: str) -> str:
        """
        Return the lowercase file extension, including the leading dot.
        """

        return Path(filename).suffix.lower()

    @classmethod
    def detect_kind(cls, *, mime_type: str, filename: str = "") -> str:
        """
        Return the broad file kind for a MIME type and filename.
        """

        extension = cls.detect_extension(filename=filename)

        if mime_type.startswith(cls.IMAGE_PREFIX):
            return FileKind.IMAGE

        if mime_type.startswith(cls.VIDEO_PREFIX):
            return FileKind.VIDEO

        if mime_type.startswith(cls.AUDIO_PREFIX):
            return FileKind.AUDIO

        if mime_type in cls.DOCUMENT_MIME_TYPES:
            return FileKind.DOCUMENT

        if mime_type in cls.ARCHIVE_MIME_TYPES:
            return FileKind.ARCHIVE

        if extension in {".doc", ".docx", ".pdf", ".ppt", ".pptx"}:
            return FileKind.DOCUMENT

        if extension in {".xls", ".xlsx", ".csv", ".txt", ".rtf"}:
            return FileKind.DOCUMENT

        if extension in {".zip", ".rar", ".7z"}:
            return FileKind.ARCHIVE

        return FileKind.OTHER