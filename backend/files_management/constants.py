"""
Constants for the files_management app.

This module contains stable string values used across models, services,
selectors, policies, and APIs. Keeping them here prevents magic strings
from leaking across the codebase.
"""

DEFAULT_SIGNED_URL_EXPIRY_SECONDS = 900
DEFAULT_MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024
DEFAULT_IMAGE_MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024
DEFAULT_VIDEO_MAX_FILE_SIZE_BYTES = 250 * 1024 * 1024

FILE_UPLOAD_PATH_PREFIX = "managed-files"

PUBLIC_FILE_CACHE_SECONDS = 60 * 60 * 24 * 30
PRIVATE_FILE_CACHE_SECONDS = 60

SYSTEM_ACTOR_LABEL = "system"

ALLOWED_IMAGE_MIME_TYPES = (
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
)

ALLOWED_DOCUMENT_MIME_TYPES = (
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "text/plain",
    "text/csv",
)

ALLOWED_VIDEO_MIME_TYPES = (
    "video/mp4",
    "video/webm",
    "video/quicktime",
)

ALLOWED_AUDIO_MIME_TYPES = (
    "audio/mpeg",
    "audio/mp4",
    "audio/wav",
    "audio/webm",
    "audio/ogg",
)

ALLOWED_ARCHIVE_MIME_TYPES = (
    "application/zip",
    "application/x-zip-compressed",
    "application/x-rar-compressed",
    "application/x-7z-compressed",
)

ALLOWED_FILE_MIME_TYPES = (
    *ALLOWED_IMAGE_MIME_TYPES,
    *ALLOWED_DOCUMENT_MIME_TYPES,
    *ALLOWED_VIDEO_MIME_TYPES,
    *ALLOWED_AUDIO_MIME_TYPES,
    *ALLOWED_ARCHIVE_MIME_TYPES,
)

ALLOWED_DOCUMENT_EXTENSIONS = (
    ".pdf",
    ".doc",
    ".docx",
    ".odt",
    ".rtf",
    ".txt",
    ".csv",
    ".xls",
    ".xlsx",
    ".ods",
    ".ppt",
    ".pptx",
    ".odp",
)

ALLOWED_IMAGE_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".gif",
)

ALLOWED_VIDEO_EXTENSIONS = (
    ".mp4",
    ".webm",
    ".mov",
)

ALLOWED_AUDIO_EXTENSIONS = (
    ".mp3",
    ".m4a",
    ".wav",
    ".ogg",
    ".webm",
)

ALLOWED_ARCHIVE_EXTENSIONS = (
    ".zip",
    ".rar",
    ".7z",
)

ALLOWED_FILE_EXTENSIONS = (
    *ALLOWED_DOCUMENT_EXTENSIONS,
    *ALLOWED_IMAGE_EXTENSIONS,
    *ALLOWED_VIDEO_EXTENSIONS,
    *ALLOWED_AUDIO_EXTENSIONS,
    *ALLOWED_ARCHIVE_EXTENSIONS,
)