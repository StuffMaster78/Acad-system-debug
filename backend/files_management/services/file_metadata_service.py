from __future__ import annotations

from typing import Any

from django.db import transaction

from files_management.models.managed_file import ManagedFile


class FileMetadataService:
    """
    Handles safe metadata updates for managed files.

    Metadata is flexible JSON used by domain apps for context such as
    CMS image details, order delivery notes, attachment labels, external
    processing status, and frontend display hints.

    This service centralizes metadata mutation so apps do not directly
    manipulate ManagedFile.metadata in scattered places.
    """

    @staticmethod
    def get_metadata(
        *,
        managed_file: ManagedFile,
    ) -> dict[str, Any]:
        """
        Return a safe metadata dictionary for a managed file.
        """

        metadata = managed_file.metadata or {}

        if not isinstance(metadata, dict):
            return {}

        return dict(metadata)

    @classmethod
    @transaction.atomic
    def replace_metadata(
        cls,
        *,
        managed_file: ManagedFile,
        metadata: dict[str, Any],
    ) -> ManagedFile:
        """
        Replace all metadata on a managed file.
        """

        managed_file.metadata = dict(metadata)
        managed_file.full_clean()
        managed_file.save(
            update_fields=[
                "metadata",
                "updated_at",
            ]
        )
        return managed_file

    @classmethod
    @transaction.atomic
    def update_metadata(
        cls,
        *,
        managed_file: ManagedFile,
        updates: dict[str, Any],
    ) -> ManagedFile:
        """
        Merge new metadata values into existing metadata.
        """

        metadata = cls.get_metadata(managed_file=managed_file)
        metadata.update(updates)

        managed_file.metadata = metadata
        managed_file.full_clean()
        managed_file.save(
            update_fields=[
                "metadata",
                "updated_at",
            ]
        )
        return managed_file

    @classmethod
    @transaction.atomic
    def remove_metadata_keys(
        cls,
        *,
        managed_file: ManagedFile,
        keys: list[str],
    ) -> ManagedFile:
        """
        Remove selected metadata keys from a managed file.
        """

        metadata = cls.get_metadata(managed_file=managed_file)

        for key in keys:
            metadata.pop(key, None)

        managed_file.metadata = metadata
        managed_file.full_clean()
        managed_file.save(
            update_fields=[
                "metadata",
                "updated_at",
            ]
        )
        return managed_file

    @classmethod
    def get_value(
        cls,
        *,
        managed_file: ManagedFile,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Return one metadata value by key.
        """

        metadata = cls.get_metadata(managed_file=managed_file)
        return metadata.get(key, default)

    @classmethod
    def has_key(
        cls,
        *,
        managed_file: ManagedFile,
        key: str,
    ) -> bool:
        """
        Return whether metadata contains a key.
        """

        metadata = cls.get_metadata(managed_file=managed_file)
        return key in metadata

    @classmethod
    @transaction.atomic
    def set_alt_text(
        cls,
        *,
        managed_file: ManagedFile,
        alt_text: str,
    ) -> ManagedFile:
        """
        Store CMS/image alt text in metadata.
        """

        return cls.update_metadata(
            managed_file=managed_file,
            updates={
                "alt_text": alt_text.strip(),
            },
        )

    @classmethod
    def get_alt_text(
        cls,
        *,
        managed_file: ManagedFile,
    ) -> str:
        """
        Return image alt text from metadata.
        """

        value = cls.get_value(
            managed_file=managed_file,
            key="alt_text",
            default="",
        )
        return str(value or "")

    @classmethod
    @transaction.atomic
    def set_cms_metadata(
        cls,
        *,
        managed_file: ManagedFile,
        title: str = "",
        alt_text: str = "",
        caption: str = "",
        credit: str = "",
        source_url: str = "",
    ) -> ManagedFile:
        """
        Store common CMS media metadata.
        """

        updates = {
            "title": title.strip(),
            "alt_text": alt_text.strip(),
            "caption": caption.strip(),
            "credit": credit.strip(),
            "source_url": source_url.strip(),
        }

        return cls.update_metadata(
            managed_file=managed_file,
            updates=updates,
        )

    @classmethod
    def get_cms_metadata(
        cls,
        *,
        managed_file: ManagedFile,
    ) -> dict[str, str]:
        """
        Return normalized CMS media metadata.
        """

        metadata = cls.get_metadata(managed_file=managed_file)

        return {
            "title": str(metadata.get("title") or ""),
            "alt_text": str(metadata.get("alt_text") or ""),
            "caption": str(metadata.get("caption") or ""),
            "credit": str(metadata.get("credit") or ""),
            "source_url": str(metadata.get("source_url") or ""),
        }

    @classmethod
    @transaction.atomic
    def set_processing_metadata(
        cls,
        *,
        managed_file: ManagedFile,
        processor: str,
        status: str,
        details: dict[str, Any] | None = None,
    ) -> ManagedFile:
        """
        Store processing status for scans, derivatives, OCR, previews, or
        future AI/media processing jobs.
        """

        metadata = cls.get_metadata(managed_file=managed_file)
        processing = metadata.get("processing")

        if not isinstance(processing, dict):
            processing = {}

        processing[processor] = {
            "status": status,
            "details": details or {},
        }

        metadata["processing"] = processing

        return cls.replace_metadata(
            managed_file=managed_file,
            metadata=metadata,
        )

    @classmethod
    def get_processing_metadata(
        cls,
        *,
        managed_file: ManagedFile,
        processor: str,
    ) -> dict[str, Any]:
        """
        Return processing metadata for one processor.
        """

        metadata = cls.get_metadata(managed_file=managed_file)
        processing = metadata.get("processing")

        if not isinstance(processing, dict):
            return {}

        value = processing.get(processor)

        if not isinstance(value, dict):
            return {}

        return dict(value)