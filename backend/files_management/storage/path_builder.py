from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from django.utils import timezone
from django.utils.text import slugify

from files_management.constants import FILE_UPLOAD_PATH_PREFIX


class FileStoragePathBuilder:
    """
    Builds tenant-aware storage paths for uploaded files.

    Storage keys should avoid user-controlled raw filenames. A readable
    slug is kept for support visibility, but uniqueness comes from UUIDs.
    """

    @staticmethod
    def build_key(
        *,
        website_id: int,
        original_name: str,
        purpose: str,
    ) -> str:
        """
        Build a stable storage key for a managed file.
        """

        now = timezone.now()
        extension = Path(original_name).suffix.lower()
        stem = Path(original_name).stem
        safe_stem = slugify(stem)[:80] or "file"
        unique_id = uuid4().hex

        return (
            f"{FILE_UPLOAD_PATH_PREFIX}/"
            f"website-{website_id}/"
            f"{purpose}/"
            f"{now:%Y/%m/%d}/"
            f"{safe_stem}-{unique_id}{extension}"
        )